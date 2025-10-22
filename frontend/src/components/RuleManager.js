import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Alert,
  Switch,
} from '@mui/material';
import { Add, Delete, Edit } from '@mui/icons-material';
import { getRules, createRule, updateRule, deleteRule, getAllNodes } from '../services/api';

const RuleManager = () => {
  const [rules, setRules] = useState([]);
  const [nodes, setNodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingRule, setEditingRule] = useState(null);
  const [ruleData, setRuleData] = useState({
    node_id: '',
    rule_type: 'extension',
    pattern: '',
    priority: 0,
    is_active: true,
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [rulesResponse, nodesResponse] = await Promise.all([
        getRules(),
        getAllNodes(),
      ]);

      if (rulesResponse.success) {
        setRules(rulesResponse.rules);
      }

      if (nodesResponse.success) {
        setNodes(nodesResponse.nodes);
      }

      setError(null);
    } catch (err) {
      setError('Error cargando datos: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDialog = (rule = null) => {
    if (rule) {
      setEditingRule(rule);
      setRuleData({
        node_id: rule.node_id,
        rule_type: rule.rule_type,
        pattern: rule.pattern,
        priority: rule.priority,
        is_active: rule.is_active,
      });
    } else {
      setEditingRule(null);
      setRuleData({
        node_id: '',
        rule_type: 'extension',
        pattern: '',
        priority: 0,
        is_active: true,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingRule(null);
  };

  const handleSaveRule = async () => {
    try {
      let response;
      if (editingRule) {
        response = await updateRule(editingRule.id, ruleData);
      } else {
        response = await createRule(ruleData);
      }

      if (response.success) {
        setSuccess(
          editingRule ? 'Regla actualizada correctamente' : 'Regla creada correctamente'
        );
        handleCloseDialog();
        loadData();
      }
    } catch (err) {
      setError('Error guardando regla: ' + err.message);
    }
  };

  const handleDeleteRule = async (ruleId) => {
    if (window.confirm('¿Estás seguro de eliminar esta regla?')) {
      try {
        const response = await deleteRule(ruleId);
        if (response.success) {
          setSuccess('Regla eliminada correctamente');
          loadData();
        }
      } catch (err) {
        setError('Error eliminando regla: ' + err.message);
      }
    }
  };

  const handleToggleActive = async (rule) => {
    try {
      const response = await updateRule(rule.id, {
        is_active: !rule.is_active,
      });
      if (response.success) {
        loadData();
      }
    } catch (err) {
      setError('Error actualizando regla: ' + err.message);
    }
  };

  const getNodeName = (nodeId) => {
    const node = nodes.find((n) => n.id === nodeId);
    return node ? node.name : 'Desconocido';
  };

  const getRuleTypeLabel = (type) => {
    const labels = {
      extension: 'Extensión',
      keyword: 'Palabra clave',
      size: 'Tamaño',
      date: 'Fecha',
    };
    return labels[type] || type;
  };

  if (loading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>Cargando reglas...</Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h5">Reglas de Organización</Typography>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => handleOpenDialog()}
          >
            Nueva Regla
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
            {success}
          </Alert>
        )}

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Nodo</TableCell>
                <TableCell>Tipo</TableCell>
                <TableCell>Patrón</TableCell>
                <TableCell>Prioridad</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell align="right">Acciones</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rules.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    <Typography color="text.secondary">
                      No hay reglas configuradas. Crea una para comenzar.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                rules.map((rule) => (
                  <TableRow key={rule.id}>
                    <TableCell>{getNodeName(rule.node_id)}</TableCell>
                    <TableCell>
                      <Chip
                        label={getRuleTypeLabel(rule.rule_type)}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <code>{rule.pattern}</code>
                    </TableCell>
                    <TableCell>{rule.priority}</TableCell>
                    <TableCell>
                      <Switch
                        checked={rule.is_active}
                        onChange={() => handleToggleActive(rule)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      <IconButton
                        size="small"
                        onClick={() => handleOpenDialog(rule)}
                      >
                        <Edit fontSize="small" />
                      </IconButton>
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDeleteRule(rule.id)}
                      >
                        <Delete fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Dialog para crear/editar regla */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingRule ? 'Editar Regla' : 'Nueva Regla'}
        </DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>Nodo de Destino</InputLabel>
            <Select
              value={ruleData.node_id}
              onChange={(e) => setRuleData({ ...ruleData, node_id: e.target.value })}
              label="Nodo de Destino"
            >
              {nodes.map((node) => (
                <MenuItem key={node.id} value={node.id}>
                  {node.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth margin="normal">
            <InputLabel>Tipo de Regla</InputLabel>
            <Select
              value={ruleData.rule_type}
              onChange={(e) =>
                setRuleData({ ...ruleData, rule_type: e.target.value })
              }
              label="Tipo de Regla"
            >
              <MenuItem value="extension">Extensión</MenuItem>
              <MenuItem value="keyword">Palabra clave</MenuItem>
              <MenuItem value="size">Tamaño</MenuItem>
              <MenuItem value="date">Fecha</MenuItem>
            </Select>
          </FormControl>

          <TextField
            fullWidth
            label="Patrón"
            value={ruleData.pattern}
            onChange={(e) => setRuleData({ ...ruleData, pattern: e.target.value })}
            margin="normal"
            helperText={
              ruleData.rule_type === 'extension'
                ? 'Ejemplo: .pdf, .jpg, .docx'
                : 'Ejemplo: factura, reporte, contrato'
            }
          />

          <TextField
            fullWidth
            label="Prioridad"
            type="number"
            value={ruleData.priority}
            onChange={(e) =>
              setRuleData({ ...ruleData, priority: parseInt(e.target.value) })
            }
            margin="normal"
            helperText="Mayor número = mayor prioridad"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancelar</Button>
          <Button
            onClick={handleSaveRule}
            variant="contained"
            disabled={!ruleData.node_id || !ruleData.pattern}
          >
            {editingRule ? 'Actualizar' : 'Crear'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default RuleManager;
