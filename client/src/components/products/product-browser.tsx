import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { 
  Package, 
  ShoppingCart, 
  Eye, 
  Plus, 
  Minus, 
  Calendar,
  CheckCircle,
  Clock,
  Truck,
  X
} from "lucide-react";
import type { User } from "@/hooks/useAuth";

interface Product {
  id: string;
  name: string;
  description: string;
  sku: string;
  categoryId: string;
  manufacturerId: string;
  imageUrl: string;
  basePrice: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

interface OrderItem {
  id: string;
  productId: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  product: Product;
}

interface Order {
  id: string;
  orderNumber: string;
  retailerId: string;
  distributorId: string;
  totalAmount: number;
  status: string;
  createdAt: string;
  updatedAt: string;
  items: OrderItem[];
}

interface ProductBrowserProps {
  partner: User;
  isOpen: boolean;
  onClose: () => void;
}

export default function ProductBrowser({ partner, isOpen, onClose }: ProductBrowserProps) {
  const { user } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [quantities, setQuantities] = useState<Record<string, number>>({});
  const [isOrderModalOpen, setIsOrderModalOpen] = useState(false);
  const [selectedProducts, setSelectedProducts] = useState<Product[]>([]);

  // Determine if user can place new orders
  const canPlaceOrders = () => {
    if (!user || !partner) return false;
    
    // Retailer can order from Distributor
    if (user.role === 'retailer' && partner.role === 'distributor') return true;
    
    // Distributor can order from Manufacturer
    if (user.role === 'distributor' && partner.role === 'manufacturer') return true;
    
    return false;
  };

  // Fetch products from partner
  const { data: products = [], isLoading: productsLoading, error: productsError } = useQuery<Product[]>({
    queryKey: ["api", "products", "partner", partner.id],
    enabled: isOpen && canPlaceOrders(),
  });

  // Fetch order history
  const { data: orderHistory = [], isLoading: historyLoading, error: historyError } = useQuery<Order[]>({
    queryKey: ["api", "orders", "history", partner.id],
    enabled: isOpen && !canPlaceOrders(),
  });

  // Place order mutation
  const placeOrderMutation = useMutation({
    mutationFn: async (orderData: any) => {
      const response = await apiRequest("POST", "/api/orders", orderData);
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Order Placed",
        description: "Your order has been successfully placed.",
      });
      queryClient.invalidateQueries({ queryKey: ["api", "orders"] });
      setIsOrderModalOpen(false);
      setSelectedProducts([]);
      setQuantities({});
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to place order.",
        variant: "destructive",
      });
    },
  });

  const handleQuantityChange = (productId: string, change: number) => {
    const currentQty = quantities[productId] || 0;
    const newQty = Math.max(0, currentQty + change);
    
    if (newQty === 0) {
      const newQuantities = { ...quantities };
      delete newQuantities[productId];
      setQuantities(newQuantities);
    } else {
      setQuantities(prev => ({ ...prev, [productId]: newQty }));
    }
  };

  const handleAddToOrder = (product: Product) => {
    const currentQty = quantities[product.id] || 0;
    if (currentQty === 0) {
      setQuantities(prev => ({ ...prev, [product.id]: 1 }));
    }
  };

  const handlePlaceOrder = () => {
    const orderItems = Object.entries(quantities)
      .filter(([_, qty]) => qty > 0)
      .map(([productId, quantity]) => {
        const product = products.find(p => p.id === productId);
        return {
          productId,
          quantity,
          unitPrice: product?.basePrice || 0
        };
      });

    if (orderItems.length === 0) {
      toast({
        title: "No Items Selected",
        description: "Please select at least one product to order.",
        variant: "destructive",
      });
      return;
    }

    const orderData = {
      distributorId: partner.role === 'distributor' ? partner.id : user.id,
      retailerId: user.role === 'retailer' ? user.id : partner.id,
      items: orderItems,
      notes: `Order placed by ${user.role} for ${partner.role}`
    };

    placeOrderMutation.mutate(orderData);
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'delivered':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case 'dispatched':
        return <Truck className="h-4 w-4 text-blue-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const statusColors = {
      'pending': 'bg-yellow-100 text-yellow-800',
      'accepted': 'bg-blue-100 text-blue-800',
      'dispatched': 'bg-purple-100 text-purple-800',
      'delivered': 'bg-green-100 text-green-800',
      'cancelled': 'bg-red-100 text-red-800'
    };
    
    return (
      <Badge className={statusColors[status.toLowerCase() as keyof typeof statusColors] || 'bg-gray-100 text-gray-800'}>
        {status}
      </Badge>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[900px] max-h-[90vh] overflow-y-auto bg-white border border-gray-200 shadow-xl">
        <DialogHeader className="pb-6">
          <DialogTitle className="text-xl font-semibold text-gray-900">
            {canPlaceOrders() ? `Browse Products from ${partner.businessName || partner.firstName}` : `Order History with ${partner.businessName || partner.firstName}`}
          </DialogTitle>
          <DialogDescription className="text-gray-600">
            {canPlaceOrders() 
              ? `Browse and order products from ${partner.businessName || partner.firstName}`
              : `View order history with ${partner.businessName || partner.firstName}`
            }
          </DialogDescription>
        </DialogHeader>

        {canPlaceOrders() ? (
          // New Order View
          <div className="space-y-6">
            {productsError ? (
              <Card>
                <CardContent className="text-center py-12">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Products</h3>
                  <p className="text-gray-500 mb-4">
                    {productsError.message || "Failed to load products"}
                  </p>
                  <Button onClick={() => window.location.reload()}>
                    Retry
                  </Button>
                </CardContent>
              </Card>
            ) : productsLoading ? (
              <div className="text-center py-8">
                <div className="w-8 h-8 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto"></div>
                <p className="text-sm text-gray-600 mt-2">Loading products...</p>
              </div>
            ) : products.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No products available</h3>
                  <p className="text-gray-500">
                    This partner doesn't have any products listed yet.
                  </p>
                </CardContent>
              </Card>
            ) : (
              <>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {products.map((product) => (
                    <Card key={product.id} className="hover:shadow-md transition-shadow">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <Badge variant="outline">{product.sku}</Badge>
                          <span className="text-lg font-semibold">₹{product.basePrice}</span>
                        </div>
                        <CardTitle className="text-lg">{product.name}</CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <p className="text-sm text-gray-600 line-clamp-2">
                          {product.description}
                        </p>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleQuantityChange(product.id, -1)}
                              disabled={(quantities[product.id] || 0) <= 0}
                            >
                              <Minus className="h-3 w-3" />
                            </Button>
                            <span className="w-8 text-center text-sm font-medium">
                              {quantities[product.id] || 0}
                            </span>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleQuantityChange(product.id, 1)}
                            >
                              <Plus className="h-3 w-3" />
                            </Button>
                          </div>
                          <Button
                            size="sm"
                            onClick={() => handleAddToOrder(product)}
                            disabled={(quantities[product.id] || 0) > 0}
                          >
                            <ShoppingCart className="h-4 w-4 mr-1" />
                            Add
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {Object.keys(quantities).length > 0 && (
                  <div className="border-t pt-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-semibold">Order Summary</h3>
                        <p className="text-sm text-gray-600">
                          {Object.values(quantities).reduce((sum, qty) => sum + qty, 0)} items selected
                        </p>
                      </div>
                      <Button 
                        onClick={handlePlaceOrder}
                        disabled={placeOrderMutation.isPending}
                        className="action-button-primary"
                      >
                        {placeOrderMutation.isPending ? (
                          <>
                            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                            Placing Order...
                          </>
                        ) : (
                          <>
                            <ShoppingCart className="h-4 w-4 mr-2" />
                            Place Order
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        ) : (
          // History View
          <div className="space-y-6">
            {historyError ? (
              <Card>
                <CardContent className="text-center py-12">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Order History</h3>
                  <p className="text-gray-500 mb-4">
                    {historyError.message || "Failed to load order history"}
                  </p>
                  <Button onClick={() => window.location.reload()}>
                    Retry
                  </Button>
                </CardContent>
              </Card>
            ) : historyLoading ? (
              <div className="text-center py-8">
                <div className="w-8 h-8 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto"></div>
                <p className="text-sm text-gray-600 mt-2">Loading order history...</p>
              </div>
            ) : orderHistory.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No order history</h3>
                  <p className="text-gray-500">
                    No orders have been placed with this partner yet.
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="space-y-4">
                {orderHistory.map((order) => (
                  <Card key={order.id}>
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div>
                          <h3 className="text-lg font-semibold">Order #{order.orderNumber}</h3>
                          <p className="text-sm text-gray-600">
                            {formatDate(order.createdAt)}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(order.status)}
                          {getStatusBadge(order.status)}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Product</TableHead>
                            <TableHead>SKU</TableHead>
                            <TableHead>Quantity</TableHead>
                            <TableHead>Unit Price</TableHead>
                            <TableHead>Total</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {order.items.map((item) => (
                            <TableRow key={item.id}>
                              <TableCell className="font-medium">
                                {item.product.name}
                              </TableCell>
                              <TableCell>{item.product.sku}</TableCell>
                              <TableCell>{item.quantity}</TableCell>
                              <TableCell>₹{item.unitPrice}</TableCell>
                              <TableCell>₹{item.totalPrice}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                      <div className="flex justify-end mt-4">
                        <div className="text-right">
                          <p className="text-sm text-gray-600">Total Amount</p>
                          <p className="text-lg font-semibold">₹{order.totalAmount}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
} 