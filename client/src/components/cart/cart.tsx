import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { apiRequest } from "@/lib/queryClient";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Trash2, ShoppingCart, Package, DollarSign, CheckCircle } from "lucide-react";
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
  const [quantities, setQuantities] = useState<Record<string, number>>({});

  // Fetch cart data
  const { data: cart, isLoading } = useQuery<Cart>({
    queryKey: ["api", "cart"],
    enabled: !!user,
  });

  // Update cart item quantity
  const updateQuantityMutation = useMutation({
    mutationFn: async ({ itemId, quantity }: { itemId: string; quantity: number }) => {
      return apiRequest(`/api/cart/update/${itemId}`, {
        method: "PUT",
        body: JSON.stringify({ quantity }),
      });
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
      return apiRequest(`/api/cart/remove/${itemId}`, {
        method: "DELETE",
      });
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
      return apiRequest("/api/cart/clear", {
        method: "DELETE",
      });
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
      return apiRequest("/api/orders", {
        method: "POST",
      });
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

    updateQuantityMutation.mutate({ itemId, quantity: newQuantity });
  };

  const handleRemoveItem = (itemId: string) => {
    removeItemMutation.mutate(itemId);
  };

  const handleClearCart = () => {
    if (confirm("Are you sure you want to clear your cart?")) {
      clearCartMutation.mutate();
    }
  };

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
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center">
            <ShoppingCart className="h-5 w-5 mr-2" />
            Shopping Cart ({cart.totalItems} items)
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
          {cart.items.map((item) => (
            <div key={item.id} className="flex items-center space-x-4 p-4 border rounded-lg">
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
                    ${item.unitPrice.toFixed(2)} each
                  </Badge>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <div className="flex items-center border rounded-md">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleQuantityChange(item.id, item.quantity - 1)}
                    disabled={item.quantity <= 1 || updateQuantityMutation.isPending}
                    className="h-8 w-8 p-0"
                  >
                    -
                  </Button>
                  <Input
                    type="number"
                    value={item.quantity}
                    onChange={(e) => handleQuantityChange(item.id, parseInt(e.target.value) || 1)}
                    className="w-16 h-8 text-center border-0"
                    min="1"
                    max={item.availableStock}
                  />
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleQuantityChange(item.id, item.quantity + 1)}
                    disabled={item.quantity >= item.availableStock || updateQuantityMutation.isPending}
                    className="h-8 w-8 p-0"
                  >
                    +
                  </Button>
                </div>
              </div>
              
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  ${item.totalPrice.toFixed(2)}
                </p>
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
          ))}
          
          <div className="border-t pt-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center">
                <DollarSign className="h-5 w-5 text-gray-600 mr-2" />
                <span className="text-lg font-medium">Total:</span>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-gray-900">
                  ${cart.totalAmount.toFixed(2)}
                </p>
                <p className="text-sm text-gray-500">
                  {cart.totalItems} item{cart.totalItems !== 1 ? 's' : ''}
                </p>
              </div>
            </div>
            
            <div className="mt-4 flex space-x-2">
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
                className="flex-1"
              >
                {placeOrderMutation.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Placing Order...
                  </>
                ) : (
                  <>
                    <Package className="h-4 w-4 mr-2" />
                    Place Order
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
