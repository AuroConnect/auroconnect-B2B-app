import { QueryClient, QueryFunction } from "@tanstack/react-query";

// API Base URL - change this to your Flask backend URL
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:5001';

// Get JWT token from localStorage
function getAuthToken(): string | null {
  return localStorage.getItem('authToken');
}

// Set JWT token in localStorage
export function setAuthToken(token: string): void {
  localStorage.setItem('authToken', token);
}

// Remove JWT token from localStorage
export function removeAuthToken(): void {
  localStorage.removeItem('authToken');
}

async function throwIfResNotOk(res: Response) {
  if (!res.ok) {
    const text = (await res.text()) || res.statusText;
    throw new Error(`${res.status}: ${text}`);
  }
}

export async function apiRequest(
  method: string,
  url: string,
  data?: unknown | undefined,
): Promise<Response> {
  const token = getAuthToken();
  const headers: Record<string, string> = {};
  
  if (data) {
    headers['Content-Type'] = 'application/json';
  }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE_URL}${url}`, {
    method,
    headers,
    body: data ? JSON.stringify(data) : undefined,
  });

  await throwIfResNotOk(res);
  return res;
}

type UnauthorizedBehavior = "returnNull" | "throw";
export const getQueryFn: <T>(options: {
  on401: UnauthorizedBehavior;
}) => QueryFunction<T> =
  ({ on401: unauthorizedBehavior }) =>
  async ({ queryKey }) => {
    const token = getAuthToken();
    const headers: Record<string, string> = {};
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    // Construct URL properly with trailing slash for endpoints that need it
    const path = queryKey.join("/");
    const url = path.startsWith('/') ? path : `/${path}`;
    
    // Add trailing slash for specific endpoints that need it
    const endpointsNeedingTrailingSlash = ['api/orders', 'api/products', 'api/favorites', 'api/partnerships', 'api/notifications'];
    const finalUrl = endpointsNeedingTrailingSlash.some(endpoint => url.includes(endpoint)) ? `${url}/` : url;

    const res = await fetch(`${API_BASE_URL}${finalUrl}`, {
      headers,
    });

    if (unauthorizedBehavior === "returnNull" && res.status === 401) {
      return null;
    }

    await throwIfResNotOk(res);
    return await res.json();
  };

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      queryFn: getQueryFn({ on401: "throw" }),
      refetchInterval: false,
      refetchOnWindowFocus: false,
      staleTime: Infinity,
      retry: false,
    },
    mutations: {
      retry: false,
    },
  },
});
