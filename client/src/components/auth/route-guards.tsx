import React from "react";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";

type AllowedRole = "retailer" | "distributor" | "manufacturer" | "admin";

export function withAuth<P>(Component: React.ComponentType<P>) {
  const Wrapped: React.FC<P> = (props) => {
    const { user, isLoading } = useAuth();

    if (isLoading) {
      return (
        <div className="min-h-screen auromart-gradient-bg flex items-center justify-center">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-white text-lg">Loading...</p>
          </div>
        </div>
      );
    }

    if (!user) {
      // Use a hard redirect since we are outside router context
      window.location.href = "/";
      return null;
    }

    return <Component {...props} />;
  };

  Wrapped.displayName = `withAuth(${Component.displayName || Component.name || "Component"})`;
  return Wrapped;
}

export function withRole<P>(Component: React.ComponentType<P>, allowedRoles: AllowedRole[]) {
  const Wrapped: React.FC<P> = (props) => {
    const { user, isLoading } = useAuth();
    const { toast } = useToast();

    if (isLoading) {
      return (
        <div className="min-h-screen auromart-gradient-bg flex items-center justify-center">
          <div className="text-center">
            <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-white text-lg">Loading...</p>
          </div>
        </div>
      );
    }

    if (!user) {
      window.location.href = "/";
      return null;
    }

    if (!allowedRoles.includes(user.role)) {
      // show once and redirect
      try {
        toast({ title: "Access Denied", description: "You do not have permission to view this page.", variant: "destructive" });
      } catch {}
      window.location.href = "/";
      return null;
    }

    return <Component {...props} />;
  };

  Wrapped.displayName = `withRole(${Component.displayName || Component.name || "Component"})`;
  return Wrapped;
}


