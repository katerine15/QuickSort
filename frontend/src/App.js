import React, { useState, useEffect } from 'react';
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
  IconButton,
  Menu,
  MenuItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Badge,
} from '@mui/material';
import {
  AccountTree,
  Monitor,
  Rule,
  History,
  Notifications as NotificationsIcon,
  CheckCircle,
  Clear,
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
  const [notifications, setNotifications] = useState([]);
  const [notificationMenu, setNotificationMenu] = useState(null);

  useEffect(() => {
    loadNotifications();

    // Listen for localStorage changes
    const handleStorageChange = (e) => {
      if (e.key === 'rejectedNotifications') {
        loadNotifications();
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const loadNotifications = () => {
    const savedNotifications = JSON.parse(localStorage.getItem('rejectedNotifications') || '[]');
    setNotifications(savedNotifications);
  };

  const handleTabChange = (event, newValue) => {
    setCurrentTab(newValue);
  };

  const handleNotificationMenu = (event) => {
    setNotificationMenu(event.currentTarget);
  };

  const handleNotificationMenuClose = () => {
    setNotificationMenu(null);
  };

  const clearNotification = (notificationId) => {
    const updatedNotifications = notifications.filter(n => n.id !== notificationId);
    setNotifications(updatedNotifications);
    localStorage.setItem('rejectedNotifications', JSON.stringify(updatedNotifications));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
    localStorage.setItem('rejectedNotifications', JSON.stringify([]));
    setNotificationMenu(null);
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

            {/* Notifications Icon */}
            <IconButton
              color="inherit"
              onClick={handleNotificationMenu}
              sx={{ ml: 2 }}
            >
              <Badge badgeContent={notifications.length} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
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

        {/* Notifications Menu */}
        <Menu
          anchorEl={notificationMenu}
          open={Boolean(notificationMenu)}
          onClose={handleNotificationMenuClose}
          PaperProps={{
            sx: { width: 350, maxHeight: 400 },
          }}
        >
          <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
            <Typography variant="h6">Notificaciones</Typography>
          </Box>

          {notifications.length === 0 ? (
            <MenuItem disabled>
              <ListItemText primary="No hay notificaciones" />
            </MenuItem>
          ) : (
            <>
              {notifications.map((notification) => (
                <MenuItem key={notification.id} sx={{ display: 'flex', alignItems: 'center' }}>
                  <ListItemIcon>
                    <Clear color="error" fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={notification.message}
                    secondary={new Date(notification.timestamp).toLocaleString()}
                  />
                  <IconButton
                    size="small"
                    onClick={() => clearNotification(notification.id)}
                    sx={{ ml: 1 }}
                  >
                    <Clear fontSize="small" />
                  </IconButton>
                </MenuItem>
              ))}

              {notifications.length > 0 && (
                <>
                  <Divider />
                  <MenuItem onClick={clearAllNotifications}>
                    <ListItemText primary="Limpiar todas" />
                  </MenuItem>
                </>
              )}
            </>
          )}
        </Menu>
      </Box>
    </ThemeProvider>
  );
}

export default App;
