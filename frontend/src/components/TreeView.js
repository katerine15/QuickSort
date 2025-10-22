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
  ExpandMore,
  ChevronRight,
} from '@mui/icons-material';
import { getTree, getAllNodes, createNode, deleteNode } from '../services/api';

const TreeView = () => {
  const [tree, setTree] = useState(null);
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [newNodeData, setNewNodeData] = useState({
    name: '',
    path: '',
    parent_id: null,
    node_type: 'folder',
  });
  const [expandedNodes, setExpandedNodes] = useState(new Set());

  useEffect(() => {
    loadTree();
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
        }
      } catch (err) {
        setError('Error eliminando nodo: ' + err.message);
      }
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
          
          <Typography sx={{ flexGrow: 1 }}>{node.name}</Typography>
          
          <Typography variant="caption" sx={{ mr: 2, color: 'text.secondary' }}>
            {node.rules_count || 0} reglas
          </Typography>
          
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
          <Typography variant="h5">Estructura del Árbol</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setOpenDialog(true)}
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

      {/* Dialog para crear nodo */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Crear Nuevo Nodo</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Nombre"
            value={newNodeData.name}
            onChange={(e) =>
              setNewNodeData({ ...newNodeData, name: e.target.value })
            }
            margin="normal"
          />
          <TextField
            fullWidth
            label="Ruta"
            value={newNodeData.path}
            onChange={(e) =>
              setNewNodeData({ ...newNodeData, path: e.target.value })
            }
            margin="normal"
            helperText="Ruta completa donde se guardarán los archivos"
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
          />
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
    </Box>
  );
};

export default TreeView;
