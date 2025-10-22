import React, { useState } from 'react';
import {
  Box,
  Container,
  AppBar,
  Toolbar,
  Typography,
  Tabs,
  Tab,
  CssBaseline,
  ThemeProvider,
  createTheme,
} from '@mui/material';
import {
  AccountTree,
  Monitor,
  Rule,
  History,
} from '@mui/icons-material';
import TreeView from './components/TreeView';
import FileMonitor from './components/FileMonitor';
import RuleManager from './components/RuleManager';
import LogViewer from './components/LogViewer';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [currentTab, setCurrentTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <AccountTree sx={{ mr: 2 }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              QuickSort - Organizador Automático de Archivos
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl">
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mt: 2 }}>
            <Tabs value={currentTab} onChange={handleTabChange}>
              <Tab icon={<AccountTree />} label="Árbol" />
              <Tab icon={<Monitor />} label="Monitor" />
              <Tab icon={<Rule />} label="Reglas" />
              <Tab icon={<History />} label="Historial" />
            </Tabs>
          </Box>

          <TabPanel value={currentTab} index={0}>
            <TreeView />
          </TabPanel>

          <TabPanel value={currentTab} index={1}>
            <FileMonitor />
          </TabPanel>

          <TabPanel value={currentTab} index={2}>
            <RuleManager />
          </TabPanel>

          <TabPanel value={currentTab} index={3}>
            <LogViewer />
          </TabPanel>
        </Container>

        <Box
          component="footer"
          sx={{
            py: 3,
            px: 2,
            mt: 'auto',
            backgroundColor: (theme) =>
              theme.palette.mode === 'light'
                ? theme.palette.grey[200]
                : theme.palette.grey[800],
            textAlign: 'center',
          }}
        >
          <Typography variant="body2" color="text.secondary">
            QuickSort © 2024 - Organizador de archivos con estructura de árbol
          </Typography>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
