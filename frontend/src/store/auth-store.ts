import { create } from "zustand";
import { authApi, UserResponse } from "@/services/api/auth";
import {
  setTokens,
  clearTokens,
  getAccessToken,
  getRefreshToken,
} from "@/lib/auth";

interface AuthState {
  user: UserResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (email: string, password: string) => Promise<void>;
  register: (
    email: string,
    password: string,
    fullName: string
  ) => Promise<void>;
  googleLogin: (idToken: string) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  hydrate: () => Promise<void>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null });
    try {
      const tokens = await authApi.login(email, password);
      setTokens(tokens.access_token, tokens.refresh_token);
      set({ isAuthenticated: true });
      await get().fetchUser();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Login failed";
      set({ error: message, isAuthenticated: false });
      throw err;
    } finally {
      set({ isLoading: false });
    }
  },

  register: async (email, password, fullName) => {
    set({ isLoading: true, error: null });
    try {
      await authApi.register(email, password, fullName);
      // Auto-login after registration
      await get().login(email, password);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Registration failed";
      set({ error: message });
      throw err;
    } finally {
      set({ isLoading: false });
    }
  },

  googleLogin: async (idToken) => {
    set({ isLoading: true, error: null });
    try {
      const tokens = await authApi.googleLogin(idToken);
      setTokens(tokens.access_token, tokens.refresh_token);
      set({ isAuthenticated: true });
      await get().fetchUser();
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Google login failed";
      set({ error: message, isAuthenticated: false });
      throw err;
    } finally {
      set({ isLoading: false });
    }
  },

  logout: async () => {
    try {
      const refreshToken = getRefreshToken();
      if (refreshToken) {
        await authApi.logout(refreshToken);
      }
    } catch {
      // Ignore errors on logout — clear local state regardless
    } finally {
      clearTokens();
      set({ user: null, isAuthenticated: false, error: null });
    }
  },

  fetchUser: async () => {
    try {
      const user = await authApi.getMe();
      set({ user, isAuthenticated: true });
    } catch {
      set({ user: null, isAuthenticated: false });
      clearTokens();
    }
  },

  hydrate: async () => {
    const token = getAccessToken();
    if (token) {
      set({ isLoading: true });
      try {
        await get().fetchUser();
      } finally {
        set({ isLoading: false });
      }
    }
  },

  clearError: () => set({ error: null }),
}));
