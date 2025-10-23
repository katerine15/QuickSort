import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==================== ÁRBOL ====================

export const getTree = async () => {
  const response = await api.get('/tree');
  return response.data;
};

export const getAllNodes = async () => {
  const response = await api.get('/tree/nodes');
  return response.data;
};

export const createNode = async (nodeData) => {
  const response = await api.post('/tree/nodes', nodeData);
  return response.data;
};

export const deleteNode = async (nodeId) => {
  const response = await api.delete(`/tree/nodes/${nodeId}`);
  return response.data;
};

// ==================== REGLAS ====================

export const getRules = async () => {
  const response = await api.get('/rules');
  return response.data;
};

export const createRule = async (ruleData) => {
  const response = await api.post('/rules', ruleData);
  return response.data;
};

export const updateRule = async (ruleId, ruleData) => {
  const response = await api.put(`/rules/${ruleId}`, ruleData);
  return response.data;
};

export const deleteRule = async (ruleId) => {
  const response = await api.delete(`/rules/${ruleId}`);
  return response.data;
};

// ==================== MONITOR ====================

export const getMonitorStatus = async () => {
  const response = await api.get('/monitor/status');
  return response.data;
};

export const startMonitor = async () => {
  const response = await api.post('/monitor/start');
  return response.data;
};

export const stopMonitor = async () => {
  const response = await api.post('/monitor/stop');
  return response.data;
};

export const getMonitorConfig = async () => {
  const response = await api.get('/monitor/config');
  return response.data;
};

export const updateMonitorConfig = async (configData) => {
  const response = await api.put('/monitor/config', configData);
  return response.data;
};

export const getMonitorFiles = async () => {
  const response = await api.get('/monitor/files');
  return response.data;
};

export const organizeAllFiles = async () => {
  const response = await api.post('/monitor/organize-all');
  return response.data;
};

// ==================== ORGANIZACIÓN ====================

export const organizeFile = async (filePath) => {
  const response = await api.post('/organize/file', { file_path: filePath });
  return response.data;
};

export const organizeFolder = async (folderPath, recursive = false) => {
  const response = await api.post('/organize/folder', {
    folder_path: folderPath,
    recursive: recursive,
  });
  return response.data;
};

export const previewOrganization = async (folderPath, recursive = false) => {
  const response = await api.post('/organize/preview', {
    folder_path: folderPath,
    recursive: recursive,
  });
  return response.data;
};

// ==================== LOGS ====================

export const getLogs = async (limit = 100) => {
  const response = await api.get(`/logs?limit=${limit}`);
  return response.data;
};

export const getLogStats = async () => {
  const response = await api.get('/logs/stats');
  return response.data;
};

// ==================== HEALTH CHECK ====================

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
