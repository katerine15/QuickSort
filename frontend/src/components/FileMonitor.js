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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Folder,
  Refresh,
  FolderOpen,
  CheckCircle,
  Warning,
} from '@mui/icons-material';
import {
  getMonitorStatus,
  startMonitor,
  stopMonitor,
  getMonitorConfig,
  updateMonitorConfig,
  getMonitorFiles,
  organizeAllFiles,
} from '../services/api';

const FileMonitor = () => {
  const [status, setStatus] = useState(null);
  const [config, setConfig] = useState(null);
  const [files, setFiles] = useState([]);
  const [filesStats, setFilesStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadingFiles, setLoadingFiles] = useState(false);
  const [organizing, setOrganizing] = useState(false);
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

  const loadFiles = async () => {
    try {
      setLoadingFiles(true);
      const response = await getMonitorFiles();
      
      if (response.success) {
        setFiles(response.files);
        setFilesStats({
          total: response.total,
          with_rules: response.with_rules,
          without_rules: response.without_rules,
        });
      }
    } catch (err) {
      setError('Error cargando archivos: ' + err.message);
    } finally {
      setLoadingFiles(false);
    }
  };

  const handleOrganizeAll = async () => {
    if (!window.confirm('¿Deseas organizar todos los archivos según las reglas definidas?')) {
      return;
    }

    try {
      setOrganizing(true);
      const response = await organizeAllFiles();
      
      if (response.success) {
        setSuccess(`Archivos organizados: ${response.result.stats.files_moved} movidos, ${response.result.stats.files_failed} fallidos`);
        loadFiles(); // Recargar lista de archivos
      }
    } catch (err) {
      setError('Error organizando archivos: ' + err.message);
    } finally {
      setOrganizing(false);
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
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

      {/* Sección de Archivos Detectados */}
      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">
            Archivos en Carpeta Monitoreada
          </Typography>
          <Box>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={loadFiles}
              disabled={loadingFiles}
              sx={{ mr: 1 }}
            >
              {loadingFiles ? 'Cargando...' : 'Actualizar'}
            </Button>
            <Button
              variant="contained"
              color="primary"
              startIcon={organizing ? <CircularProgress size={20} /> : <FolderOpen />}
              onClick={handleOrganizeAll}
              disabled={organizing || !files.length || !filesStats?.with_rules}
            >
              {organizing ? 'Organizando...' : 'Organizar Todos'}
            </Button>
          </Box>
        </Box>

        {filesStats && (
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} md={4}>
              <Box sx={{ p: 2, bgcolor: 'info.light', borderRadius: 1 }}>
                <Typography variant="h4" color="info.dark">
                  {filesStats.total}
                </Typography>
                <Typography variant="body2" color="info.dark">
                  Total de archivos
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ p: 2, bgcolor: 'success.light', borderRadius: 1 }}>
                <Typography variant="h4" color="success.dark">
                  {filesStats.with_rules}
                </Typography>
                <Typography variant="body2" color="success.dark">
                  Con reglas definidas
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ p: 2, bgcolor: 'warning.light', borderRadius: 1 }}>
                <Typography variant="h4" color="warning.dark">
                  {filesStats.without_rules}
                </Typography>
                <Typography variant="body2" color="warning.dark">
                  Sin reglas
                </Typography>
              </Box>
            </Grid>
          </Grid>
        )}

        <Divider sx={{ my: 2 }} />

        {loadingFiles ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
            <CircularProgress />
          </Box>
        ) : files.length === 0 ? (
          <Box sx={{ textAlign: 'center', p: 3 }}>
            <Typography color="text.secondary">
              No hay archivos en la carpeta monitoreada.
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Haz clic en "Actualizar" para escanear la carpeta.
            </Typography>
          </Box>
        ) : (
          <TableContainer sx={{ maxHeight: 400 }}>
            <Table stickyHeader size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Estado</TableCell>
                  <TableCell>Nombre del Archivo</TableCell>
                  <TableCell>Extensión</TableCell>
                  <TableCell>Tamaño</TableCell>
                  <TableCell>Destino</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {files.map((file, index) => (
                  <TableRow key={index} hover>
                    <TableCell>
                      {file.has_rule ? (
                        <CheckCircle color="success" fontSize="small" />
                      ) : (
                        <Warning color="warning" fontSize="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                        {file.filename}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={file.extension || 'N/A'} size="small" />
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatFileSize(file.size)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {file.has_rule ? (
                        <Typography variant="body2" color="success.main">
                          {file.destination_name}
                        </Typography>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          Sin regla
                        </Typography>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Box>
  );
};

export default FileMonitor;
