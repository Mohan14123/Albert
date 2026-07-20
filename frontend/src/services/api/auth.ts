import { apiClient } from "@/lib/api-client";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  assistant_name: string;
  is_active: boolean;
}

export const authApi = {
  login: (email: string, password: string) =>
    apiClient<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
      skipAuth: true,
    }),

  register: (email: string, password: string, fullName: string) =>
    apiClient<{ data: { user_id: string } }>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name: fullName }),
      skipAuth: true,
    }),

  googleLogin: (idToken: string) =>
    apiClient<TokenResponse>("/auth/google-login", {
      method: "POST",
      body: JSON.stringify({ id_token: idToken }),
      skipAuth: true,
    }),

  refresh: (refreshToken: string) =>
    apiClient<TokenResponse>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
      skipAuth: true,
    }),

  logout: (refreshToken: string) =>
    apiClient("/auth/logout", {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),

  logoutAll: () =>
    apiClient("/auth/logout-all", {
      method: "POST",
    }),

  getMe: () => apiClient<UserResponse>("/auth/me"),
};
