import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Switch,
  FormControlLabel,
  TextField,
  Alert,
  Chip,
  Grid,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Folder,
  Refresh,
} from '@mui/icons-material';
import {
  getMonitorStatus,
  startMonitor,
  stopMonitor,
  getMonitorConfig,
  updateMonitorConfig,
} from '../services/api';

const FileMonitor = () => {
  const [status, setStatus] = useState(null);
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadMonitorData();
    const interval = setInterval(loadMonitorData, 3000);
    return () => clearInterval(interval);
  }, []);

  const loadMonitorData = async () => {
    try {
      const [statusResponse, configResponse] = await Promise.all([
        getMonitorStatus(),
        getMonitorConfig(),
      ]);

      if (statusResponse.success) {
        setStatus(statusResponse.status);
      }

      if (configResponse.success) {
        setConfig(configResponse.config);
      }

      setError(null);
    } catch (err) {
      setError('Error cargando datos del monitor: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStartMonitor = async () => {
    try {
      const response = await startMonitor();
      if (response.success) {
        setSuccess('Monitor iniciado correctamente');
        loadMonitorData();
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError('Error iniciando monitor: ' + err.message);
    }
  };

  const handleStopMonitor = async () => {
    try {
      const response = await stopMonitor();
      if (response.success) {
        setSuccess('Monitor detenido correctamente');
        loadMonitorData();
      } else {
        setError(response.message);
      }
    } catch (err) {
      setError('Error deteniendo monitor: ' + err.message);
    }
  };

  const handleUpdateConfig = async (field, value) => {
    try {
      const response = await updateMonitorConfig({ [field]: value });
      if (response.success) {
        setConfig(response.config);
        setSuccess('Configuración actualizada');
      }
    } catch (err) {
      setError('Error actualizando configuración: ' + err.message);
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 3 }}>
        <Typography>Cargando monitor...</Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Paper sx={{ p: 3, mb: 2 }}>
        <Typography variant="h5" gutterBottom>
          Monitor de Archivos
        </Typography>

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

        {/* Estado del Monitor */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Estado
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography sx={{ mr: 2 }}>Estado:</Typography>
                <Chip
                  label={status?.is_running ? 'Activo' : 'Inactivo'}
                  color={status?.is_running ? 'success' : 'default'}
                />
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <Typography sx={{ mr: 2 }}>Archivos pendientes:</Typography>
                <Chip label={status?.pending_files || 0} color="info" />
              </Box>
            </Grid>
          </Grid>

          <Box sx={{ mt: 2 }}>
            {status?.is_running ? (
              <Button
                variant="contained"
                color="error"
                startIcon={<Stop />}
                onClick={handleStopMonitor}
              >
                Detener Monitor
              </Button>
            ) : (
              <Button
                variant="contained"
                color="success"
                startIcon={<PlayArrow />}
                onClick={handleStartMonitor}
              >
                Iniciar Monitor
              </Button>
            )}
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={loadMonitorData}
              sx={{ ml: 2 }}
            >
              Actualizar
            </Button>
          </Box>
        </Box>

        {/* Configuración */}
        {config && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Configuración
            </Typography>

            <TextField
              fullWidth
              label="Carpeta a Monitorear"
              value={config.watch_folder}
              onChange={(e) => handleUpdateConfig('watch_folder', e.target.value)}
              margin="normal"
              InputProps={{
                startAdornment: <Folder sx={{ mr: 1, color: 'action.active' }} />,
              }}
              helperText="Ruta de la carpeta que será monitoreada"
            />

            <Box sx={{ mt: 2 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.auto_organize}
                    onChange={(e) =>
                      handleUpdateConfig('auto_organize', e.target.checked)
                    }
                  />
                }
                label="Organizar automáticamente"
              />
            </Box>

            <Box sx={{ mt: 1 }}>
              <FormControlLabel
                control={
                  <Switch
                    checked={config.recursive}
                    onChange={(e) =>
                      handleUpdateConfig('recursive', e.target.checked)
                    }
                  />
                }
                label="Monitorear subcarpetas"
              />
            </Box>

            <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                <strong>Carpeta actual:</strong> {status?.watch_folder}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Auto-organizar:</strong>{' '}
                {status?.auto_organize ? 'Sí' : 'No'}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                <strong>Recursivo:</strong> {status?.recursive ? 'Sí' : 'No'}
              </Typography>
            </Box>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default FileMonitor;
