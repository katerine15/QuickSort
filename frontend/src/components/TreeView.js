import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
} from '@mui/material';
import {
  FolderOpen,
  Add,
  Delete,
  Edit,
  ExpandMore,
  ChevronRight,
} from '@mui/icons-material';
import {
  getTree,
  getAllNodes,
  createNode,
  deleteNode,
  updateNode,
  getMonitorConfig,
  connectProjectFolders,
  getTreeRelations,
} from '../services/api';

const TreeView = () => {
  const [tree, setTree] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [monitorConfig, setMonitorConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [graphToast, setGraphToast] = useState(null);
  const [graphRelated, setGraphRelated] = useState([]);
  const [relations, setRelations] = useState({});
  const [actionMessage, setActionMessage] = useState(null);
  const [actionError, setActionError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [selectedRelation, setSelectedRelation] = useState({});
  const [openDialog, setOpenDialog] = useState(false);
  const [editDialog, setEditDialog] = useState(false);
  const [newNodeData, setNewNodeData] = useState({
    name: '',
    path: '',
    parent_id: null,
    node_type: 'folder',
  });
  const [editNodeData, setEditNodeData] = useState({
    id: null,
    name: '',
    path: '',
    parent_id: null,
    node_type: 'folder',
  });
  const [expandedNodes, setExpandedNodes] = useState(new Set());
  const getDisplayName = (node) => {
    if (!node) return '';
    return node.name === "Root" ? 'Organized (carpeta raiz)' : node.name;
  };

  useEffect(() => {
    loadTree();
    loadMonitorConfig();
  }, []);

  const loadTree = async () => {
    try {
      setLoading(true);
      const [treeResponse, nodesResponse, relationsResponse] = await Promise.all([
        getTree(),
        getAllNodes(),
        getTreeRelations(),
      ]);

      if (treeResponse.success) {
        setTree(treeResponse.tree);
      }

      if (nodesResponse.success) {
        let dbNodes = nodesResponse.nodes || [];
        // Incluir nodo raíz virtual si no existe en la lista proveniente de la BD
        if (treeResponse.success && treeResponse.tree?.root) {
          const rootNode = treeResponse.tree.root;
          const existsRoot = dbNodes.some((n) => n.path === rootNode.path);
          if (!existsRoot) {
            dbNodes = [
              {
                ...rootNode,
                id: rootNode.id || 'root-virtual',
                parent_id: null,
                is_virtual_root: true,
              },
              ...dbNodes,
            ];
          }
        }
        setNodes(dbNodes);
      }

      if (relationsResponse.success) {
        setRelations(relationsResponse.relations || {});
      }

      setError(null);
    } catch (err) {
      setError('Error cargando el árbol: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadMonitorConfig = async () => {
    try {
      const response = await getMonitorConfig();
      if (response.success) {
        setMonitorConfig(response.config);
      }
    } catch (err) {
      console.error('Error cargando configuración del monitor:', err);
    }
  };

  const handleOpenDialog = () => {
    // Auto-completar la ruta basándose en la configuración del monitor
    if (monitorConfig && monitorConfig.watch_folder) {
      const basePath = monitorConfig.watch_folder;
      setNewNodeData({
        name: '',
        path: basePath + '/Organized/',
        parent_id: null,
        node_type: 'folder',
      });
    } else {
      setNewNodeData({
        name: '',
        path: '',
        parent_id: null,
        node_type: 'folder',
      });
    }
    setOpenDialog(true);
  };

  const handleNodeNameChange = (name) => {
    // Actualizar el path automáticamente cuando cambia el nombre
    if (monitorConfig && monitorConfig.watch_folder) {
      const basePath = monitorConfig.watch_folder;
      const newPath = `${basePath}/Organized/${name}`;
      setNewNodeData({
        ...newNodeData,
        name: name,
        path: newPath,
      });
    } else {
      setNewNodeData({
        ...newNodeData,
        name: name,
      });
    }
  };

  const handleCreateNode = async () => {
    try {
      // Derivar base para grafo: carpeta a monitorear o carpeta padre
      const parentPath = newNodeData.parent_id
        ? nodes.find((n) => n.id === newNodeData.parent_id)?.path
        : null;
      const graphBasePath =
        monitorConfig?.watch_folder ||
        (parentPath && parentPath.split('/').slice(0, -1).join('/')) ||
        (newNodeData.path && newNodeData.path.split('/').slice(0, -1).join('/')) ||
        '';

      const response = await createNode({
        ...newNodeData,
        graph_base_path: graphBasePath,
      });
      if (response.success) {
        setOpenDialog(false);
        setNewNodeData({
          name: '',
          path: '',
          parent_id: null,
          node_type: 'folder',
        });
        loadTree();

        // Mostrar sugerencia de grafo si existe
        if (response.graph) {
          setGraphToast(response.graph.toast);
          setGraphRelated(response.graph.related_folders || []);
        } else {
          setGraphToast(null);
          setGraphRelated([]);
        }

        // Recargar relaciones después de crear un nodo
        const relationsResponse = await getTreeRelations();
        if (relationsResponse.success) {
          setRelations(relationsResponse.relations || {});
        } else if (response.graph?.relations_bidirectional) {
          setRelations(response.graph.relations_bidirectional);
        }
      }
    } catch (err) {
      setError('Error creando nodo: ' + err.message);
    }
  };

  const handleDeleteNode = async (nodeId) => {
    if (typeof nodeId !== 'number') {
      setError('No se puede eliminar este nodo porque no está registrado en la base de datos.');
      return;
    }
    if (window.confirm('¿Estás seguro de eliminar este nodo?')) {
      try {
        const response = await deleteNode(nodeId);
        if (response.success) {
          loadTree();
        } else {
          setError(response.message || 'Error eliminando nodo');
        }
      } catch (err) {
        setError('Error eliminando nodo: ' + err.message);
      }
    }
  };

  const handleEditNode = (node) => {
    if (typeof node.id !== 'number') {
      setError('No se puede editar este nodo porque no está registrado en la base de datos.');
      return;
    }
    setEditNodeData({
      id: node.id,
      name: node.name,
      path: node.path,
      parent_id: node.parent_id,
      node_type: node.node_type,
    });
    setEditDialog(true);
  };

  const handleEditNodeNameChange = (name) => {
    // Actualizar el path automáticamente cuando cambia el nombre
    if (monitorConfig && monitorConfig.watch_folder) {
      const basePath = monitorConfig.watch_folder;
      const newPath = `${basePath}/Organized/${name}`;
      setEditNodeData({
        ...editNodeData,
        name: name,
        path: newPath,
      });
    } else {
      setEditNodeData({
        ...editNodeData,
        name: name,
      });
    }
  };

  const handleUpdateNode = async () => {
    try {
      const response = await updateNode(editNodeData.id, editNodeData);
      if (response.success) {
        setEditDialog(false);
        setEditNodeData({
          id: null,
          name: '',
          path: '',
          parent_id: null,
          node_type: 'folder',
        });
        loadTree();
      } else {
        setError(response.message || 'Error actualizando nodo');
      }
    } catch (err) {
      setError('Error actualizando nodo: ' + err.message);
    }
  };

  const deriveBasePath = (nodePath) => {
    if (monitorConfig?.watch_folder) return monitorConfig.watch_folder;
    if (!nodePath) return '';
    const parts = nodePath.split('/');
    if (parts.length > 1) {
      parts.pop();
      return parts.join('/');
    }
    return nodePath;
  };

  const handleNodeCopy = async (node, relatedFolder) => {
    try {
      setActionLoading(true);
      setActionError(null);
      const basePath = deriveBasePath(node.path);
      const response = await connectProjectFolders({
        base_path: basePath,
        current_folder: node.path,
        preferred_related_folder: relatedFolder || null,
        copy_on_confirm: true,
        create_backup: false,
      });

      if (response.success) {
        const copyResult = response.result?.copy_result;
        const toast = response.result?.toast;
        const selectedRelation = response.result?.selected_relation;
        const bidirectional = response.result?.relations_bidirectional;
        if (bidirectional) {
          setRelations(bidirectional);
        }
        if (copyResult) {
          const copied = copyResult.copied?.length || 0;
          const skipped = copyResult.skipped?.length || 0;
          const relName = selectedRelation?.folder || relatedFolder || 'mejor coincidencia';
          setActionMessage(`Copiado desde relación (${relName}): ${copied} archivos, ${skipped} omitidos.`);
        } else if (toast) {
          setActionMessage(toast);
        } else {
          setActionMessage('Relación detectada pero no se copiaron archivos.');
        }
      } else {
        setActionError(response.message || 'No se pudo copiar desde la relación.');
      }
    } catch (err) {
      setActionError('Error copiando archivos: ' + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const handleNodeBackup = async (node) => {
    try {
      setActionLoading(true);
      setActionError(null);
      const basePath = deriveBasePath(node.path);
      const response = await connectProjectFolders({
        base_path: basePath,
        current_folder: node.path,
        copy_on_confirm: false,
        create_backup: true,
      });

      if (response.success) {
        const bidirectional = response.result?.relations_bidirectional;
        if (bidirectional) {
          setRelations(bidirectional);
        }
        const backupPath = response.result?.backup_path;
        if (backupPath) {
          setActionMessage(`Backup creado en: ${backupPath}`);
        } else {
          setActionMessage('Backup procesado sin ruta devuelta.');
        }
      } else {
        setActionError(response.message || 'No se pudo crear el backup.');
      }
    } catch (err) {
      setActionError('Error creando backup: ' + err.message);
    } finally {
      setActionLoading(false);
    }
  };

  const toggleNode = (nodeId) => {
    const newExpanded = new Set(expandedNodes);
    if (newExpanded.has(nodeId)) {
      newExpanded.delete(nodeId);
    } else {
      newExpanded.add(nodeId);
    }
    setExpandedNodes(newExpanded);
  };

  const renderTreeNode = (node, level = 0) => {
    const isExpanded = expandedNodes.has(node.id);
    const hasChildren = node.children && node.children.length > 0;
    const nodeRelations = relations[node.path] || [];
    const selectedRelForNode = selectedRelation[node.path] || (nodeRelations[0]?.folder || '');
    
    // Encontrar información del padre
    const parentNode = node.parent_id 
      ? nodes.find(n => n.id === node.parent_id) 
      : null;

    return (
      <Box key={node.id} sx={{ ml: level * 3 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            py: 0.5,
            '&:hover': { bgcolor: 'action.hover' },
          }}
        >
          {hasChildren && (
            <IconButton size="small" onClick={() => toggleNode(node.id)}>
              {isExpanded ? <ExpandMore /> : <ChevronRight />}
            </IconButton>
          )}
          {!hasChildren && <Box sx={{ width: 40 }} />}
          
          <FolderOpen sx={{ mr: 1, color: 'primary.main' }} />
          
          <Box sx={{ flexGrow: 1 }}>
            <Typography component="span" sx={{ fontWeight: 500 }}>
              {getDisplayName(node)}
            </Typography>
            {parentNode && (
              <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary', ml: 0.5 }}>
                Hijo de: {getDisplayName(parentNode)}
              </Typography>
            )}
          </Box>
          
          <Typography variant="caption" sx={{ mr: 2, color: 'text.secondary' }}>
            {node.rules_count || 0} reglas
          </Typography>

          {nodeRelations.length > 0 && (
            <Chip
              label={`Relaciones: ${nodeRelations.length}`}
              color="secondary"
              size="small"
              sx={{ mr: 1 }}
            />
          )}

          <IconButton
            size="small"
            color="primary"
            onClick={() => handleEditNode(node)}
            sx={{ mr: 1 }}
          >
            <Edit fontSize="small" />
          </IconButton>

          <IconButton
            size="small"
            color="error"
            onClick={() => handleDeleteNode(node.id)}
          >
            <Delete fontSize="small" />
          </IconButton>
        </Box>

        {isExpanded && hasChildren && (
          <Box>
            {node.children.map((child) => renderTreeNode(child, level + 1))}
          </Box>
        )}

        {nodeRelations.length > 0 && (
          <Box sx={{ ml: (level + 1) * 3, mt: 1, mb: 2, display: 'flex', flexDirection: 'column', gap: 1.5 }}>
            {nodeRelations.map((rel) => (
              <Box
                key={`${node.id}-${rel.folder}`}
                sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}
              >
                <Chip
                  label={`${rel.folder} (${rel.shared_keywords.join(', ')})`}
                  variant="outlined"
                  size="small"
                  color="secondary"
                />
              </Box>
            ))}
            {nodeRelations.length > 1 && (
              <FormControl size="small" sx={{ minWidth: 220 }}>
                <InputLabel>Selecciona relación</InputLabel>
                <Select
                  label="Selecciona relación"
                  value={selectedRelForNode}
                  onChange={(e) =>
                    setSelectedRelation((prev) => ({
                      ...prev,
                      [node.path]: e.target.value,
                    }))
                  }
                >
                  {nodeRelations.map((rel) => (
                    <MenuItem key={`${node.id}-${rel.folder}-select`} value={rel.folder}>
                      {rel.folder} ({rel.shared_keywords.join(', ')})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                size="small"
                onClick={() => handleNodeCopy(node, selectedRelForNode)}
                disabled={actionLoading}
              >
                Copiar mejor relación
              </Button>
              <Button
                variant="outlined"
                size="small"
                onClick={() => handleNodeBackup(node)}
                disabled={actionLoading}
              >
                Crear backup
              </Button>
            </Box>
          </Box>
        )}
      </Box>
    );
  };

  if (loading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>Cargando árbol...</Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h5">Estructura de Árbol</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={handleOpenDialog}
          >
            Agregar Nodo
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {actionError && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setActionError(null)}>
            {actionError}
          </Alert>
        )}
        {actionMessage && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setActionMessage(null)}>
            {actionMessage}
          </Alert>
        )}
        {graphToast && (
          <Alert severity="info" sx={{ mb: 2 }} onClose={() => setGraphToast(null)}>
            {graphToast}
            {graphRelated.length > 0 && (
              <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {graphRelated.slice(0, 5).map((rel) => (
                  <Chip
                    key={rel.folder}
                    label={`${rel.folder} (${rel.shared_keywords.join(', ')})`}
                    size="small"
                  />
                ))}
                {graphRelated.length > 5 && (
                  <Chip label={`+${graphRelated.length - 5} más`} size="small" />
                )}
              </Box>
            )}
          </Alert>
        )}

        {tree && tree.root ? (
          <Box sx={{ mt: 2 }}>
            {renderTreeNode(tree.root)}
          </Box>
        ) : (
          <Typography color="text.secondary">
            No hay nodos en el árbol. Crea uno para comenzar.
          </Typography>
        )}

        <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Total de nodos: {tree?.total_nodes || 0}
          </Typography>
        </Box>
      </Paper>

      {/* Lista de todos los nodos de la base de datos */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Todos los Nodos en la Base de Datos
        </Typography>
        
        {nodes.length > 0 ? (
          <Box sx={{ mt: 2 }}>
            {nodes.map((node) => {
              const parentNode = node.parent_id 
                ? nodes.find(n => n.id === node.parent_id) 
                : null;
              const nodeRelations = relations[node.path] || [];
              const selectedRelForNode = selectedRelation[node.path] || (nodeRelations[0]?.folder || '');
              
              return (
                <Box
                  key={node.id}
                  sx={{
                    p: 2,
                    mb: 1,
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 1,
                    '&:hover': { bgcolor: 'action.hover' },
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <FolderOpen sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="subtitle1" sx={{ fontWeight: 500 }}>
                      {node.name}
                    </Typography>

                    <Box sx={{ ml: 'auto', display: 'flex', gap: 0.5 }}>
                      <IconButton
                        size="small"
                        color="primary"
                        onClick={() => handleEditNode(node)}
                        sx={{ mr: 1 }}
                      >
                        <Edit fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteNode(node.id)}
                      >
                        <Delete fontSize="small" />
                      </IconButton>
                    </Box>
                  </Box>

                  <Typography variant="body2" color="text.secondary" sx={{ ml: 4 }}>
                    <strong>Ruta:</strong> {node.path}
                  </Typography>

                  <Typography variant="body2" color="text.secondary" sx={{ ml: 4 }}>
                    <strong>Tipo:</strong> {node.node_type}
                  </Typography>

                  {parentNode ? (
                    <Typography variant="body2" sx={{ ml: 4, color: 'info.main' }}>
                      <strong>Hijo de:</strong> {parentNode.name}
                    </Typography>
                  ) : (
                    <Typography variant="body2" sx={{ ml: 4, color: 'success.main' }}>
                      <strong>Nodo Raíz</strong>
                    </Typography>
                  )}
                  
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 4 }}>
                    <strong>Reglas:</strong> {node.rules_count || 0}
                  </Typography>

                  {nodeRelations.length > 0 && (
                    <Box sx={{ mt: 1, ml: 4, display: 'flex', flexDirection: 'column', gap: 1 }}>
                      <Typography variant="body2" color="text.secondary">
                        Relaciones (grafos):
                      </Typography>
                      {nodeRelations.length > 1 && (
                        <FormControl size="small" sx={{ minWidth: 220 }}>
                          <InputLabel>Selecciona relación</InputLabel>
                          <Select
                            label="Selecciona relación"
                            value={selectedRelForNode}
                            onChange={(e) =>
                              setSelectedRelation((prev) => ({
                                ...prev,
                                [node.path]: e.target.value,
                              }))
                            }
                          >
                            {nodeRelations.map((rel) => (
                              <MenuItem key={`${node.id}-${rel.folder}-list`} value={rel.folder}>
                                {rel.folder} ({rel.shared_keywords.join(', ')})
                              </MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      )}
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        <Button
                          variant="contained"
                          size="small"
                          onClick={() => handleNodeCopy(node, selectedRelForNode)}
                          disabled={actionLoading}
                        >
                          Copiar relación
                        </Button>
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => handleNodeBackup(node)}
                          disabled={actionLoading}
                        >
                          Backup
                        </Button>
                      </Box>
                    </Box>
                  )}
                </Box>
              );
            })}
          </Box>
        ) : (
          <Typography color="text.secondary" sx={{ mt: 2 }}>
            No hay nodos en la base de datos.
          </Typography>
        )}
      </Paper>

      {/* Dialog para crear nodo */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Crear Nuevo Nodo</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mt: 2, mb: 2 }}>
            La ruta se genera automáticamente basándose en la carpeta monitoreada.
            Solo necesitas ingresar el nombre del nodo (carpeta).
          </Alert>

          <TextField
            fullWidth
            label="Nombre del Nodo (Carpeta)"
            value={newNodeData.name}
            onChange={(e) => handleNodeNameChange(e.target.value)}
            margin="normal"
            autoFocus
            helperText="Ejemplo: Documentos, Imágenes, Videos, etc."
          />

          <TextField
            fullWidth
            label="Ruta Completa (Auto-generada)"
            value={newNodeData.path}
            margin="normal"
            InputProps={{
              readOnly: true,
            }}
            helperText="Esta ruta se genera automáticamente"
            sx={{
              '& .MuiInputBase-input': {
                bgcolor: 'action.hover',
              },
            }}
          />

          <FormControl fullWidth margin="normal">
            <InputLabel>Nodo Padre (opcional)</InputLabel>
            <Select
              value={newNodeData.parent_id || ''}
              onChange={(e) =>
                setNewNodeData({
                  ...newNodeData,
                  parent_id: e.target.value ? parseInt(e.target.value) : null,
                })
              }
              label="Nodo Padre (opcional)"
            >
              <MenuItem value="">
                <em>Sin padre (Nodo raíz)</em>
              </MenuItem>
              {nodes.map((node) => (
                <MenuItem key={node.id} value={node.id}>
                  {node.name} {node.parent_id && '(hijo)'}
                </MenuItem>
              ))}
            </Select>
            <Typography variant="caption" sx={{ mt: 0.5, ml: 1.5, color: 'text.secondary' }}>
              Selecciona un nodo padre para crear este nodo dentro de él
            </Typography>
          </FormControl>

          {monitorConfig && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                <strong>Carpeta monitoreada:</strong> {monitorConfig.watch_folder}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Carpeta base de organización:</strong> {monitorConfig.watch_folder}/Organized
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancelar</Button>
          <Button
            onClick={handleCreateNode}
            variant="contained"
            disabled={!newNodeData.name || !newNodeData.path}
          >
            Crear
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog para editar nodo */}
      <Dialog open={editDialog} onClose={() => setEditDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Editar Nodo</DialogTitle>
        <DialogContent>
          <Alert severity="info" sx={{ mt: 2, mb: 2 }}>
            Puedes editar el nombre del nodo. La ruta se actualizará automáticamente.
          </Alert>

          <TextField
            fullWidth
            label="Nombre del Nodo (Carpeta)"
            value={editNodeData.name}
            onChange={(e) => handleEditNodeNameChange(e.target.value)}
            margin="normal"
            autoFocus
            helperText="Ejemplo: Documentos, Imágenes, Videos, etc."
          />

          <TextField
            fullWidth
            label="Ruta Completa (Auto-generada)"
            value={editNodeData.path}
            margin="normal"
            InputProps={{
              readOnly: true,
            }}
            helperText="Esta ruta se genera automáticamente"
            sx={{
              '& .MuiInputBase-input': {
                bgcolor: 'action.hover',
              },
            }}
          />

          <FormControl fullWidth margin="normal">
            <InputLabel>Nodo Padre (opcional)</InputLabel>
            <Select
              value={editNodeData.parent_id || ''}
              onChange={(e) =>
                setEditNodeData({
                  ...editNodeData,
                  parent_id: e.target.value ? parseInt(e.target.value) : null,
                })
              }
              label="Nodo Padre (opcional)"
            >
              <MenuItem value="">
                <em>Sin padre (Nodo raíz)</em>
              </MenuItem>
              {nodes.filter(n => n.id !== editNodeData.id).map((node) => (
                <MenuItem key={node.id} value={node.id}>
                  {node.name} {node.parent_id && '(hijo)'}
                </MenuItem>
              ))}
            </Select>
            <Typography variant="caption" sx={{ mt: 0.5, ml: 1.5, color: 'text.secondary' }}>
              Selecciona un nodo padre para mover este nodo dentro de él
            </Typography>
          </FormControl>

          {monitorConfig && (
            <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                <strong>Carpeta monitoreada:</strong> {monitorConfig.watch_folder}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Carpeta base de organización:</strong> {monitorConfig.watch_folder}/Organized
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>Cancelar</Button>
          <Button
            onClick={handleUpdateNode}
            variant="contained"
            disabled={!editNodeData.name || !editNodeData.path}
          >
            Actualizar
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TreeView;
