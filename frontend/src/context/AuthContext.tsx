import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, TokenResponse } from '../types';
import { authApi, LoginParams, RegisterParams } from '../api/auth';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (params: LoginParams) => Promise<void>;
  register: (params: RegisterParams) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const cachedUser = localStorage.getItem('docuquest_user');
    return cachedUser ? JSON.parse(cachedUser) : null;
  });
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('docuquest_token');
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Initial authentication check
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('docuquest_token');
      if (storedToken) {
        try {
          const profile = await authApi.getMe();
          setUser(profile);
          localStorage.setItem('docuquest_user', JSON.stringify(profile));
        } catch (err) {
          console.warn('Session expired or invalid token:', err);
          logout();
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (params: LoginParams) => {
    setIsLoading(true);
    try {
      const tokens: TokenResponse = await authApi.login(params);
      localStorage.setItem('docuquest_token', tokens.access_token);
      setToken(tokens.access_token);

      const profile = await authApi.getMe();
      setUser(profile);
      localStorage.setItem('docuquest_user', JSON.stringify(profile));
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (params: RegisterParams) => {
    setIsLoading(true);
    try {
      await authApi.register(params);
      // Auto-login after successful registration
      await login({ username: params.email, password: params.password });
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('docuquest_token');
    localStorage.removeItem('docuquest_user');
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated: !!token && !!user,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
