import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Clock, Eye, AlertTriangle } from "lucide-react";
import { getQueryFn } from "@/lib/queryClient";

interface OrderItem {
  id: string;
  productId: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  product?: {
    name: string;
    sku?: string;
  };
}

interface Order {
  id: string;
  orderNumber: string;
  retailerId: string;
  distributorId: string;
  status: string;
  deliveryMode: string;
  totalAmount: number;
  notes?: string;
  createdAt: string;
  updatedAt: string;
  items: OrderItem[];
  retailer?: {
    firstName: string;
    lastName: string;
    email: string;
  };
  distributor?: {
    firstName: string;
    lastName: string;
    email: string;
  };
}

export default function RecentOrders() {
  const { data: orders, isLoading, error } = useQuery({
    queryKey: ["api", "orders"],
    queryFn: getQueryFn({ on401: "throw" }),
    retry: 1,
    refetchOnWindowFocus: false,
  });

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'confirmed':
      case 'accepted':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'packed':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'dispatched':
      case 'out_for_delivery':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'delivered':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'cancelled':
      case 'rejected':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatStatusDisplay = (status: string) => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-IN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return 'Invalid Date';
    }
  };

  const formatCurrency = (amount: number) => {
    try {
      return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
      }).format(amount);
    } catch (error) {
      return `₹${amount}`;
    }
  };

  const getCustomerName = (order: Order) => {
    if (order.retailer) {
      return `${order.retailer.firstName} ${order.retailer.lastName}`;
    }
    if (order.distributor) {
      return `${order.distributor.firstName} ${order.distributor.lastName}`;
    }
    return 'Customer';
  };

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

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Clock className="h-5 w-5 text-primary mr-2" />
            Recent Orders
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <AlertTriangle className="h-12 w-12 mx-auto mb-4 text-orange-400" />
            <p className="text-gray-600 mb-2">Failed to load recent orders</p>
            <p className="text-sm text-gray-500">
              {error instanceof Error ? error.message : 'An unexpected error occurred'}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const recentOrders = Array.isArray(orders) ? (orders as Order[]).slice(0, 5) : [];

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
            recentOrders.slice(0, 4).map((order) => (
              <div key={order.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors" data-testid={`order-${order.id}`}>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900" data-testid={`order-id-${order.id}`}>
                      {order.orderNumber}
                    </h4>
                    <Badge className={`${getStatusColor(order.status)} border`} data-testid={`order-status-${order.id}`}>
                      {formatStatusDisplay(order.status)}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mb-1" data-testid={`order-customer-${order.id}`}>
                    {getCustomerName(order)}
                  </p>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>{order.items?.length || 0} items</span>
                    <span className="font-medium">{formatCurrency(order.totalAmount || 0)}</span>
                    <span>{formatDate(order.createdAt)}</span>
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
            <Button 
              variant="outline" 
              size="sm" 
              data-testid="button-view-all-orders"
              onClick={() => window.location.href = '/orders'}
            >
              View All Orders
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}