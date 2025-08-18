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
    retry: 1,
    enabled: !!localStorage.getItem('authToken'),
    staleTime: 5 * 60 * 1000, // 5 minutes
    queryFn: async () => {
      try {
        const response = await apiRequest('GET', '/api/auth/user');
        if (!response.ok) {
          throw new Error('Failed to fetch user data');
        }
        const userData = await response.json();
        console.log('User data fetched:', userData); // Debug log
        return userData;
      } catch (error) {
        console.error('Auth check failed:', error);
        // If auth check fails, clear the token and return null
        localStorage.removeItem('authToken');
        return null;
      }
    }
  });

  // Handle auth errors separately
  if (error) {
    console.error('Auth query error:', error);
    localStorage.removeItem('authToken');
  }

  const loginMutation = useMutation({
    mutationFn: async (data: LoginData) => {
      const response = await apiRequest('POST', '/api/auth/login', data);
      const result = await response.json();
      
      if (!response.ok) {
        throw new Error(result.message || "Login failed");
      }
      
      if (result.access_token) {
        setAuthToken(result.access_token);
        // Immediately set user data in cache
        if (result.user) {
          queryClient.setQueryData(["api", "auth", "user"], result.user);
          console.log('User data set after login:', result.user); // Debug log
        }
      }
      
      return result;
    },
    onSuccess: (result) => {
      // Ensure user data is set and invalidate related queries
      if (result.user) {
        queryClient.setQueryData(["api", "auth", "user"], result.user);
        console.log('User data set in onSuccess:', result.user); // Debug log
      }
      // Invalidate all queries to refresh data
      queryClient.invalidateQueries();
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

  // Debug logging
  console.log('Auth state:', {
    user,
    isLoading,
    error,
    hasToken: !!localStorage.getItem('authToken'),
    isAuthenticated: !!user && !!localStorage.getItem('authToken')
  });

  return {
    user: user as User | null,
    isLoading: isLoading || loginMutation.isPending,
    error,
    isAuthenticated: !!user && !!localStorage.getItem('authToken'),
    login,
    register,
    logout: logoutMutation.mutate,
    isLoginLoading: loginMutation.isPending,
    isRegisterLoading: registerMutation.isPending,
    loginError: loginMutation.error,
    registerError: registerMutation.error,
  };
}
