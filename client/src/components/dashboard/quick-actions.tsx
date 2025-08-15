import { useLocation } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Package, Users, ShoppingCart, FileText, Building2 } from "lucide-react";

interface QuickActionsProps {
  userRole: string;
}

export default function QuickActions({ userRole }: QuickActionsProps) {
  const [, setLocation] = useLocation();
  
  const navigate = (path: string) => {
    setLocation(path);
  };

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
            label: "Orders from Distributors",
            description: "View distributor orders",
            href: "/orders",
            testId: "action-distributor-orders"
          },
          {
            icon: Users,
            label: "Assigned Distributors",
            description: "Manage distribution network",
            href: "/partners",
            testId: "action-assigned-distributors"
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
        <CardTitle className="flex items-center gap-2">
          <div className="w-8 h-8 auromart-gradient-accent rounded-lg flex items-center justify-center">
            <Plus className="h-4 w-4 text-white" />
          </div>
          Quick Actions
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {actions.map((action, index) => (
            <Button
              key={index}
              variant="outline"
              className="w-full justify-start h-auto p-3"
              onClick={() => navigate(action.href)}
              data-testid={action.testId}
            >
              <div className="flex items-center gap-3">
                <action.icon className="h-5 w-5 text-gray-600" />
                <div className="text-left">
                  <div className="font-medium text-sm">{action.label}</div>
                  <div className="text-xs text-gray-500">{action.description}</div>
                </div>
              </div>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}