import { QueryClient, QueryFunction } from "@tanstack/react-query";

// API Base URL - change this to your Flask backend URL
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:5000';

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
    let errorMessage = res.statusText;
    try {
      const errorData = await res.json();
      errorMessage = errorData.message || errorData.error || res.statusText;
    } catch {
      // If JSON parsing fails, use status text
    }
    
    // Provide more specific error messages based on status code
    switch (res.status) {
      case 400:
        errorMessage = "Bad request. Please check your input data.";
        break;
      case 401:
        errorMessage = "Unauthorized. Please check your credentials.";
        break;
      case 403:
        errorMessage = "Forbidden. You don't have permission to access this resource.";
        break;
      case 404:
        errorMessage = "Resource not found.";
        break;
      case 409:
        errorMessage = "Conflict. The resource already exists.";
        break;
      case 500:
        errorMessage = "Internal server error. Please try again later.";
        break;
      default:
        errorMessage = errorMessage || "An error occurred.";
    }
    
    throw new Error(`${res.status}: ${errorMessage}`);
  }
}

// Endpoints that need trailing slashes
const ENDPOINTS_NEEDING_TRAILING_SLASH = [
  'api/products',
  'api/orders', 
  'api/favorites',
  'api/notifications',
  'api/partnerships'
];

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

  // Clean the URL and ensure trailing slash for specific API endpoints
  const cleanUrl = url.replace(/\/+/g, '/').replace(/^\//, '');
  const finalUrl = `${API_BASE_URL}/${cleanUrl}`;
  
  // Add trailing slash only for endpoints that need it
  const needsTrailingSlash = ENDPOINTS_NEEDING_TRAILING_SLASH.some(endpoint => 
    finalUrl.includes(endpoint) && !finalUrl.includes('categories')
  );
  const urlWithTrailingSlash = needsTrailingSlash && !finalUrl.endsWith('/') ? `${finalUrl}/` : finalUrl;

  try {
    console.log(`Making API request to: ${urlWithTrailingSlash}`);
    const res = await fetch(urlWithTrailingSlash, {
      method,
      headers,
      body: data ? JSON.stringify(data) : undefined,
    });

    console.log(`Response status: ${res.status}`);
    await throwIfResNotOk(res);
    return res;
  } catch (error) {
    console.error('API request failed:', error);
    console.error('Attempted URL:', urlWithTrailingSlash);
    console.error('API Base URL:', API_BASE_URL);
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error(`Network error: Unable to connect to server at ${API_BASE_URL}. Please check your internet connection and ensure the backend is running.`);
    }
    throw error;
  }
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

    // Build the path from query key
    const pathParts = queryKey.map(part => String(part)).filter(part => part !== '');
    let path = pathParts.join('/');
    
    // Handle query parameters
    const lastPart = pathParts[pathParts.length - 1];
    if (lastPart && lastPart.includes('?')) {
      const [basePath, queryString] = lastPart.split('?');
      if (basePath && queryString) {
        // Remove the last part and add the base path
        pathParts.pop();
        pathParts.push(basePath);
        path = pathParts.join('/');
        path = `${path}?${queryString}`;
      }
    }
    
    // Clean the path to remove double slashes
    const cleanPath = path.replace(/\/+/g, '/').replace(/^\//, '');
    const finalUrl = `${API_BASE_URL}/${cleanPath}`;
    
    // Add trailing slash only for endpoints that need it
    const needsTrailingSlash = ENDPOINTS_NEEDING_TRAILING_SLASH.some(endpoint => 
      finalUrl.includes(endpoint) && !finalUrl.includes('categories')
    );
    const urlWithTrailingSlash = needsTrailingSlash && !finalUrl.endsWith('/') ? `${finalUrl}/` : finalUrl;

    const res = await fetch(urlWithTrailingSlash, {
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

