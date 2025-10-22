import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  Alert,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import { Refresh, CheckCircle, Error, Info } from '@mui/icons-material';
import { getLogs, getLogStats } from '../services/api';

const LogViewer = () => {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadLogs();
    const interval = setInterval(loadLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadLogs = async () => {
    try {
      const [logsResponse, statsResponse] = await Promise.all([
        getLogs(50),
        getLogStats(),
      ]);

      if (logsResponse.success) {
        setLogs(logsResponse.logs);
      }

      if (statsResponse.success) {
        setStats(statsResponse.stats);
      }

      setError(null);
    } catch (err) {
      setError('Error cargando logs: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const getStatusChip = (status) => {
    const statusConfig = {
      success: { label: 'Éxito', color: 'success', icon: <CheckCircle /> },
      failed: { label: 'Fallido', color: 'error', icon: <Error /> },
      pending: { label: 'Pendiente', color: 'warning', icon: <Info /> },
    };

    const config = statusConfig[status] || statusConfig.pending;

    return (
      <Chip
        label={config.label}
        color={config.color}
        size="small"
        icon={config.icon}
      />
    );
  };

  const getActionChip = (action) => {
    const actionConfig = {
      moved: { label: 'Movido', color: 'primary' },
      copied: { label: 'Copiado', color: 'info' },
      deleted: { label: 'Eliminado', color: 'error' },
    };

    const config = actionConfig[action] || { label: action, color: 'default' };

    return <Chip label={config.label} color={config.color} size="small" />;
  };

  if (loading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>Cargando logs...</Typography>
      </Paper>
    );
  }

  return (
    <Box>
      {/* Estadísticas */}
      {stats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total de Operaciones
                </Typography>
                <Typography variant="h4">{stats.total}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ bgcolor: 'success.light' }}>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Exitosas
                </Typography>
                <Typography variant="h4">{stats.success}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ bgcolor: 'error.light' }}>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Fallidas
                </Typography>
                <Typography variant="h4">{stats.failed}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Tabla de Logs */}
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h5">Historial de Operaciones</Typography>
          <IconButton onClick={loadLogs}>
            <Refresh />
          </IconButton>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Fecha</TableCell>
                <TableCell>Archivo</TableCell>
                <TableCell>Acción</TableCell>
                <TableCell>Estado</TableCell>
                <TableCell>Destino</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {logs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    <Typography color="text.secondary">
                      No hay logs disponibles
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                logs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell>{formatDate(log.timestamp)}</TableCell>
                    <TableCell>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 200 }}>
                        {log.filename}
                      </Typography>
                    </TableCell>
                    <TableCell>{getActionChip(log.action)}</TableCell>
                    <TableCell>{getStatusChip(log.status)}</TableCell>
                    <TableCell>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        noWrap
                        sx={{ maxWidth: 300 }}
                      >
                        {log.destination_path || 'N/A'}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {logs.length > 0 && (
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Mostrando los últimos 50 registros
            </Typography>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default LogViewer;
