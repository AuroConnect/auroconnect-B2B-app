import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import Header from "@/components/layout/header";
import MobileNav from "@/components/layout/mobile-nav";
import OrderStatus from "@/components/orders/order-status"; 
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Package, Download, MessageCircle } from "lucide-react";
import { useEffect } from "react";
import { useToast } from "@/hooks/use-toast";

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
        window.location.href = "/api/login";
      }, 500);
      return;
    }
  }, [user, isLoading, toast]);

  const { data: orders, isLoading: ordersLoading } = useQuery({
    queryKey: ["/api/orders"],
    enabled: !!user,
  });

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'pending':
        return 'status-pending';
      case 'confirmed':
        return 'status-confirmed';
      case 'packed':
        return 'status-packed';
      case 'out_for_delivery':
        return 'status-out-for-delivery';
      case 'delivered':
        return 'status-delivered';
      case 'cancelled':
        return 'status-cancelled';
      default:
        return 'status-pending';
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
          <h1 className="text-2xl font-bold text-gray-900" data-testid="text-page-title">
            Order Management
          </h1>
          <p className="text-gray-600 mt-1">
            {user.role === 'retailer' ? 'Track your orders and download invoices' : 'Manage and process incoming orders'}
          </p>
        </div>

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
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : orders && orders.length > 0 ? (
          <div className="space-y-6">
            {orders.map((order: any) => (
              <Card key={order.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2" data-testid={`text-order-number-${order.id}`}>
                        <Package className="h-5 w-5" />
                        {order.orderNumber}
                      </CardTitle>
                      <p className="text-sm text-gray-600 mt-1">
                        {new Date(order.createdAt).toLocaleDateString('en-IN', {
                          year: 'numeric',
                          month: 'long', 
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                    <Badge className={getStatusBadgeClass(order.status)} data-testid={`badge-order-status-${order.id}`}>
                      {order.status.replace('_', ' ').toUpperCase()}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Order Details</h4>
                      <div className="space-y-1 text-sm text-gray-600">
                        <p><strong>Total Amount:</strong> ₹{order.totalAmount}</p>
                        <p><strong>Delivery Mode:</strong> {order.deliveryMode === 'pickup' ? 'Self Pickup' : 'Home Delivery'}</p>
                        {order.notes && <p><strong>Notes:</strong> {order.notes}</p>}
                      </div>
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">Order Status</h4>
                      <OrderStatus status={order.status} />
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap gap-2 mt-6">
                    <Button variant="outline" size="sm" data-testid={`button-view-details-${order.id}`}>
                      View Details
                    </Button>
                    <Button variant="outline" size="sm" data-testid={`button-download-invoice-${order.id}`}>
                      <Download className="h-4 w-4 mr-1" />
                      Invoice
                    </Button>
                    <Button variant="outline" size="sm" className="whatsapp-green text-white hover:bg-green-600" data-testid={`button-whatsapp-${order.id}`}>
                      <MessageCircle className="h-4 w-4 mr-1" />
                      WhatsApp
                    </Button>
                    {user.role === 'distributor' && order.status === 'pending' && (
                      <>
                        <Button size="sm" className="action-button-secondary" data-testid={`button-approve-${order.id}`}>
                          Approve
                        </Button>
                        <Button size="sm" variant="destructive" data-testid={`button-reject-${order.id}`}>
                          Reject
                        </Button>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <CardContent className="text-center py-12">
              <Package className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Orders Found</h3>
              <p className="text-gray-600 mb-6">
                {user.role === 'retailer' 
                  ? "You haven't placed any orders yet. Browse products to get started."
                  : "No orders to process at the moment."
                }
              </p>
              {user.role === 'retailer' && (
                <Button className="action-button-primary" data-testid="button-browse-products">
                  Browse Products
                </Button>
              )}
            </CardContent>
          </Card>
        )}
      </div>

      <MobileNav />
    </div>
  );
}
