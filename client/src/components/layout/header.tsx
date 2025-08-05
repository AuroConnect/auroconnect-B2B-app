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
import { Bell, User, Settings, LogOut, Menu } from "lucide-react";
import type { User as UserType } from "@shared/schema";

export default function Header() {
  const { user, isAuthenticated } = useAuth();
  const [location] = useLocation();

  if (!isAuthenticated || !user) {
    return null;
  }

  const typedUser = user as UserType;

  const getInitials = (firstName?: string | null, lastName?: string | null) => {
    return `${firstName?.[0] || ''}${lastName?.[0] || ''}`.toUpperCase() || 'U';
  };

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center" data-testid="link-home">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">A</span>
              </div>
              <span className="ml-2 text-xl font-bold text-gray-900">AuroMart</span>
            </Link>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            <Link 
              href="/" 
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
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
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                location === '/products' 
                  ? 'text-primary bg-primary/10' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              data-testid="nav-products"
            >
              Products
            </Link>
            <Link 
              href="/orders" 
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
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
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                location === '/reports' 
                  ? 'text-primary bg-primary/10' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              data-testid="nav-reports"
            >
              Reports
            </Link>
            <Link 
              href="/partnerships" 
              className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                location === '/partnerships' 
                  ? 'text-primary bg-primary/10' 
                  : 'text-gray-600 hover:text-gray-900'
              }`}
              data-testid="nav-partnerships"
            >
              Partnerships
            </Link>
          </nav>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* Notifications */}
            <Button variant="ghost" size="sm" data-testid="button-notifications">
              <Bell className="h-5 w-5" />
            </Button>

            {/* User Menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full" data-testid="button-user-menu">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={typedUser.profileImageUrl || undefined} alt={typedUser.firstName || 'User'} />
                    <AvatarFallback>{getInitials(typedUser.firstName, typedUser.lastName)}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none" data-testid="text-user-name">
                      {typedUser.firstName} {typedUser.lastName}
                    </p>
                    <p className="text-xs leading-none text-muted-foreground" data-testid="text-user-email">
                      {typedUser.email}
                    </p>
                    <p className="text-xs leading-none text-muted-foreground capitalize" data-testid="text-user-role">
                      {typedUser.role}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem data-testid="menu-profile">
                  <User className="mr-2 h-4 w-4" />
                  <span>Profile</span>
                </DropdownMenuItem>
                <DropdownMenuItem data-testid="menu-settings">
                  <Settings className="mr-2 h-4 w-4" />
                  <span>Settings</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem 
                  onClick={() => window.location.href = '/api/logout'}
                  data-testid="menu-logout"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>

            {/* Mobile menu button */}
            <Button variant="ghost" size="sm" className="md:hidden" data-testid="button-mobile-menu">
              <Menu className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
}