import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { useAuth } from "@/hooks/useAuth";
import NotFound from "@/pages/not-found";
import Landing from "@/pages/landing";
import Dashboard from "@/pages/dashboard";
import Products from "@/pages/products";
import MyProducts from "@/pages/my-products";
import Orders from "@/pages/orders";
import Reports from "@/pages/reports";
import Partnerships from "@/pages/partnerships";
import Partners from "@/pages/partners";
import InviteAccept from "@/pages/invite-accept";
import Register from "@/pages/register";
import Profile from "@/pages/profile";
import Settings from "@/pages/settings";
import Cart from "@/pages/cart";
import Inventory from "@/pages/inventory";
import LoginForm from "@/components/auth/login-form";
import ErrorBoundary from "@/components/ui/error-boundary";

function Router() {
  const { isAuthenticated, isLoading } = useAuth();

  // Show loading state only if we have a token and are checking auth
  const hasToken = !!localStorage.getItem('authToken');
  
  if (hasToken && isLoading) {
    return (
      <div className="min-h-screen auromart-gradient-bg flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <Switch>
      {!isAuthenticated ? (
        <>
          <Route path="/" component={Landing} />
          <Route path="/login" component={LoginPage} />
          <Route path="/register" component={Register} />
          <Route path="/partnerships/invite/:token" component={InviteAccept} />
          <Route component={NotFound} />
        </>
      ) : (
        <>
          <Route path="/" component={Dashboard} />
          <Route path="/products" component={Products} />
          <Route path="/my-products" component={MyProducts} />
          <Route path="/inventory" component={Inventory} />
          <Route path="/cart" component={Cart} />
          <Route path="/orders" component={Orders} />
          <Route path="/reports" component={Reports} />
          <Route path="/partnerships" component={Partnerships} />
          <Route path="/partners" component={Partners} />
          <Route path="/partnerships/invite/:token" component={InviteAccept} />
          <Route path="/profile" component={Profile} />
          <Route path="/settings" component={Settings} />
          <Route component={NotFound} />
        </>
      )}
    </Switch>
  );
}

// Dedicated Login Page Component
function LoginPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-green-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <LoginForm />
        <div className="text-center mt-6">
          <a 
            href="/"
            className="text-gray-700 hover:text-gray-900 font-medium inline-flex items-center"
          >
            ← Back to Home
          </a>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
