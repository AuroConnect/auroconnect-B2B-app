import { useAuth } from "@/hooks/useAuth";
import Header from "@/components/layout/header";
import MobileNav from "@/components/layout/mobile-nav";
import Cart from "@/components/cart/cart";
import { useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import { ShoppingCart } from "lucide-react";

export default function CartPage() {
  const { user, isLoading } = useAuth();
  const { toast } = useToast();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !user) {
      toast({
        title: "Unauthorized", 
        description: "You are logged out. Logging in again...",
        variant: "destructive",
      });
      setTimeout(() => {
        window.location.href = "/";
      }, 500);
      return;
    }
  }, [user, isLoading, toast]);

  if (isLoading || !user) {
    return (
      <div className="min-h-screen auromart-gradient-bg flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading cart...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header />
      
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 auromart-gradient-primary rounded-2xl flex items-center justify-center mr-4">
              <ShoppingCart className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Shopping Cart
              </h1>
              <p className="text-gray-600">
                Review and manage your order items
              </p>
            </div>
          </div>
        </div>

        {/* Cart Component */}
        <Cart />
      </div>
      
      <MobileNav />
    </div>
  );
}
