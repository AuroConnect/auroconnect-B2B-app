import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useAuth } from "@/hooks/useAuth";
import { useCart } from "@/hooks/useCart";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { Package, ShoppingCart, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

export default function CartPage() {
  const { user, isLoading } = useAuth();
  const { toast } = useToast();
  const cart = useCart();
  const [address, setAddress] = useState("");
  const [placing, setPlacing] = useState(false);

  useEffect(() => {
    if (!isLoading && !user) {
      toast({ title: "Unauthorized", description: "Please login.", variant: "destructive" });
      window.location.href = "/";
    }
  }, [user, isLoading, toast]);

  const placeOrder = async () => {
    if (!user) return;
    if (cart.items.length === 0) {
      toast({ title: "Cart is empty", variant: "destructive" });
      return;
    }
    if (!address.trim()) {
      toast({ title: "Delivery address required", variant: "destructive" });
      return;
    }

    try {
      setPlacing(true);
      const payload = {
        items: cart.items.map((i) => ({ product_id: i.product.id, quantity: i.quantity })),
        delivery_address: address,
        delivery_method: "delivery",
      };
      const res = await apiRequest("POST", "/api/orders", payload);
      const data = await res.json();
      toast({ title: "Order placed", description: `Order #${data.orderNumber || data.id}` });
      cart.clear();
      window.location.href = "/orders";
    } catch (e: any) {
      toast({ title: "Failed to place order", description: e.message, variant: "destructive" });
    } finally {
      setPlacing(false);
    }
  };

  if (isLoading || !user) {
    return (
      <div className="min-h-screen auromart-gradient-bg flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
          <ShoppingCart className="h-6 w-6" /> Cart
        </h1>
        <p className="text-gray-600">Review your items and place the order</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Items</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {cart.items.length === 0 ? (
              <div className="text-center py-12">
                <Package className="h-12 w-12 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-500">Your cart is empty</p>
              </div>
            ) : (
              cart.items.map((item) => (
                <div key={item.product.id} className="flex items-center gap-4 p-3 border rounded-lg">
                  <div className="w-16 h-16 bg-gray-100 rounded overflow-hidden flex items-center justify-center">
                    {item.product.imageUrl ? (
                      <img src={item.product.imageUrl} alt={item.product.name} className="w-full h-full object-cover" />
                    ) : (
                      <Package className="h-6 w-6 text-gray-400" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-gray-900 truncate">{item.product.name}</h3>
                    <p className="text-sm text-gray-500">SKU: {item.product.sku}</p>
                    <p className="text-sm text-gray-500">₹{item.product.basePrice}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Input
                      type="number"
                      min="1"
                      value={item.quantity}
                      onChange={(e) => cart.updateQuantity(item.product.id, parseInt(e.target.value) || 1)}
                      className="w-20"
                    />
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => cart.removeItem(item.product.id)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Order Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span>₹{cart.total}</span>
              </div>
              <div className="flex justify-between">
                <span>Shipping</span>
                <span>₹0</span>
              </div>
              <div className="border-t pt-2">
                <div className="flex justify-between font-medium">
                  <span>Total</span>
                  <span>₹{cart.total}</span>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Delivery Address</label>
              <Input
                placeholder="Enter delivery address"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
              />
            </div>

            <Button
              onClick={placeOrder}
              disabled={placing || cart.items.length === 0}
              className="w-full"
            >
              {placing ? "Placing Order..." : "Place Order"}
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
