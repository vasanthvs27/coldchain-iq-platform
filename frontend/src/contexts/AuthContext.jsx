import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../services/api';

const AuthContext = createContext();

export const ROLES = [
  'Logistics Analyst',
  'Operations Manager',
  'Planner',
  'Supplier',
  'Carrier/Warehouse Operator',
  'Administrator'
];

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState({
    user_id: 'USR-002',
    full_name: 'Sarah Jenkins',
    email: 'analyst@coldchainiq.io',
    role: 'Logistics Analyst',
    organization: 'ColdChain IQ Intelligence'
  });
  const [activeRole, setActiveRole] = useState('Logistics Analyst');
  const [token, setToken] = useState(localStorage.getItem('token') || 'demo-token-2026');
  const [loading, setLoading] = useState(false);

  const login = async (email, password) => {
    try {
      const res = await apiClient.post('/auth/login', { email, password });
      if (res.success && res.data) {
        setUser(res.data.user);
        setActiveRole(res.data.user.role);
        setToken(res.data.access_token);
        localStorage.setItem('token', res.data.access_token);
        return { success: true };
      }
    } catch (err) {
      return { success: false, message: err.message };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
  };

  const switchRole = (newRole) => {
    setActiveRole(newRole);
    if (user) {
      setUser({ ...user, role: newRole });
    }
  };

  return (
    <AuthContext.Provider value={{ user, activeRole, switchRole, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
