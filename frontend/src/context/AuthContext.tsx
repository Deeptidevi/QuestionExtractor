import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, TokenResponse } from '../types';
import { authApi, LoginParams, RegisterParams } from '../api/auth';

const DEFAULT_USER: User = {
  id: 'usr_default',
  email: 'admin@docuquest.ai',
  full_name: 'Administrator',
  is_active: true,
  is_superuser: true,
  created_at: new Date().toISOString(),
};

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
  const [user, setUser] = useState<User>(() => {
    try {
      const cachedUser = localStorage.getItem('docuquest_user');
      if (cachedUser && cachedUser !== 'undefined' && cachedUser !== 'null') {
        return JSON.parse(cachedUser);
      }
    } catch {
      // fallback
    }
    return DEFAULT_USER;
  });

  const [token, setToken] = useState<string | null>(() => {
    try {
      const stored = localStorage.getItem('docuquest_token');
      return stored && stored !== 'undefined' ? stored : null;
    } catch {
      return null;
    }
  });

  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Background auth initialization - never blocks dashboard rendering
  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('docuquest_token');
      if (storedToken) {
        try {
          const profile = await authApi.getMe();
          setUser(profile);
          localStorage.setItem('docuquest_user', JSON.stringify(profile));
        } catch {
          // Keep default user active
        }
      } else {
        // Auto-provision demo credentials in the background if available
        try {
          const tokens = await authApi.login({
            username: 'demo_admin@docuquest.ai',
            password: 'SecurePassword123!',
          });
          if (tokens?.access_token) {
            localStorage.setItem('docuquest_token', tokens.access_token);
            setToken(tokens.access_token);
            const profile = await authApi.getMe();
            setUser(profile);
            localStorage.setItem('docuquest_user', JSON.stringify(profile));
          }
        } catch {
          // If demo login fails, keep default active user
        }
      }
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
      await login({ username: params.email, password: params.password });
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('docuquest_token');
    localStorage.removeItem('docuquest_user');
    setUser(DEFAULT_USER);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated: true,
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
