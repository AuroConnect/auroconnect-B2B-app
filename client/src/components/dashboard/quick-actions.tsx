import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, ShoppingCart, Package, FileText, Users } from "lucide-react";
import { useLocation } from "wouter";

interface QuickActionsProps {
  userRole: string;
}

export default function QuickActions({ userRole }: QuickActionsProps) {
  const [, setLocation] = useLocation();
  
  const getActionsForRole = () => {
    switch (userRole) {
      case 'retailer':
        return [
          {
            icon: ShoppingCart,
            label: "New Order",
            description: "Place a new order",
            href: "/products",
            testId: "action-new-order"
          },
          {
            icon: FileText,
            label: "View Invoices",
            description: "Check invoices",
            href: "/invoices", 
            testId: "action-view-invoices"
          },
          {
            icon: Users,
            label: "Suppliers",
            description: "Manage suppliers",
            href: "/suppliers",
            testId: "action-suppliers"
          }
        ];
      case 'distributor':
        return [
          {
            icon: Package,
            label: "Manage Inventory",
            description: "Update stock levels",
            href: "/inventory",
            testId: "action-manage-inventory"
          },
          {
            icon: ShoppingCart,
            label: "Process Orders",
            description: "Review pending orders",
            href: "/orders",
            testId: "action-process-orders"
          },
          {
            icon: Users,
            label: "Retailers",
            description: "Manage retailer network",
            href: "/retailers",
            testId: "action-retailers"
          }
        ];
      case 'manufacturer':
        return [
          {
            icon: Plus,
            label: "Add Product",
            description: "Create new product",
            href: "/products",
            testId: "action-add-product"
          },
          {
            icon: Package,
            label: "Production",
            description: "Track production",
            href: "/production",
            testId: "action-production"
          },
          {
            icon: Users,
            label: "Distributors",
            description: "Manage distribution network",
            href: "/distributors",
            testId: "action-distributors"
          }
        ];
      default:
        return [
          {
            icon: Users,
            label: "Manage Users",
            description: "User administration",
            href: "/admin/users",
            testId: "action-manage-users"
          },
          {
            icon: FileText,
            label: "System Reports",
            description: "View system reports",
            href: "/admin/reports",
            testId: "action-system-reports"
          },
          {
            icon: Package,
            label: "Platform Overview",
            description: "Monitor platform health",
            href: "/admin",
            testId: "action-platform-overview"
          }
        ];
    }
  };

  const actions = getActionsForRole();

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {actions.map((action, index) => {
            const Icon = action.icon;
            return (
              <Button
                key={index}
                variant="outline"
                className="w-full justify-start h-auto p-4"
                data-testid={action.testId}
                onClick={() => {
                  setLocation(action.href);
                }}
              >
                <div className="flex items-center space-x-3 text-left">
                  <Icon className="h-5 w-5 text-primary flex-shrink-0" />
                  <div>
                    <div className="font-medium">{action.label}</div>
                    <div className="text-xs text-gray-500">{action.description}</div>
                  </div>
                </div>
              </Button>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}