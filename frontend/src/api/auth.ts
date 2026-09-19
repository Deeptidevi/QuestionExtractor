import { apiClient } from './client';
import { TokenResponse, User } from '../types';

export interface LoginParams {
  username: string;
  password: string;
}

export interface RegisterParams {
  email: string;
  password: string;
  full_name: string;
  role?: string;
}

export const authApi = {
  login: async (params: LoginParams): Promise<TokenResponse> => {
    // OAuth2PasswordRequestForm requires application/x-www-form-urlencoded
    const formData = new URLSearchParams();
    formData.append('username', params.username);
    formData.append('password', params.password);

    const response = await apiClient.post<TokenResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  register: async (params: RegisterParams): Promise<User> => {
    const response = await apiClient.post<User>('/auth/register', params);
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },
};
