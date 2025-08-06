import { Link, useLocation } from "wouter";
import { useAuth } from "@/hooks/useAuth";
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
import { Bell, User, Settings, LogOut, Menu, Sparkles } from "lucide-react";
import type { User as UserType } from "@/hooks/useAuth";

export default function Header() {
  const { user, isAuthenticated, logout } = useAuth();
  const [location, setLocation] = useLocation();

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