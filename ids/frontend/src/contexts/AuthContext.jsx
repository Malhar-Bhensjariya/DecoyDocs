import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isDecoy, setIsDecoy] = useState(false);

  useEffect(() => {
    // Install a global axios response interceptor to catch `X-Decoy` header at any time
    const interceptorId = axios.interceptors.response.use((response) => {
      const decoyHeader = response.headers['x-decoy'];
      if (decoyHeader === '1') setIsDecoy(true);
      return response;
    }, (error) => {
      // also inspect error responses
      if (error?.response?.headers?.['x-decoy'] === '1') setIsDecoy(true);
      return Promise.reject(error);
    });

    // Check if user is logged in on app start
    const token = localStorage.getItem('token');
    if (token) {
      // Verify token with backend
      axios.get('http://localhost:3001/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      })
        .then(response => {
          setUser(response.data);
          // backend can signal decoy with header `X-Decoy: 1`
          const decoyHeader = response.headers['x-decoy'];
          setIsDecoy(decoyHeader === '1');
        })
        .catch(() => {
          localStorage.removeItem('token');
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(false);
    }

    return () => {
      axios.interceptors.response.eject(interceptorId);
    };
  }, []);

  const login = async (username, password) => {
    try {
      const response = await axios.post('http://localhost:3001/api/auth/login', {
        username,
        password
      });

      const { token, user: userData } = response.data;
      localStorage.setItem('token', token);
      setUser(userData);

      // If backend already marks session as decoy, capture that (some setups may flag immediately)
      const decoyHeader = response.headers['x-decoy'];
      setIsDecoy(decoyHeader === '1');

      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Login failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const getToken = () => {
    return localStorage.getItem('token');
  };

  const value = {
    user,
    login,
    logout,
    getToken,
    loading,
    isDecoy
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};