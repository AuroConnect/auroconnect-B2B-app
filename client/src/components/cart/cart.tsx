import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { apiRequest } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { 
  Trash2, 
  ShoppingCart, 
  Package, 
  DollarSign, 
  CheckCircle, 
  Minus, 
  Plus, 
  AlertCircle,
  Truck,
  CreditCard
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface CartItem {
  id: string;
  productId: string;
  productName: string;
  productSku: string;
  productImage: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  availableStock: number;
}

interface Cart {
  id: string;
  items: CartItem[];
  totalItems: number;
  totalAmount: number;
}

export default function Cart() {
  const { user } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [localQuantities, setLocalQuantities] = useState<Record<string, number>>({});
  const [isUpdating, setIsUpdating] = useState<Record<string, boolean>>({});

  // Fetch cart data
  const { data: cart, isLoading } = useQuery<Cart>({
    queryKey: ["api", "cart"],
    enabled: !!user,
  });

  // Initialize local quantities when cart data loads
  useEffect(() => {
    if (cart?.items) {
      const initialQuantities: Record<string, number> = {};
      cart.items.forEach(item => {
        initialQuantities[item.id] = item.quantity;
      });
      setLocalQuantities(initialQuantities);
    }
  }, [cart]);

  // Update cart item quantity
  const updateQuantityMutation = useMutation({
    mutationFn: async ({ itemId, quantity }: { itemId: string; quantity: number }) => {
      return apiRequest("PUT", `/api/cart/update/${itemId}`, { quantity });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["api", "cart"] });
      toast({
        title: "Cart Updated",
        description: "Item quantity updated successfully",
      });
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: "Failed to update cart item",
        variant: "destructive",
      });
    },
  });

  // Remove item from cart
  const removeItemMutation = useMutation({
    mutationFn: async (itemId: string) => {
      return apiRequest("DELETE", `/api/cart/remove/${itemId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["api", "cart"] });
      toast({
        title: "Item Removed",
        description: "Item removed from cart successfully",
      });
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: "Failed to remove item from cart",
        variant: "destructive",
      });
    },
  });

  // Clear cart
  const clearCartMutation = useMutation({
    mutationFn: async () => {
      return apiRequest("DELETE", "/api/cart/clear");
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["api", "cart"] });
      toast({
        title: "Cart Cleared",
        description: "Cart cleared successfully",
      });
    },
    onError: (error) => {
      toast({
        title: "Error",
        description: "Failed to clear cart",
        variant: "destructive",
      });
    },
  });

  // Place order from cart
  const placeOrderMutation = useMutation({
    mutationFn: async () => {
      if (!cart?.items || cart.items.length === 0) {
        throw new Error("No items in cart");
      }
      
      const cart_items = cart.items.map(item => ({
        product_id: item.productId,
        quantity: item.quantity
      }));
      
      const response = await apiRequest("POST", "/api/orders", {
        cart_items,
        delivery_option: 'DELIVER_TO_BUYER',
        notes: ''
      });
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["api", "cart"] });
      queryClient.invalidateQueries({ queryKey: ["api", "orders"] });
      toast({
        title: "Order Placed Successfully!",
        description: `Order ${data.orderNumber} has been created with ${data.itemsCount} items.`,
      });
      // Redirect to orders page after a short delay
      setTimeout(() => {
        window.location.href = "/orders";
      }, 2000);
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to place order",
        variant: "destructive",
      });
    },
  });

  const handleQuantityChange = (itemId: string, newQuantity: number) => {
    if (newQuantity < 1) return;
    
    const item = cart?.items.find(item => item.id === itemId);
    if (item && newQuantity > item.availableStock) {
      toast({
        title: "Invalid Quantity",
        description: `Maximum available stock is ${item.availableStock}`,
        variant: "destructive",
      });
      return;
    }

    // Update local state immediately for better UX
    setLocalQuantities(prev => ({ ...prev, [itemId]: newQuantity }));
    setIsUpdating(prev => ({ ...prev, [itemId]: true }));

    // Debounce the API call
    setTimeout(() => {
      updateQuantityMutation.mutate({ itemId, quantity: newQuantity }, {
        onSettled: () => {
          setIsUpdating(prev => ({ ...prev, [itemId]: false }));
        }
      });
    }, 500);
  };

  const handleRemoveItem = (itemId: string) => {
    removeItemMutation.mutate(itemId);
  };

  const handleClearCart = () => {
    if (confirm("Are you sure you want to clear your cart?")) {
      clearCartMutation.mutate();
    }
  };

  // Calculate real-time totals based on local quantities
  const calculateRealTimeTotals = () => {
    if (!cart?.items) return { totalItems: 0, totalAmount: 0 };
    
    let totalItems = 0;
    let totalAmount = 0;
    
    cart.items.forEach(item => {
      const quantity = localQuantities[item.id] || item.quantity;
      totalItems += quantity;
      totalAmount += item.unitPrice * quantity;
    });
    
    return { totalItems, totalAmount };
  };

  const realTimeTotals = calculateRealTimeTotals();

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <ShoppingCart className="h-5 w-5 mr-2" />
            Shopping Cart
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="w-8 h-8 border-4 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading cart...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!cart || cart.items.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <ShoppingCart className="h-5 w-5 mr-2" />
            Shopping Cart
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <ShoppingCart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Your cart is empty</h3>
            <p className="text-gray-600 mb-4">Add some products to get started</p>
            <Button onClick={() => window.location.href = "/products"}>
              Browse Products
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Cart Summary Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              <ShoppingCart className="h-5 w-5 mr-2" />
              Shopping Cart ({realTimeTotals.totalItems} items)
            </CardTitle>
            <Button
              variant="outline"
              size="sm"
              onClick={handleClearCart}
              disabled={clearCartMutation.isPending}
            >
              <Trash2 className="h-4 w-4 mr-1" />
              Clear Cart
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {cart.items.map((item) => {
              const localQuantity = localQuantities[item.id] || item.quantity;
              const localTotal = item.unitPrice * localQuantity;
              const isUpdatingItem = isUpdating[item.id];
              
              return (
                <div key={item.id} className="flex items-center space-x-4 p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="flex-shrink-0">
                    {item.productImage ? (
                      <img
                        src={item.productImage}
                        alt={item.productName}
                        className="w-16 h-16 object-cover rounded-md"
                      />
                    ) : (
                      <div className="w-16 h-16 bg-gray-200 rounded-md flex items-center justify-center">
                        <Package className="h-8 w-8 text-gray-400" />
                      </div>
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium text-gray-900 truncate">
                      {item.productName}
                    </h3>
                    <p className="text-sm text-gray-500">SKU: {item.productSku}</p>
                    <div className="flex items-center space-x-2 mt-1">
                      <Badge variant="outline" className="text-xs">
                        Stock: {item.availableStock}
                      </Badge>
                      <Badge variant="secondary" className="text-xs">
                        ₹{item.unitPrice.toFixed(2)} each
                      </Badge>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <div className="flex items-center border rounded-md">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleQuantityChange(item.id, localQuantity - 1)}
                        disabled={localQuantity <= 1 || isUpdatingItem}
                        className="h-8 w-8 p-0 hover:bg-gray-100"
                      >
                        <Minus className="h-3 w-3" />
                      </Button>
                      <Input
                        type="number"
                        value={localQuantity}
                        onChange={(e) => handleQuantityChange(item.id, parseInt(e.target.value) || 1)}
                        className="w-16 h-8 text-center border-0 focus:ring-0"
                        min="1"
                        max={item.availableStock}
                        disabled={isUpdatingItem}
                      />
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleQuantityChange(item.id, localQuantity + 1)}
                        disabled={localQuantity >= item.availableStock || isUpdatingItem}
                        className="h-8 w-8 p-0 hover:bg-gray-100"
                      >
                        <Plus className="h-3 w-3" />
                      </Button>
                    </div>
                    {isUpdatingItem && (
                      <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                    )}
                  </div>
                  
                  <div className="text-right">
                    <p className={`text-sm font-medium ${isUpdatingItem ? 'text-gray-400' : 'text-gray-900'}`}>
                      ₹{localTotal.toFixed(2)}
                    </p>
                    {localQuantity !== item.quantity && (
                      <p className="text-xs text-gray-500 line-through">
                        ₹{item.totalPrice.toFixed(2)}
                      </p>
                    )}
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleRemoveItem(item.id)}
                      disabled={removeItemMutation.isPending}
                      className="text-red-600 hover:text-red-700 p-1"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Order Summary Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <CreditCard className="h-5 w-5 mr-2" />
            Order Summary
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Subtotal ({realTimeTotals.totalItems} items):</span>
              <span className="font-medium">₹{realTimeTotals.totalAmount.toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Shipping:</span>
              <span className="font-medium text-green-600">Free</span>
            </div>
            <div className="border-t pt-4">
              <div className="flex justify-between items-center">
                <span className="text-lg font-semibold">Total:</span>
                <span className="text-2xl font-bold text-gray-900">
                  ₹{realTimeTotals.totalAmount.toFixed(2)}
                </span>
              </div>
            </div>
            
            <div className="flex space-x-3 pt-4">
              <Button
                onClick={() => window.location.href = "/products"}
                variant="outline"
                className="flex-1"
              >
                Continue Shopping
              </Button>
              <Button
                onClick={() => placeOrderMutation.mutate()}
                disabled={placeOrderMutation.isPending}
                className="flex-1 bg-green-600 hover:bg-green-700"
              >
                {placeOrderMutation.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Placing Order...
                  </>
                ) : (
                  <>
                    <Truck className="h-4 w-4 mr-2" />
                    Place Order
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
