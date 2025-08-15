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

  const getActionsForRole = (role: string) => {
    switch (role) {
      case 'manufacturer':
        return [
          {
            title: 'Add Product',
            description: 'Create a new product in your catalog',
            icon: Plus,
            href: '/products',
            color: 'bg-blue-500 hover:bg-blue-600'
          },
          {
            title: 'Orders from Distributors',
            description: 'View orders placed by distributors',
            icon: Package,
            href: '/orders',
            color: 'bg-green-500 hover:bg-green-600'
          },
          {
            title: 'Assigned Distributors',
            description: 'Manage your distributor partnerships',
            icon: Users,
            href: '/partners',
            color: 'bg-purple-500 hover:bg-purple-600'
          }
        ];
      case 'distributor':
        return [
          {
            title: 'Add Product',
            description: 'Add products to your inventory',
            icon: Plus,
            href: '/products',
            color: 'bg-blue-500 hover:bg-blue-600'
          },
          {
            title: 'Orders from Retailers',
            description: 'View orders placed by retailers',
            icon: Package,
            href: '/orders',
            color: 'bg-green-500 hover:bg-green-600'
          },
          {
            title: 'Assigned Partners',
            description: 'Manage manufacturers and retailers',
            icon: Users,
            href: '/partners',
            color: 'bg-purple-500 hover:bg-purple-600'
          }
        ];
      case 'retailer':
        return [
          {
            title: 'New Order',
            description: 'Place a new order with suppliers',
            icon: Plus,
            href: '/products',
            color: 'bg-blue-500 hover:bg-blue-600'
          },
          {
            title: 'View Invoices',
            description: 'Check your order invoices',
            icon: FileText,
            href: '/orders',
            color: 'bg-green-500 hover:bg-green-600'
          },
          {
            title: 'Suppliers',
            description: 'Manage your supplier partnerships',
            icon: Users,
            href: '/partners',
            color: 'bg-purple-500 hover:bg-purple-600'
          }
        ];
      default:
        return [];
    }
  };

  const actions = getActionsForRole(userRole);

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
            >
              <div className="flex items-center gap-3">
                <action.icon className="h-5 w-5 text-gray-600" />
                <div className="text-left">
                  <div className="font-medium text-sm">{action.title}</div>
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