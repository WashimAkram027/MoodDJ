import React, { useEffect, useState, createContext } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import { testBackendConnection } from './services/testConnection';
import { authService } from './services/authService';

// Create Auth Context for global auth state
export const AuthContext = createContext(null);

// Dark theme for MoodDJ
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#1DB954', // Spotify green
    },
    secondary: {
      main: '#FF006E',
    },
    background: {
      default: '#121212',
      paper: '#1E1E1E',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  useEffect(() => {
    // Test backend connection and check auth status on app load
    const initializeApp = async () => {
      try {
        // Test backend connection
        await testBackendConnection();

        // Check if user is authenticated
        const authStatus = await authService.checkAuthStatus();

        if (authStatus.authenticated) {
          setIsAuthenticated(true);
          setUser(authStatus.user);
          console.log('User is authenticated:', authStatus.user);
        } else {
          setIsAuthenticated(false);
          setUser(null);
        }
      } catch (error) {
        console.error('App initialization error:', error);
        setIsAuthenticated(false);
        setUser(null);
      } finally {
        setAuthLoading(false);
      }
    };

    initializeApp();
  }, []);

  const authContextValue = {
    isAuthenticated,
    user,
    authLoading,
    setIsAuthenticated,
    setUser,
  };

  return (
    <AuthContext.Provider value={authContextValue}>
      <ThemeProvider theme={darkTheme}>
        <CssBaseline />
        <Router>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
          </Routes>
        </Router>
      </ThemeProvider>
    </AuthContext.Provider>
  );
}

export default App;