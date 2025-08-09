import { useEffect, useMemo, useState } from "react";
import { useAuth } from "@/hooks/useAuth";

export interface CartProduct {
  id: string;
  name: string;
  sku?: string;
  imageUrl?: string | null;
  basePrice?: number;
}

export interface CartItem {
  product: CartProduct;
  quantity: number;
}

function getStorageKey(userId?: string | null) {
  return userId ? `cart:${userId}` : "cart:guest";
}

export function useCart() {
  const { user } = useAuth();
  const storageKey = useMemo(() => getStorageKey(user?.id || null), [user?.id]);
  const [items, setItems] = useState<CartItem[]>([]);

  // Load from localStorage
  useEffect(() => {
    try {
      const raw = localStorage.getItem(storageKey);
      if (raw) setItems(JSON.parse(raw));
    } catch {}
  }, [storageKey]);

  // Persist to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(storageKey, JSON.stringify(items));
    } catch {}
  }, [items, storageKey]);

  const addItem = (product: CartProduct, quantity = 1) => {
    setItems((prev) => {
      const idx = prev.findIndex((i) => i.product.id === product.id);
      if (idx >= 0) {
        const updated = [...prev];
        updated[idx] = { ...updated[idx], quantity: Math.min(updated[idx].quantity + quantity, 9999) };
        return updated;
      }
      return [...prev, { product, quantity }];
    });
  };

  const updateQuantity = (productId: string, quantity: number) => {
    setItems((prev) => prev.map((i) => (i.product.id === productId ? { ...i, quantity: Math.max(1, Math.min(9999, quantity)) } : i)));
  };

  const removeItem = (productId: string) => setItems((prev) => prev.filter((i) => i.product.id !== productId));
  const clear = () => setItems([]);

  const subtotal = items.reduce((sum, i) => sum + (i.product.basePrice || 0) * i.quantity, 0);
  const count = items.reduce((sum, i) => sum + i.quantity, 0);

  return {
    items,
    addItem,
    updateQuantity,
    removeItem,
    clear,
    subtotal,
    count,
  };
}


