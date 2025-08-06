import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import Header from "@/components/layout/header";
import MobileNav from "@/components/layout/mobile-nav";
import OrderStatus from "@/components/orders/order-status"; 
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Package, Download, MessageCircle, Eye, AlertCircle, RefreshCw } from "lucide-react";
import { useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
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
}

export default function Orders() {
  const { user, isLoading } = useAuth();
  const { toast } = useToast();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !user) {
      toast({
        title: "Unauthorized",
        description: "You are logged out. Logging in again...",
        variant: "destructive",
      });
      setTimeout(() => {
        window.location.href = "/";
      }, 500);
      return;
    }
  }, [user, isLoading, toast]);

  const { data: orders, isLoading: ordersLoading, error: ordersError, refetch } = useQuery({
    queryKey: ["api", "orders"],
    queryFn: getQueryFn({ on401: "throw" }),
    enabled: !!user,
    retry: 1,
    refetchOnWindowFocus: false,
  });

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'pending':
        return 'status-pending';
      case 'confirmed':
      case 'accepted':
        return 'status-confirmed';
      case 'packed':
        return 'status-packed';
      case 'dispatched':
      case 'out_for_delivery':
        return 'status-out-for-delivery';
      case 'delivered':
        return 'status-delivered';
      case 'cancelled':
      case 'rejected':
        return 'status-cancelled';
      default:
        return 'status-pending';
    }
  };

  const formatStatusDisplay = (status: string) => {
    return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-IN', {
        year: 'numeric',
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
        currency: 'INR'
      }).format(amount);
    } catch (error) {
      return `₹${amount}`;
    }
  };

  if (isLoading || !user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading orders...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900" data-testid="text-page-title">
                Order Management
              </h1>
              <p className="text-gray-600 mt-1">
                {user.role === 'retailer' ? 'Track your orders and download invoices' : 'Manage and process incoming orders'}
              </p>
            </div>
            {ordersError && (
              <Button
                onClick={() => refetch()}
                variant="outline"
                size="sm"
                className="flex items-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Retry
              </Button>
            )}
          </div>
        </div>

        {/* Error State */}
        {ordersError && (
          <Card className="mb-6 border-red-200 bg-red-50">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <AlertCircle className="h-5 w-5 text-red-500" />
                <div>
                  <p className="text-red-800 font-medium">Failed to load orders</p>
                  <p className="text-red-600 text-sm">
                    {ordersError instanceof Error ? ordersError.message : 'An unexpected error occurred'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {ordersLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="h-3 bg-gray-200 rounded"></div>
                    <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                    <div className="flex gap-2 pt-2">
                      <div className="h-8 bg-gray-200 rounded w-20"></div>
                      <div className="h-8 bg-gray-200 rounded w-24"></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : orders && Array.isArray(orders) && orders.length > 0 ? (
          <div className="space-y-6">
            {(orders as Order[]).map((order) => (
              <Card key={order.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-semibold">{order.orderNumber}</h3>
                      <p className="text-sm text-gray-600">
                        {formatDate(order.createdAt)}
                      </p>
                      {order.deliveryMode && (
                        <p className="text-xs text-gray-500 mt-1">
                          Delivery: {order.deliveryMode.charAt(0).toUpperCase() + order.deliveryMode.slice(1)}
                        </p>
                      )}
                    </div>
                    <Badge className={getStatusBadgeClass(order.status)}>
                      {formatStatusDisplay(order.status)}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex justify-between text-sm">
                      <span>Total Amount:</span>
                      <span className="font-semibold">{formatCurrency(order.totalAmount || 0)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Items:</span>
                      <span>{order.items?.length || 0} items</span>
                    </div>
                    {order.notes && (
                      <div className="text-sm">
                        <span className="text-gray-600">Notes:</span>
                        <p className="text-gray-800 mt-1">{order.notes}</p>
                      </div>
                    )}
                    
                    {/* Order Items Preview */}
                    {order.items && order.items.length > 0 && (
                      <div className="border-t pt-3">
                        <p className="text-sm font-medium mb-2">Items:</p>
                        <div className="space-y-1">
                          {order.items.slice(0, 3).map((item) => (
                            <div key={item.id} className="flex justify-between text-xs text-gray-600">
                              <span>{item.product?.name || `Product ${item.productId.slice(0, 8)}`}</span>
                              <span>{item.quantity}x {formatCurrency(item.unitPrice)}</span>
                            </div>
                          ))}
                          {order.items.length > 3 && (
                            <p className="text-xs text-gray-500">+{order.items.length - 3} more items</p>
                          )}
                        </div>
                      </div>
                    )}
                    
                    <div className="flex gap-2 pt-2">
                      <Button size="sm" variant="outline">
                        <Eye className="h-4 w-4 mr-1" />
                        View Details
                      </Button>
                      {order.status === 'delivered' && (
                        <Button size="sm" variant="outline">
                          <Download className="h-4 w-4 mr-1" />
                          Download Invoice
                        </Button>
                      )}
                      <Button size="sm" variant="outline">
                        <MessageCircle className="h-4 w-4 mr-1" />
                        Contact
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Orders Found</h3>
            <p className="text-gray-600 mb-4">
              {user.role === 'retailer' 
                ? "You haven't placed any orders yet." 
                : "No orders have been assigned to you yet."}
            </p>
            {user.role === 'retailer' && (
              <Button variant="outline" onClick={() => window.location.href = '/products'}>
                Browse Products
              </Button>
            )}
          </div>
        )}
      </div>
      
      <MobileNav />
    </div>
  );
}
