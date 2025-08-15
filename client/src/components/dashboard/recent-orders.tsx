import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Package, 
  Truck, 
  Check, 
  X, 
  XCircle,
  Eye,
  TrendingUp,
  DollarSign,
  Calendar
} from "lucide-react";
import { getQueryFn } from "@/lib/queryClient";
import { useAuth } from "@/hooks/useAuth";
import { Link } from "wouter";

interface OrderItem {
  id: string;
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
}

interface Order {
  id: string;
  orderNumber: string;
  status: string;
  totalAmount: number;
  createdAt: string;
  updatedAt: string;
  items: OrderItem[];
  distributor?: {
    id: string;
    businessName: string;
    firstName: string;
    lastName: string;
  };
  retailer?: {
    id: string;
    businessName: string;
    firstName: string;
    lastName: string;
  };
}

export default function RecentOrders() {
  const { user } = useAuth();
  const userRole = (user as any)?.role || 'retailer';

  const { data: orders, isLoading, error } = useQuery<Order[]>({
    queryKey: ["api", "orders"],
    queryFn: getQueryFn({ on401: "throw" }),
    retry: 1,
    refetchOnWindowFocus: false,
  });

  // For manufacturers, filter orders from distributors only
  const filteredOrders = userRole === 'manufacturer' 
    ? orders?.filter(order => order.distributor) || []
    : orders || [];

  // Sort by most recent first
  const sortedOrders = filteredOrders.sort((a, b) => 
    new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  ).slice(0, 5); // Show only 5 most recent orders

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'confirmed':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'accepted':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'processing':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'packed':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'shipped':
        return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      case 'out_for_delivery':
        return 'bg-pink-100 text-pink-800 border-pink-200';
      case 'delivered':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'cancelled':
      case 'rejected':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending': return <Clock className="h-4 w-4" />;
      case 'confirmed': return <CheckCircle className="h-4 w-4" />;
      case 'accepted': return <CheckCircle className="h-4 w-4" />;
      case 'processing': return <AlertCircle className="h-4 w-4" />;
      case 'packed': return <Package className="h-4 w-4" />;
      case 'shipped': return <Truck className="h-4 w-4" />;
      case 'out_for_delivery': return <Truck className="h-4 w-4" />;
      case 'delivered': return <Check className="h-4 w-4" />;
      case 'cancelled': return <X className="h-4 w-4" />;
      case 'rejected': return <XCircle className="h-4 w-4" />;
      default: return <Package className="h-4 w-4" />;
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
      return 'Invalid date';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            Recent Orders
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
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
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            Recent Orders
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">
            <p className="text-sm text-red-600">Failed to load orders</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            Recent Orders
            {userRole === 'manufacturer' && (
              <span className="text-sm text-gray-500">(from Distributors)</span>
            )}
          </CardTitle>
          <Link href="/orders">
            <Button variant="outline" size="sm">
              View All
            </Button>
          </Link>
        </div>
      </CardHeader>
      <CardContent>
        {sortedOrders.length === 0 ? (
          <div className="text-center py-6">
            <Package className="h-8 w-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-500">
              {userRole === 'manufacturer' 
                ? "No orders from distributors yet" 
                : "No recent orders"
              }
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {sortedOrders.map((order) => (
              <div key={order.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-sm">#{order.orderNumber}</span>
                    <Badge className={`text-xs ${getStatusColor(order.status)}`}>
                      {getStatusIcon(order.status)}
                      {formatStatusDisplay(order.status)}
                    </Badge>
                  </div>
                  <div className="text-sm text-gray-600">
                    {userRole === 'manufacturer' && order.distributor ? (
                      <span>From: {order.distributor.businessName || `${order.distributor.firstName} ${order.distributor.lastName}`}</span>
                    ) : userRole === 'distributor' && order.retailer ? (
                      <span>To: {order.retailer.businessName || `${order.retailer.firstName} ${order.retailer.lastName}`}</span>
                    ) : (
                      <span>{order.items?.length || 0} items</span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500">
                    {formatDate(order.createdAt)}
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-sm">
                    {formatCurrency(order.totalAmount)}
                  </div>
                  <div className="text-xs text-gray-500">
                    {order.items?.length || 0} items
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}