import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Clock, Eye } from "lucide-react";

export default function RecentOrders() {
  const { data: orders, isLoading } = useQuery({
    queryKey: ["api", "orders"],
  });

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Recent Orders</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="space-y-2 flex-1">
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                    <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                  </div>
                  <div className="h-6 bg-gray-200 rounded w-16"></div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  const mockOrders = [
    {
      id: "ORD-001",
      customer: "Tech Retailer Co",
      items: 5,
      total: 2449.95,
      status: "pending",
      date: "2024-01-15T10:30:00Z"
    },
    {
      id: "ORD-002", 
      customer: "Office Supply Plus",
      items: 12,
      total: 1299.50,
      status: "confirmed",
      date: "2024-01-15T09:15:00Z"
    },
    {
      id: "ORD-003",
      customer: "Modern Furniture Ltd",
      items: 3,
      total: 899.99,
      status: "shipped",
      date: "2024-01-14T16:45:00Z"
    },
    {
      id: "ORD-004",
      customer: "Fashion Forward",
      items: 8,
      total: 679.92,
      status: "delivered",
      date: "2024-01-14T14:20:00Z"
    }
  ];

  const recentOrders = Array.isArray(orders) ? orders.slice(0, 5) : mockOrders;

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'confirmed':
        return 'bg-blue-100 text-blue-800';
      case 'shipped':
        return 'bg-purple-100 text-purple-800';
      case 'delivered':
        return 'bg-green-100 text-green-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Clock className="h-5 w-5 text-primary mr-2" />
          Recent Orders
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recentOrders.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Clock className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>No recent orders found</p>
            </div>
          ) : (
            recentOrders.slice(0, 4).map((order: any) => (
              <div key={order.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors" data-testid={`order-${order.id}`}>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900" data-testid={`order-id-${order.id}`}>
                      {order.id}
                    </h4>
                    <Badge className={getStatusColor(order.status)} data-testid={`order-status-${order.id}`}>
                      {order.status.charAt(0).toUpperCase() + order.status.slice(1)}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-1" data-testid={`order-customer-${order.id}`}>
                    {order.customer}
                  </p>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{order.items} items</span>
                    <span className="font-medium">${order.total.toLocaleString()}</span>
                    <span>{formatDate(order.date)}</span>
                  </div>
                </div>
                <Button variant="ghost" size="sm" className="ml-4" data-testid={`button-view-order-${order.id}`}>
                  <Eye className="h-4 w-4" />
                </Button>
              </div>
            ))
          )}
        </div>
        {recentOrders.length > 4 && (
          <div className="mt-4 text-center">
            <Button variant="outline" size="sm" data-testid="button-view-all-orders">
              View All Orders
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}