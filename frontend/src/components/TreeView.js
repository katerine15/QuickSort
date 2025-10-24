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
} from '@mui/material';
import {
  FolderOpen,
  Add,
  Delete,
  Edit,
  ExpandMore,
  ChevronRight,
} from '@mui/icons-material';
import { getTree, getAllNodes, createNode, deleteNode, updateNode, getMonitorConfig } from '../services/api';

const TreeView = () => {
  const [tree, setTree] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [monitorConfig, setMonitorConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
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

  useEffect(() => {
    loadTree();
    loadMonitorConfig();
  }, []);

  const loadTree = async () => {
    try {
      setLoading(true);
      const [treeResponse, nodesResponse] = await Promise.all([
        getTree(),
        getAllNodes(),
      ]);

      if (treeResponse.success) {
        setTree(treeResponse.tree);
      }

      if (nodesResponse.success) {
        setNodes(nodesResponse.nodes);
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
      const response = await createNode(newNodeData);
      if (response.success) {
        setOpenDialog(false);
        setNewNodeData({
          name: '',
          path: '',
          parent_id: null,
          node_type: 'folder',
        });
        loadTree();
      }
    } catch (err) {
      setError('Error creando nodo: ' + err.message);
    }
  };

  const handleDeleteNode = async (nodeId) => {
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
              {node.name}
            </Typography>
            {parentNode && (
              <Typography variant="caption" sx={{ display: 'block', color: 'text.secondary', ml: 0.5 }}>
                Hijo de: {parentNode.name}
              </Typography>
            )}
          </Box>
          
          <Typography variant="caption" sx={{ mr: 2, color: 'text.secondary' }}>
            {node.rules_count || 0} reglas
          </Typography>

          {/* Solo mostrar edit/delete para nodos que no son root */}
          {node.parent_id !== null && (
            <>
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
            </>
          )}
        </Box>

        {isExpanded && hasChildren && (
          <Box>
            {node.children.map((child) => renderTreeNode(child, level + 1))}
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

                    {/* Solo mostrar edit/delete para nodos que no son root */}
                    {node.parent_id !== null && (
                      <Box sx={{ ml: 'auto' }}>
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
                    )}
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

          <TextField
            fullWidth
            label="ID del Padre (opcional)"
            type="number"
            value={newNodeData.parent_id || ''}
            onChange={(e) =>
              setNewNodeData({
                ...newNodeData,
                parent_id: e.target.value ? parseInt(e.target.value) : null,
              })
            }
            margin="normal"
            helperText="Dejar vacío para crear un nodo raíz"
          />

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

          <TextField
            fullWidth
            label="ID del Padre (opcional)"
            type="number"
            value={editNodeData.parent_id || ''}
            onChange={(e) =>
              setEditNodeData({
                ...editNodeData,
                parent_id: e.target.value ? parseInt(e.target.value) : null,
              })
            }
            margin="normal"
            helperText="Dejar vacío para nodo raíz"
          />

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
