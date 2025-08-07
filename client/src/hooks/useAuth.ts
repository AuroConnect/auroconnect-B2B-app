import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest, setAuthToken, removeAuthToken } from "@/lib/queryClient";

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: 'retailer' | 'distributor' | 'manufacturer' | 'admin';
  businessName?: string;
  address?: string;
  phoneNumber?: string;
  whatsappNumber?: string;
  isActive: boolean;
  profileImageUrl?: string;
  companyName?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  role: 'retailer' | 'distributor' | 'manufacturer';
  businessName?: string;
  address?: string;
  phoneNumber?: string;
  whatsappNumber?: string;
}

export function useAuth() {
  const queryClient = useQueryClient();

  const { data: user, isLoading, error } = useQuery({
    queryKey: ["api", "auth", "user"],
    retry: false,
    enabled: !!localStorage.getItem('authToken'),
    queryFn: async () => {
      const response = await apiRequest('GET', '/api/auth/user');
      return response.json();
    },
  });

  const loginMutation = useMutation({
    mutationFn: async (data: LoginData) => {
      const response = await apiRequest('POST', '/api/auth/login', data);
      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.message || "Login failed");
      }
      
      if (result.access_token) {
        setAuthToken(result.access_token);
        queryClient.setQueryData(["api", "auth", "user"], result.user);
      }
      
      return result;
    },
    onSuccess: (result) => {
      if (result.user) {
        queryClient.setQueryData(["api", "auth", "user"], result.user);
      }
      queryClient.invalidateQueries({ queryKey: ["api", "auth", "user"] });
    },
  });

  const registerMutation = useMutation({
    mutationFn: async (data: RegisterData) => {
      const response = await apiRequest('POST', '/api/auth/register', data);
      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.message || "Registration failed");
      }
      
      return result;
    },
  });

  const register = (data: RegisterData, callbacks?: { onSuccess?: () => void; onError?: (error: Error) => void }) => {
    registerMutation.mutate(data, {
      onSuccess: (result) => {
        callbacks?.onSuccess?.();
      },
      onError: (error: Error) => {
        callbacks?.onError?.(error);
      },
    });
  };

  const login = (data: LoginData, callbacks?: { onSuccess?: () => void; onError?: (error: Error) => void }) => {
    loginMutation.mutate(data, {
      onSuccess: (result) => {
        callbacks?.onSuccess?.();
      },
      onError: (error: Error) => {
        callbacks?.onError?.(error);
      },
    });
  };

  const logoutMutation = useMutation({
    mutationFn: async () => {
      removeAuthToken();
      queryClient.clear();
    },
  });

  return {
    user: user as User | null,
    isLoading,
    error,
    isAuthenticated: !!user,
    login,
    register,
    logout: logoutMutation.mutate,
    isLoginLoading: loginMutation.isPending,
    isRegisterLoading: registerMutation.isPending,
    loginError: loginMutation.error,
    registerError: registerMutation.error,
  };
}
