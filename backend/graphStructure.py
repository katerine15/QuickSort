import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Directorios y archivos que no se deben copiar en operaciones de backup/copia
IGNORED_DIRECTORIES = {
    "node_modules",
    "venv",
    ".venv",
    "env",
    ".env",
    "__pycache__",
    "build",
    "dist",
    "docker",
    ".docker",
    ".github",
    ".gitlab",
    ".next",
    ".nuxt",
    "target",
    ".idea",
    ".vscode",
    ".git",
}
IGNORED_FILES = {".DS_Store"}


class Graph:
    def __init__(self):
        self.adj = {}  # Diccionario para listas de adyacencia

    def add_node(self, node):
        if node not in self.adj:
            self.adj[node] = []

    def add_edge(self, u, v):
        # Aseguramos que existan los nodos
        self.add_node(u)
        self.add_node(v)
        # Grafo no dirigido: agregamos en ambos sentidos
        if v not in self.adj[u]:
            self.adj[u].append(v)
        if u not in self.adj[v]:
            self.adj[v].append(u)

    def show(self):
        for node, neighbors in self.adj.items():
            print(f"{node} -> {neighbors}")

    def bfs(self, start):
        visited = set()
        queue = [start]
        visited.add(start)

        while queue:
            current = queue.pop(0)
            print(current, end=" ")

            for neighbor in self.adj[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

    def dfs(self, start, visited=None):
        if visited is None:
            visited = set()

        print(start, end=" ")
        visited.add(start)

        for neighbor in self.adj[start]:
            if neighbor not in visited:
                self.dfs(neighbor, visited)


def _normalize_keywords(folder_name: str) -> Set[str]:
    """Normaliza y extrae palabras clave del nombre de una carpeta."""
    cleaned = re.sub(r"[^\w\s-]", " ", folder_name.lower())
    return {part for part in re.split(r"[\s_-]+", cleaned) if part}


def _collect_folders_and_keywords(base_path: str) -> Tuple[List[str], Dict[str, Set[str]]]:
    """
    Recorre un proyecto y devuelve todas las carpetas con sus palabras clave,
    heredando el contexto del padre para capturar relaciones de proyecto.
    """
    folders: List[str] = []
    folder_keywords: Dict[str, Set[str]] = {}

    for root, dirs, _ in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
        folders.append(root)

        current_keywords = _normalize_keywords(Path(root).name)
        parent = str(Path(root).parent)
        if parent in folder_keywords:
            current_keywords |= folder_keywords[parent]

        folder_keywords[root] = current_keywords

    return folders, folder_keywords


def _build_graph_from_keywords(folders: List[str], folder_keywords: Dict[str, Set[str]]) -> Graph:
    """Construye un grafo conectando carpetas que comparten palabras clave."""
    graph = Graph()
    for folder in folders:
        graph.add_node(folder)

    for idx, folder in enumerate(folders):
        for other in folders[idx + 1 :]:
            shared = folder_keywords[folder] & folder_keywords[other]
            if shared:
                graph.add_edge(folder, other)

    return graph


def _plan_copy(source: Path, destination: Path) -> List[Dict[str, str]]:
    """
    Genera un plan de copia entre carpetas, omitiendo directorios pesados
    y devolviendo los pares origen/destino para confirmación.
    """
    plan: List[Dict[str, str]] = []

    for root, dirs, files in os.walk(source):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
        relative_root = Path(root).relative_to(source)
        destination_root = destination / relative_root

        for file in files:
            if file in IGNORED_FILES:
                continue

            src_file = Path(root) / file
            dst_file = destination_root / file
            plan.append(
                {
                    "source": str(src_file),
                    "destination": str(dst_file),
                }
            )

    return plan


def _execute_copy_plan(plan: List[Dict[str, str]]) -> Dict[str, List[str]]:
    """Ejecuta el plan de copia sin sobreescribir archivos existentes."""
    copied, skipped = [], []

    for item in plan:
        src = Path(item["source"])
        dst = Path(item["destination"])
        dst.parent.mkdir(parents=True, exist_ok=True)

        if dst.exists():
            skipped.append(str(dst))
            continue

        shutil.copy2(src, dst)
        copied.append(str(dst))

    return {"copied": copied, "skipped": skipped}


def _create_backup(source_folder: Path, backup_root: Path) -> str:
    """
    Crea un backup sin incluir dependencias pesadas (node_modules, venv, etc.).
    Devuelve la ruta del backup generado.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_root / f"{source_folder.name}_backup_{timestamp}"

    for root, dirs, files in os.walk(source_folder):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRECTORIES]
        relative_root = Path(root).relative_to(source_folder)
        destination_root = backup_path / relative_root
        destination_root.mkdir(parents=True, exist_ok=True)

        for file in files:
            if file in IGNORED_FILES:
                continue
            shutil.copy2(Path(root) / file, destination_root / file)

    return str(backup_path)


def connect_project_folders(
    base_path: str,
    current_folder: str,
    backup_dir: Optional[str] = None,
    copy_on_confirm: bool = False,
    create_backup: bool = False,
    preferred_related_folder: Optional[str] = None,
) -> Dict[str, object]:
    """
    Construye un grafo de carpetas de un proyecto de código usando palabras clave
    y prepara acciones de copia/backup evitando dependencias pesadas.

    Args:
        base_path: Carpeta raíz del proyecto a analizar.
        current_folder: Carpeta sobre la que se quiere actuar (nodo principal).
        backup_dir: Carpeta donde se almacenarán los respaldos. Si es None se usa base_path/_backups.
        copy_on_confirm: Si True ejecuta la copia desde la carpeta más relacionada hacia la actual.
        create_backup: Si True crea un backup de la carpeta actual omitiendo node_modules, venv, etc.

    Returns:
        Diccionario con el grafo generado, relaciones encontradas y resultado de las acciones.
        Este resultado puede usarse en frontend para desplegar un toast solicitando confirmación.
    """
    base_path = str(Path(base_path).resolve())
    current_folder = str(Path(current_folder).resolve())

    if not os.path.isdir(base_path):
        raise ValueError(f"La ruta base no existe: {base_path}")
    if not os.path.isdir(current_folder):
        raise ValueError(f"La carpeta actual no existe: {current_folder}")

    folders, folder_keywords = _collect_folders_and_keywords(base_path)
    graph = _build_graph_from_keywords(folders, folder_keywords)
    # Relaciones bidireccionales para todos los nodos encontrados en el recorrido
    relations_all = compute_keyword_relations(
        [{"name": Path(p).name, "path": p} for p in folders]
    )

    current_keywords = folder_keywords.get(current_folder, set())
    related = []
    for folder, keywords in folder_keywords.items():
        if folder == current_folder:
            continue
        shared = current_keywords & keywords
        if shared:
            related.append(
                {
                    "folder": folder,
                    "shared_keywords": sorted(shared),
                    "strength": len(shared),
                }
            )

    related.sort(key=lambda x: x["strength"], reverse=True)

    toast = None
    selected_relation = None
    if preferred_related_folder:
        selected_relation = next(
            (r for r in related if Path(r["folder"]).resolve() == Path(preferred_related_folder).resolve()),
            None,
        )

    if not selected_relation and related:
        selected_relation = related[0]

    if selected_relation:
        top = selected_relation
        toast = (
            f"Se detectó relación entre '{Path(current_folder).name}' y "
            f"'{Path(top['folder']).name}' (coinciden: {', '.join(top['shared_keywords'])}). "
            "¿Quieres copiar los archivos relacionados a la carpeta actual?"
        )

    copy_plan: List[Dict[str, str]] = []
    copy_result: Optional[Dict[str, List[str]]] = None

    if selected_relation:
        source_folder = Path(selected_relation["folder"])
        destination_folder = Path(current_folder)
        copy_plan = _plan_copy(source_folder, destination_folder)
        if copy_on_confirm:
            copy_result = _execute_copy_plan(copy_plan)

    backup_path = None
    if create_backup:
        backup_root = Path(backup_dir).resolve() if backup_dir else Path(base_path) / "_backups"
        backup_root.mkdir(parents=True, exist_ok=True)
        backup_path = _create_backup(Path(current_folder), backup_root)

    return {
        "graph": graph.adj,
        "related_folders": related,
        "toast": toast,
        "copy_plan": copy_plan,
        "copy_result": copy_result,
        "backup_path": backup_path,
        "selected_relation": selected_relation,
        "relations_bidirectional": relations_all,
    }


def compute_keyword_relations(nodes: List[Dict[str, str]]) -> Dict[str, List[Dict[str, object]]]:
    """
    Calcula relaciones entre nodos (carpetas) basadas en palabras clave en sus nombres.
    No toca el sistema de archivos; sólo usa los nombres/rutas que recibe.
    """
    relations: Dict[str, List[Dict[str, object]]] = {}

    # Preprocesar palabras clave de cada nodo
    keywords_by_node: Dict[str, Set[str]] = {}
    for node in nodes:
        node_path = node.get("path") or node.get("name") or ""
        node_name = node.get("name") or Path(node_path).name
        keywords_by_node[node_path] = _normalize_keywords(node_name)

    node_paths = list(keywords_by_node.keys())

    # Construir relaciones por intersección de palabras clave
    for idx, node_path in enumerate(node_paths):
        base_keywords = keywords_by_node[node_path]
        node_relations: List[Dict[str, object]] = []

        for other_path in node_paths[idx + 1 :]:
            shared = base_keywords & keywords_by_node[other_path]
            if shared:
                relation = {
                    "folder": other_path,
                    "shared_keywords": sorted(shared),
                    "strength": len(shared),
                }
                node_relations.append(relation)

                # Relación simétrica
                relations.setdefault(other_path, []).append(
                    {
                        "folder": node_path,
                        "shared_keywords": relation["shared_keywords"],
                        "strength": relation["strength"],
                    }
                )

        if node_relations:
            node_relations.sort(key=lambda x: x["strength"], reverse=True)
            relations.setdefault(node_path, []).extend(node_relations)

    # Ordenar todas las listas
    for node_path, rels in relations.items():
        rels.sort(key=lambda x: x["strength"], reverse=True)

    return relations
