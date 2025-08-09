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
import Orders from "@/pages/orders";
import Reports from "@/pages/reports";
import Partnerships from "@/pages/partnerships";
import Partners from "@/pages/partners";
import Register from "@/pages/register";
import Profile from "@/pages/profile";
import Settings from "@/pages/settings";
import Invoices from "@/pages/invoices";
import Suppliers from "@/pages/suppliers";
import Inventory from "@/pages/inventory";
import Retailers from "@/pages/retailers";
import Production from "@/pages/production";
import Distributors from "@/pages/distributors";
import ManufacturerDashboard from "@/pages/manufacturer/dashboard";
import DistributorDashboard from "@/pages/distributor/dashboard";
import RetailerDashboard from "@/pages/retailer/dashboard";
import { withAuth } from "@/components/auth/route-guards";

function Router() {
  const { isAuthenticated, isLoading, user } = useAuth();

  return (
    <Switch>
      {isLoading || !isAuthenticated ? (
        <>
          <Route path="/" component={Landing} />
          <Route path="/register" component={Register} />
        </>
      ) : (
        <>
          {/* Role-based dashboard routes */}
          <Route path="/manufacturer/dashboard" component={ManufacturerDashboard} />
          <Route path="/distributor/dashboard" component={DistributorDashboard} />
          <Route path="/retailer/dashboard" component={RetailerDashboard} />
          
          {/* General routes */}
          <Route path="/" component={withAuth(Dashboard)} />
          <Route path="/products" component={withAuth(Products)} />
          <Route path="/orders" component={withAuth(Orders)} />
          <Route path="/reports" component={withAuth(Reports)} />
          <Route path="/partnerships" component={withAuth(Partnerships)} />
          <Route path="/partners" component={withAuth(Partners)} />
          <Route path="/profile" component={withAuth(Profile)} />
          <Route path="/settings" component={withAuth(Settings)} />
          <Route path="/invoices" component={withAuth(Invoices)} />
          <Route path="/suppliers" component={withAuth(Suppliers)} />
          <Route path="/inventory" component={withAuth(Inventory)} />
          <Route path="/retailers" component={withAuth(Retailers)} />
          <Route path="/production" component={withAuth(Production)} />
          <Route path="/distributors" component={withAuth(Distributors)} />
        </>
      )}
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Router />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
