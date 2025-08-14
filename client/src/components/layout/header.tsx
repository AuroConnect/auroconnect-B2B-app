import { Link, useLocation } from "wouter";
import { useAuth } from "@/hooks/useAuth";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Bell, User, Settings, LogOut, Menu, Sparkles, ShoppingCart, Package } from "lucide-react";
import type { User as UserType } from "@/hooks/useAuth";
import { getQueryFn } from "@/lib/queryClient";
import { Badge } from "@/components/ui/badge";

interface CartItem {
  id: string;
  productId: string;
  productName: string;
  productSku: string;
  productImage: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  availableStock: number;
}

interface Cart {
  id: string;
  items: CartItem[];
  totalItems: number;
  totalAmount: number;
}

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth();
  const [location, setLocation] = useLocation();

  // Fetch cart data for cart icon with real-time updates
  const { data: cart, isLoading: cartLoading } = useQuery<Cart>({
    queryKey: ["api", "cart"],
    queryFn: getQueryFn({ on401: "returnNull" }),
    enabled: !!user,
    refetchInterval: 5000, // Refresh every 5 seconds for real-time updates
    staleTime: 2000, // Consider data stale after 2 seconds
  });

  if (!isAuthenticated || !user) {
    return null;
  }

  const typedUser = user as UserType;

  const getInitials = (firstName?: string | null, lastName?: string | null) => {
    return `${firstName?.[0] || ''}${lastName?.[0] || ''}`.toUpperCase() || 'U';
  };

  const handleLogout = () => {
    logout();
    window.location.href = "/";
  };

  const handleProfile = () => {
    setLocation("/profile");
  };

  const handleSettings = () => {
    setLocation("/settings");
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  return (
    <header className="glass-card sticky top-0 z-50 border-b border-white/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center" data-testid="link-home">
              <div className="w-8 h-8 auromart-gradient-primary rounded-lg flex items-center justify-center mr-3">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">AuroMart</span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            <Link 
              href="/" 
              className={`nav-link ${
                location === '/' 
                  ? 'text-primary bg-primary/10' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              data-testid="nav-dashboard"
            >
              Dashboard
            </Link>
            <Link 
              href="/products" 
              className={`nav-link ${
                location === '/products' 
                  ? 'text-primary bg-primary/10' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              data-testid="nav-products"
            >
              Products
            </Link>
            <Link 
              href="/partners" 
              className={`nav-link ${
                location === '/partners' 
                  ? 'text-primary bg-primary/10' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              data-testid="nav-partners"
            >
              Partners
            </Link>
            <Link 
              href="/orders" 
              className={`nav-link ${
                location === '/orders' 
                  ? 'text-primary bg-primary/10' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              data-testid="nav-orders"
            >
              Orders
            </Link>
            <Link 
              href="/reports" 
              className={`nav-link ${
                location === '/reports' 
                  ? 'text-primary bg-primary/10' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              data-testid="nav-reports"
            >
              Reports
            </Link>
          </nav>

          {/* User Menu */}
          <div className="flex items-center space-x-4">
            {/* Enhanced Cart - Only show for Distributors and Retailers */}
            {user?.role !== 'manufacturer' && (
              <Link href="/cart">
              <Button variant="ghost" size="sm" className="relative group">
                <div className="flex items-center space-x-2">
                  <ShoppingCart className="h-5 w-5" />
                  {cartLoading && (
                    <div className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                  )}
                </div>
                
                {/* Cart Badge */}
                {cart?.totalItems > 0 && (
                  <Badge className="absolute -top-1 -right-1 w-5 h-5 auromart-gradient-secondary rounded-full text-xs text-white flex items-center justify-center font-medium border-2 border-white">
                    {cart.totalItems > 99 ? '99+' : cart.totalItems}
                  </Badge>
                )}
                
                {/* Cart Tooltip */}
                <div className="absolute bottom-full right-0 mb-2 w-64 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none z-50">
                  <div className="p-3">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900">Shopping Cart</span>
                      <Package className="h-4 w-4 text-gray-400" />
                    </div>
                    
                    {cart?.items && cart.items.length > 0 ? (
                      <div className="space-y-2">
                        {cart.items.slice(0, 3).map((item) => (
                          <div key={item.id} className="flex items-center space-x-2">
                            <div className="w-8 h-8 bg-gray-100 rounded flex items-center justify-center">
                              <Package className="h-3 w-3 text-gray-600" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="text-xs font-medium text-gray-900 truncate">
                                {item.productName}
                              </p>
                              <p className="text-xs text-gray-500">
                                Qty: {item.quantity} × {formatCurrency(item.unitPrice)}
                              </p>
                            </div>
                          </div>
                        ))}
                        
                        {cart.items.length > 3 && (
                          <p className="text-xs text-gray-500 text-center">
                            +{cart.items.length - 3} more items
                          </p>
                        )}
                        
                        <div className="border-t pt-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-gray-900">Total:</span>
                            <span className="text-sm font-bold text-gray-900">
                              {formatCurrency(cart.totalAmount)}
                            </span>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-2">
                        <p className="text-sm text-gray-500">Your cart is empty</p>
                      </div>
                    )}
                  </div>
                </div>
              </Button>
            </Link>
            )}

            {/* Notifications */}
            <Button variant="ghost" size="sm" className="relative">
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 w-3 h-3 auromart-gradient-secondary rounded-full"></span>
            </Button>

            {/* User Dropdown */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="flex items-center space-x-2 hover:bg-gray-100">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={typedUser.profileImageUrl} />
                    <AvatarFallback className="auromart-gradient-primary text-white">
                      {getInitials(typedUser.firstName, typedUser.lastName)}
                    </AvatarFallback>
                  </Avatar>
                  <span className="hidden md:block text-sm font-medium">
                    {typedUser.firstName} {typedUser.lastName}
                  </span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="enhanced-dropdown w-56">
                <DropdownMenuLabel className="enhanced-dropdown-label">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none text-gray-900">
                      {typedUser.firstName} {typedUser.lastName}
                    </p>
                    <p className="text-xs leading-none text-gray-500">
                      {typedUser.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="enhanced-dropdown-item" onClick={handleProfile}>
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem className="enhanced-dropdown-item" onClick={handleSettings}>
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  className="enhanced-dropdown-item-danger"
                  onClick={handleLogout}
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </header>
  );
}