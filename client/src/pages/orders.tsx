import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";
import Header from "@/components/layout/header";
import MobileNav from "@/components/layout/mobile-nav";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { 
  Search, 
  Filter, 
  Eye, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Truck, 
  Package, 
  Check, 
  X,
  History,
  Calendar,
  DollarSign,
  Users
} from "lucide-react";
import OrderStatus from "@/components/orders/order-status";

interface Order {
  id: string;
  orderNumber: string;
  status: string;
  totalAmount: number;
  createdAt: string;
  updatedAt: string;
  notes?: string;
  retailer?: {
    id: string;
    name: string;
    email: string;
    phone: string;
    businessName?: string;
    firstName?: string;
    lastName?: string;
  };
  distributor?: {
    id: string;
    name: string;
    email: string;
    phone: string;
    businessName?: string;
    firstName?: string;
    lastName?: string;
  };
  items?: Array<{
    id: string;
    productId: string;
    productName: string;
    quantity: number;
    unitPrice: number;
    totalPrice: number;
  }>;
  statusHistory?: Array<{
    status: string;
    timestamp: string;
    notes?: string;
    updatedBy?: string;
  }>;
}

export default function Orders() {
  const { user, isLoading, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [isOrderDetailsOpen, setIsOrderDetailsOpen] = useState(false);
  const [isStatusUpdateOpen, setIsStatusUpdateOpen] = useState(false);
  const [newStatus, setNewStatus] = useState("");
  const [statusNotes, setStatusNotes] = useState("");
  const [showStatusHistory, setShowStatusHistory] = useState(false);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
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
  }, [isAuthenticated, isLoading, toast]);

  // Fetch orders
  const { data: orders = [], isLoading: ordersLoading, error: ordersError } = useQuery<Order[]>({
    queryKey: ["api", "orders", statusFilter],
    enabled: !!isAuthenticated && !!user,
    retry: 3,
    staleTime: 30000,
  });

  // Update order status mutation
  const updateStatusMutation = useMutation({
    mutationFn: async ({ orderId, status, notes }: { orderId: string; status: string; notes?: string }) => {
      const response = await apiRequest("PUT", `/api/orders/${orderId}/status`, { status, notes });
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Status Updated",
        description: `Order status updated to ${data.newStatus} successfully.`,
      });
      queryClient.invalidateQueries({ queryKey: ["api", "orders"] });
      setIsStatusUpdateOpen(false);
      setNewStatus("");
      setStatusNotes("");
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to update order status.",
        variant: "destructive",
      });
    },
  });

  // Filter orders based on search term
  const filteredOrders = orders.filter((order) =>
    order.orderNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.retailer?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.distributor?.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.distributor?.businessName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.retailer?.businessName?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusIcon = (status: string) => {
    switch (status) {
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'confirmed': return 'bg-blue-100 text-blue-800';
      case 'accepted': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-orange-100 text-orange-800';
      case 'packed': return 'bg-purple-100 text-purple-800';
      case 'shipped': return 'bg-indigo-100 text-indigo-800';
      case 'out_for_delivery': return 'bg-pink-100 text-pink-800';
      case 'delivered': return 'bg-emerald-100 text-emerald-800';
      case 'cancelled': return 'bg-gray-100 text-gray-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const handleStatusUpdate = () => {
    if (!selectedOrder || !newStatus) {
      toast({
        title: "Missing Information",
        description: "Please select a status to update.",
        variant: "destructive",
      });
      return;
    }

    updateStatusMutation.mutate({
      orderId: selectedOrder.id,
      status: newStatus,
      notes: statusNotes
    });
  };

  const canUpdateStatus = (order: Order) => {
    if (!user) return false;
    return user.role === 'distributor' || user.role === 'manufacturer';
  };

  const getNextStatusOptions = (currentStatus: string) => {
    const statusFlow = {
      'pending': ['confirmed', 'accepted', 'rejected', 'cancelled'],
      'confirmed': ['accepted', 'processing', 'rejected', 'cancelled'],
      'accepted': ['processing', 'packed', 'rejected', 'cancelled'],
      'processing': ['packed', 'shipped', 'rejected', 'cancelled'],
      'packed': ['shipped', 'out_for_delivery', 'rejected', 'cancelled'],
      'shipped': ['out_for_delivery', 'delivered', 'rejected', 'cancelled'],
      'out_for_delivery': ['delivered', 'rejected', 'cancelled'],
      'delivered': [],
      'rejected': [],
      'cancelled': []
    };
    return statusFlow[currentStatus] || [];
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading || !isAuthenticated || !user) {
    return (
      <div className="min-h-screen auromart-gradient-bg flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading orders...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header />
      
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Orders</h1>
          <p className="text-gray-600">Manage and track your orders</p>
        </div>

        {/* Search and Filter */}
        <Card className="mb-6">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search orders by number, retailer, or distributor..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
              
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full md:w-48">
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent className="bg-white border border-gray-200 shadow-lg">
                  <SelectItem value="all">All Statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="confirmed">Confirmed</SelectItem>
                  <SelectItem value="accepted">Accepted</SelectItem>
                  <SelectItem value="processing">Processing</SelectItem>
                  <SelectItem value="packed">Packed</SelectItem>
                  <SelectItem value="shipped">Shipped</SelectItem>
                  <SelectItem value="out_for_delivery">Out for Delivery</SelectItem>
                  <SelectItem value="delivered">Delivered</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Orders List */}
        <div className="space-y-4">
          {ordersLoading ? (
            <div className="text-center py-8">
              <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
              <p className="text-gray-600">Loading orders...</p>
            </div>
          ) : ordersError ? (
            <div className="text-center py-8">
              <p className="text-red-600">Failed to load orders</p>
            </div>
          ) : filteredOrders.length === 0 ? (
            <div className="text-center py-8">
              <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No orders found</p>
            </div>
          ) : (
            filteredOrders.map((order) => (
              <Card key={order.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-semibold text-lg">{order.orderNumber}</h3>
                        <Badge className={getStatusColor(order.status)}>
                          <div className="flex items-center gap-1">
                            {getStatusIcon(order.status)}
                            {order.status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </div>
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600 mb-3">
                        <div className="flex items-center gap-2">
                          <DollarSign className="h-4 w-4" />
                          <span>{formatCurrency(order.totalAmount)}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4" />
                          <span>{formatDate(order.createdAt)}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <History className="h-4 w-4" />
                          <span>Updated: {formatDate(order.updatedAt)}</span>
                        </div>
                      </div>
                      
                      {/* Show distributor/retailer information based on user role */}
                      {user.role === 'manufacturer' && order.distributor && (
                        <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                          <Users className="h-4 w-4" />
                          <span>Distributor: {order.distributor.businessName || `${order.distributor.firstName} ${order.distributor.lastName}`}</span>
                        </div>
                      )}
                      
                      {user.role === 'distributor' && order.retailer && (
                        <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                          <Users className="h-4 w-4" />
                          <span>Retailer: {order.retailer.businessName || `${order.retailer.firstName} ${order.retailer.lastName}`}</span>
                        </div>
                      )}
                      
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <span>Created: {formatDate(order.createdAt)}</span>
                        <span>•</span>
                        <span>Updated: {formatDate(order.updatedAt)}</span>
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedOrder(order);
                          setIsOrderDetailsOpen(true);
                        }}
                      >
                        <Eye className="h-4 w-4 mr-1" />
                        View Details
                      </Button>
                      
                      {canUpdateStatus(order) && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setSelectedOrder(order);
                            setIsStatusUpdateOpen(true);
                          }}
                        >
                          Update Status
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>

      {/* Order Details Dialog */}
      <Dialog open={isOrderDetailsOpen} onOpenChange={setIsOrderDetailsOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Order Details - {selectedOrder?.orderNumber}</DialogTitle>
            <DialogDescription>
              Complete order information and status tracking
            </DialogDescription>
          </DialogHeader>
          
          {selectedOrder && (
            <div className="space-y-6">
              {/* Order Summary */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold mb-2">Order Information</h4>
                  <div className="space-y-2 text-sm">
                    <div><span className="font-medium">Order Number:</span> {selectedOrder.orderNumber}</div>
                    <div><span className="font-medium">Total Amount:</span> {formatCurrency(selectedOrder.totalAmount)}</div>
                    <div><span className="font-medium">Created:</span> {formatDate(selectedOrder.createdAt)}</div>
                    <div><span className="font-medium">Last Updated:</span> {formatDate(selectedOrder.updatedAt)}</div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Partners</h4>
                  <div className="space-y-2 text-sm">
                    {selectedOrder.retailer && (
                      <div>
                        <span className="font-medium">Retailer:</span> {selectedOrder.retailer.name}
                      </div>
                    )}
                    {selectedOrder.distributor && (
                      <div>
                        <span className="font-medium">Distributor:</span> {selectedOrder.distributor.name}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Order Status */}
              <div>
                <h4 className="font-semibold mb-3">Order Status</h4>
                <OrderStatus 
                  status={selectedOrder.status} 
                  statusHistory={selectedOrder.statusHistory}
                  showHistory={true}
                />
              </div>

              {/* Order Items */}
              {selectedOrder.items && selectedOrder.items.length > 0 && (
                <div>
                  <h4 className="font-semibold mb-3">Order Items</h4>
                  <div className="space-y-3">
                    {selectedOrder.items.map((item) => (
                      <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <div className="font-medium">{item.productName}</div>
                          <div className="text-sm text-gray-600">Qty: {item.quantity}</div>
                        </div>
                        <div className="text-right">
                          <div className="font-medium">{formatCurrency(item.unitPrice)} each</div>
                          <div className="text-sm text-gray-600">{formatCurrency(item.totalPrice)}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Notes */}
              {selectedOrder.notes && (
                <div>
                  <h4 className="font-semibold mb-3">Notes</h4>
                  <div className="p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm whitespace-pre-wrap">{selectedOrder.notes}</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Status Update Dialog */}
      <Dialog open={isStatusUpdateOpen} onOpenChange={setIsStatusUpdateOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Update Order Status</DialogTitle>
            <DialogDescription>
              Update the status of order {selectedOrder?.orderNumber}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="status">New Status</Label>
              <Select value={newStatus} onValueChange={setNewStatus}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select new status" />
                </SelectTrigger>
                <SelectContent>
                  {selectedOrder && getNextStatusOptions(selectedOrder.status).map((status) => (
                    <SelectItem key={status} value={status}>
                      {status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="notes">Notes (Optional)</Label>
              <Textarea
                id="notes"
                value={statusNotes}
                onChange={(e) => setStatusNotes(e.target.value)}
                placeholder="Add any notes about this status update..."
                className="min-h-[100px]"
              />
            </div>
          </div>
          
          <div className="flex justify-end gap-3 pt-6 border-t">
            <Button 
              variant="outline" 
              onClick={() => setIsStatusUpdateOpen(false)}
            >
              Cancel
            </Button>
            <Button 
              onClick={handleStatusUpdate}
              disabled={updateStatusMutation.isPending || !newStatus}
            >
              {updateStatusMutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Updating...
                </>
              ) : (
                "Update Status"
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
      
      <MobileNav />
    </div>
  );
}
