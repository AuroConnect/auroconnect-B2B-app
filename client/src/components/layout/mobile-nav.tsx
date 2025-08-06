import { Link, useLocation } from "wouter";
import { Home, Package, ShoppingCart, BarChart3, Users } from "lucide-react";

export default function MobileNav() {
  const [location] = useLocation();

  const navItems = [
    { href: "/", icon: Home, label: "Dashboard" },
    { href: "/products", icon: Package, label: "Products" },
    { href: "/partners", icon: Users, label: "Partners" },
    { href: "/orders", icon: ShoppingCart, label: "Orders" },
    { href: "/reports", icon: BarChart3, label: "Reports" },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 md:hidden">
      <div className="flex justify-around items-center py-2">
        {navItems.map(({ href, icon: Icon, label }) => (
          <Link
            key={href}
            href={href}
            className={`flex flex-col items-center py-2 px-3 rounded-lg transition-colors ${
              location === href
                ? "text-primary bg-primary/10"
                : "text-gray-600"
            }`}
            data-testid={`mobile-nav-${label.toLowerCase()}`}
          >
            <Icon className="h-5 w-5" />
            <span className="text-xs mt-1">{label}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
}