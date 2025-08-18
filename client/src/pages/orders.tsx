import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";
import Header from "@/components/layout/header";
import MobileNav from "@/components/layout/mobile-nav";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { 
  Search, 
 
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


interface Order {
  id: string;
  order_number: string;
  status: string;
  total_amount: number;
  created_at: string;
  updated_at: string;
  notes?: string;
  retailer?: {
    id: string;
    business_name?: string;
    email: string;
    firstName?: string;
    lastName?: string;
  };
  distributor?: {
    id: string;
    business_name?: string;
    email: string;
    firstName?: string;
    lastName?: string;
  };
  items?: Array<{
    id: string;
    product_id: string;
    quantity: number;
    unit_price: number;
    total_price: number;
    product?: {
      id: string;
      name: string;
      sku: string;
      image_url?: string;
    };
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

  const [declineReason, setDeclineReason] = useState("");
  const [isDeclineDialogOpen, setIsDeclineDialogOpen] = useState(false);
  const [selectedOrderForAction, setSelectedOrderForAction] = useState<Order | null>(null);

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

  // Approve order mutation
  const approveOrderMutation = useMutation({
    mutationFn: async ({ orderId }: { orderId: string }) => {
      const response = await apiRequest("POST", `/api/orders/${orderId}/approve`);
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Order Approved",
        description: "Order has been successfully approved.",
      });
      queryClient.invalidateQueries({ queryKey: ["api", "orders"] });
      queryClient.invalidateQueries({ queryKey: ["api", "analytics", "stats"] });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to approve order.",
        variant: "destructive",
      });
    },
  });

  // Decline order mutation
  const declineOrderMutation = useMutation({
    mutationFn: async (data: { orderId: string; reason: string }) => {
      const response = await apiRequest("POST", `/api/orders/${data.orderId}/decline`, {
        reason: data.reason
      });
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Order Declined",
        description: "Order has been successfully declined.",
      });
      queryClient.invalidateQueries({ queryKey: ["api", "orders"] });
      queryClient.invalidateQueries({ queryKey: ["api", "analytics", "stats"] });
      setIsDeclineDialogOpen(false);
      setDeclineReason("");
      setSelectedOrderForAction(null);
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to decline order.",
        variant: "destructive",
      });
    },
  });

  // Filter orders based on search term
  const filteredOrders = orders.filter((order) =>
    order.order_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.retailer?.business_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.distributor?.business_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.retailer?.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    order.distributor?.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending': return <Clock className="h-4 w-4" />;
      case 'confirmed': return <CheckCircle className="h-4 w-4" />;
      case 'accepted': return <CheckCircle className="h-4 w-4" />;
      case 'approved': return <CheckCircle className="h-4 w-4" />;
      case 'processing': return <AlertCircle className="h-4 w-4" />;
      case 'packed': return <Package className="h-4 w-4" />;
      case 'shipped': return <Truck className="h-4 w-4" />;
      case 'out_for_delivery': return <Truck className="h-4 w-4" />;
      case 'delivered': return <Check className="h-4 w-4" />;
      case 'cancelled': return <X className="h-4 w-4" />;
      case 'rejected': return <XCircle className="h-4 w-4" />;
      case 'declined': return <XCircle className="h-4 w-4" />;
      default: return <Package className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'confirmed': return 'bg-blue-100 text-blue-800';
      case 'accepted': return 'bg-green-100 text-green-800';
      case 'approved': return 'bg-green-100 text-green-800';
      case 'processing': return 'bg-orange-100 text-orange-800';
      case 'packed': return 'bg-purple-100 text-purple-800';
      case 'shipped': return 'bg-indigo-100 text-indigo-800';
      case 'out_for_delivery': return 'bg-pink-100 text-pink-800';
      case 'delivered': return 'bg-emerald-100 text-emerald-800';
      case 'cancelled': return 'bg-gray-100 text-gray-800';
      case 'rejected': return 'bg-red-100 text-red-800';
      case 'declined': return 'bg-red-100 text-red-800';
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

  const handleApproveOrder = (order: Order) => {
    approveOrderMutation.mutate({ orderId: order.id });
  };

  const handleDeclineOrder = (order: Order) => {
    setSelectedOrderForAction(order);
    setIsDeclineDialogOpen(true);
  };

  const handleDeclineConfirm = () => {
    if (!selectedOrderForAction || !declineReason.trim()) {
      toast({
        title: "Missing Information",
        description: "Please provide a reason for declining the order.",
        variant: "destructive",
      });
      return;
    }

    declineOrderMutation.mutate({
      orderId: selectedOrderForAction.id,
      reason: declineReason.trim()
    });
  };

  const canApproveDecline = (order: Order) => {
    if (!user) return false;
    return user.role === 'manufacturer' && order.status === 'pending';
  };

  const canUpdateStatus = (order: Order) => {
    if (!user) return false;
    return user.role === 'distributor' || user.role === 'manufacturer';
  };

  const getNextStatusOptions = (currentStatus: string) => {
    const statusFlow = {
      'pending': ['approved', 'declined'],
      'approved': ['packed', 'shipped', 'delivered'],
      'packed': ['shipped', 'delivered'],
      'shipped': ['delivered'],
      'delivered': [],
      'declined': [],
      'cancelled': [],
      'rejected': []
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
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="packed">Packed</SelectItem>
                  <SelectItem value="shipped">Shipped</SelectItem>
                  <SelectItem value="delivered">Delivered</SelectItem>
                  <SelectItem value="declined">Declined</SelectItem>
                  <SelectItem value="cancelled">Cancelled</SelectItem>
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
                        <h3 className="font-semibold text-lg">{order.order_number}</h3>
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
                          <span>{formatCurrency(order.total_amount)}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Calendar className="h-4 w-4" />
                          <span>{formatDate(order.created_at)}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <History className="h-4 w-4" />
                          <span>Updated: {formatDate(order.updated_at)}</span>
                        </div>
                      </div>
                      
                      {/* Show distributor/retailer information based on user role */}
                      {user.role === 'manufacturer' && order.distributor && (
                        <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                          <Users className="h-4 w-4" />
                          <span>Distributor: {order.distributor.business_name || `${order.distributor.firstName} ${order.distributor.lastName}`}</span>
                        </div>
                      )}
                      
                      {user.role === 'distributor' && order.retailer && (
                        <div className="flex items-center gap-2 text-sm text-gray-500 mb-2">
                          <Users className="h-4 w-4" />
                          <span>Retailer: {order.retailer.business_name || `${order.retailer.firstName} ${order.retailer.lastName}`}</span>
                        </div>
                      )}
                      
                      <div className="flex items-center gap-2 text-sm text-gray-500">
                        <span>Created: {formatDate(order.created_at)}</span>
                        <span>•</span>
                        <span>Updated: {formatDate(order.updated_at)}</span>
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
                      
                      {canApproveDecline(order) && (
                        <>
                          <Button
                            variant="default"
                            size="sm"
                            onClick={() => handleApproveOrder(order)}
                            disabled={approveOrderMutation.isPending}
                            className="bg-green-600 hover:bg-green-700"
                          >
                            {approveOrderMutation.isPending ? (
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-1"></div>
                            ) : (
                              <CheckCircle className="h-4 w-4 mr-1" />
                            )}
                            Approve
                          </Button>
                          
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => handleDeclineOrder(order)}
                            disabled={declineOrderMutation.isPending}
                          >
                            {declineOrderMutation.isPending ? (
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-1"></div>
                            ) : (
                              <XCircle className="h-4 w-4 mr-1" />
                            )}
                            Decline
                          </Button>
                        </>
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
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Order Details</DialogTitle>
            <DialogDescription>
              Detailed information about order {selectedOrder?.order_number}
            </DialogDescription>
          </DialogHeader>
          
          {selectedOrder && (
            <div className="space-y-6">
              {/* Order Header */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <h3 className="font-semibold text-lg mb-2">Order Information</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Order Number:</span>
                      <span className="font-medium">{selectedOrder.order_number}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Status:</span>
                      <Badge className={getStatusColor(selectedOrder.status)}>
                        {selectedOrder.status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total Amount:</span>
                      <span className="font-medium">{formatCurrency(selectedOrder.total_amount)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Created:</span>
                      <span>{formatDate(selectedOrder.created_at)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Updated:</span>
                      <span>{formatDate(selectedOrder.updated_at)}</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h3 className="font-semibold text-lg mb-2">Customer Information</h3>
                  <div className="space-y-2 text-sm">
                    {user?.role === 'manufacturer' && selectedOrder.distributor && (
                      <>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Distributor:</span>
                          <span className="font-medium">
                            {selectedOrder.distributor.business_name || 
                             `${selectedOrder.distributor.firstName} ${selectedOrder.distributor.lastName}`}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Email:</span>
                          <span>{selectedOrder.distributor.email}</span>
                        </div>
                      </>
                    )}
                    
                    {user?.role === 'distributor' && selectedOrder.retailer && (
                      <>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Retailer:</span>
                          <span className="font-medium">
                            {selectedOrder.retailer.business_name || 
                             `${selectedOrder.retailer.firstName} ${selectedOrder.retailer.lastName}`}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Email:</span>
                          <span>{selectedOrder.retailer.email}</span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>

              {/* Order Items */}
              <div>
                <h3 className="font-semibold text-lg mb-4">Order Items</h3>
                <div className="space-y-3">
                  {selectedOrder.items?.map((item) => (
                    <div key={item.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                          {item.product?.image_url ? (
                            <img 
                              src={item.product.image_url} 
                              alt={item.product.name}
                              className="w-full h-full object-cover rounded-lg"
                            />
                          ) : (
                            <Package className="h-6 w-6 text-gray-400" />
                          )}
                        </div>
                        <div>
                          <h4 className="font-medium">{item.product?.name || 'Product'}</h4>
                          <p className="text-sm text-gray-600">SKU: {item.product?.sku || 'N/A'}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-medium">{item.quantity} x {formatCurrency(item.unit_price)}</div>
                        <div className="text-sm text-gray-600">{formatCurrency(item.total_price)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Notes */}
              {selectedOrder.notes && (
                <div>
                  <h3 className="font-semibold text-lg mb-2">Order Notes</h3>
                  <div className="p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-700">{selectedOrder.notes}</p>
                  </div>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4 border-t">
                <Button
                  variant="outline"
                  onClick={() => setIsOrderDetailsOpen(false)}
                >
                  Close
                </Button>
                
                {canUpdateStatus(selectedOrder) && (
                  <Button
                    onClick={() => {
                      setIsOrderDetailsOpen(false);
                      setIsStatusUpdateOpen(true);
                    }}
                  >
                    Update Status
                  </Button>
                )}
                
                {canApproveDecline(selectedOrder) && (
                  <>
                    <Button
                      onClick={() => {
                        setIsOrderDetailsOpen(false);
                        handleApproveOrder(selectedOrder);
                      }}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <CheckCircle className="h-4 w-4 mr-2" />
                      Approve
                    </Button>
                    
                    <Button
                      variant="destructive"
                      onClick={() => {
                        setIsOrderDetailsOpen(false);
                        handleDeclineOrder(selectedOrder);
                      }}
                    >
                      <XCircle className="h-4 w-4 mr-2" />
                      Decline
                    </Button>
                  </>
                )}
              </div>
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
              Update the status of order {selectedOrder?.order_number}
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

      {/* Decline Order Dialog */}
      <Dialog open={isDeclineDialogOpen} onOpenChange={setIsDeclineDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Decline Order</DialogTitle>
            <DialogDescription>
              Please provide a reason for declining this order.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="decline-reason" className="text-sm font-medium">
                Reason for Decline *
              </Label>
              <Textarea
                id="decline-reason"
                value={declineReason}
                onChange={(e) => setDeclineReason(e.target.value)}
                placeholder="Enter reason for declining this order..."
                className="mt-1"
                rows={3}
              />
            </div>
          </div>
          
          <div className="flex justify-end gap-3 pt-4">
            <Button
              variant="outline"
              onClick={() => {
                setIsDeclineDialogOpen(false);
                setDeclineReason("");
                setSelectedOrderForAction(null);
              }}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeclineConfirm}
              disabled={declineOrderMutation.isPending || !declineReason.trim()}
            >
              {declineOrderMutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Declining...
                </>
              ) : (
                "Decline Order"
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
      
      <MobileNav />
    </div>
  );
}
