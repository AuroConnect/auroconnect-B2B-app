import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { setupAuth, isAuthenticated } from "./replitAuth";
import { insertProductSchema, insertOrderSchema, insertOrderItemSchema } from "@shared/schema";
import { z } from "zod";

export async function registerRoutes(app: Express): Promise<Server> {
  // Auth middleware
  await setupAuth(app);

  // Auth routes
  app.get('/api/auth/user', isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const user = await storage.getUser(userId);
      res.json(user);
    } catch (error) {
      console.error("Error fetching user:", error);
      res.status(500).json({ message: "Failed to fetch user" });
    }
  });

  // Registration route for all user roles
  app.post('/api/auth/register', async (req, res) => {
    try {
      const { 
        firstName, 
        lastName, 
        email, 
        password, 
        role, 
        businessName, 
        address, 
        phoneNumber, 
        whatsappNumber 
      } = req.body;

      // Basic validation
      if (!firstName || !lastName || !email || !password || !role) {
        return res.status(400).json({ message: "Missing required fields" });
      }

      if (!['retailer', 'distributor', 'manufacturer'].includes(role)) {
        return res.status(400).json({ message: "Invalid role" });
      }

      if (password.length < 6) {
        return res.status(400).json({ message: "Password must be at least 6 characters long" });
      }

      // Check if user already exists
      const existingUser = await storage.getUserByEmail(email);
      if (existingUser) {
        return res.status(409).json({ message: "User with this email already exists" });
      }

      // Create new user
      const newUser = await storage.createUser({
        firstName,
        lastName,
        email,
        role,
        businessName,
        address,
        phoneNumber,
        whatsappNumber,
      });

      // Return user without sensitive information
      const { ...userResponse } = newUser;
      res.status(201).json({ 
        message: "Registration successful", 
        user: userResponse 
      });
    } catch (error) {
      console.error("Error registering user:", error);
      res.status(500).json({ message: "Failed to register user" });
    }
  });

  // Categories routes
  app.get('/api/categories', async (req, res) => {
    try {
      const categories = await storage.getCategories();
      res.json(categories);
    } catch (error) {
      console.error("Error fetching categories:", error);
      res.status(500).json({ message: "Failed to fetch categories" });
    }
  });

  // Products routes
  app.get('/api/products', async (req, res) => {
    try {
      const { categoryId } = req.query;
      const products = await storage.getAvailableProducts(categoryId as string);
      res.json(products);
    } catch (error) {
      console.error("Error fetching products:", error);
      res.status(500).json({ message: "Failed to fetch products" });
    }
  });

  app.get('/api/products/:id', async (req, res) => {
    try {
      const product = await storage.getProductById(req.params.id);
      if (!product) {
        return res.status(404).json({ message: "Product not found" });
      }
      res.json(product);
    } catch (error) {
      console.error("Error fetching product:", error);
      res.status(500).json({ message: "Failed to fetch product" });
    }
  });

  app.post('/api/products', isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const user = await storage.getUser(userId);
      
      if (user?.role !== 'manufacturer') {
        return res.status(403).json({ message: "Only manufacturers can create products" });
      }

      const productData = insertProductSchema.parse({
        ...req.body,
        manufacturerId: userId,
      });
      
      const product = await storage.createProduct(productData);
      res.status(201).json(product);
    } catch (error) {
      console.error("Error creating product:", error);
      res.status(500).json({ message: "Failed to create product" });
    }
  });

  // Orders routes
  app.get('/api/orders', isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const user = await storage.getUser(userId);
      
      let orders;
      if (user?.role === 'retailer') {
        orders = await storage.getOrdersByRetailer(userId);
      } else if (user?.role === 'distributor') {
        orders = await storage.getOrdersByDistributor(userId);
      } else {
        return res.status(403).json({ message: "Access denied" });
      }
      
      res.json(orders);
    } catch (error) {
      console.error("Error fetching orders:", error);
      res.status(500).json({ message: "Failed to fetch orders" });
    }
  });

  app.get('/api/orders/:id', isAuthenticated, async (req: any, res) => {
    try {
      const order = await storage.getOrderById(req.params.id);
      if (!order) {
        return res.status(404).json({ message: "Order not found" });
      }
      
      const orderItems = await storage.getOrderItems(order.id);
      res.json({ ...order, items: orderItems });
    } catch (error) {
      console.error("Error fetching order:", error);
      res.status(500).json({ message: "Failed to fetch order" });
    }
  });

  const createOrderSchema = z.object({
    distributorId: z.string(),
    items: z.array(z.object({
      productId: z.string(),
      quantity: z.number().positive(),
      unitPrice: z.string(),
    })),
    notes: z.string().optional(),
    deliveryMode: z.enum(['pickup', 'delivery']).optional(),
  });

  app.post('/api/orders', isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const user = await storage.getUser(userId);
      
      if (user?.role !== 'retailer') {
        return res.status(403).json({ message: "Only retailers can create orders" });
      }

      const { distributorId, items, notes, deliveryMode } = createOrderSchema.parse(req.body);
      
      // Calculate total amount
      const totalAmount = items.reduce((sum, item) => 
        sum + (parseFloat(item.unitPrice) * item.quantity), 0
      );

      // Generate order number
      const orderNumber = `ORD-${new Date().getFullYear()}-${Date.now()}`;
      
      // Create order
      const order = await storage.createOrder({
        orderNumber,
        retailerId: userId,
        distributorId,
        totalAmount: totalAmount.toString(),
        notes,
        deliveryMode: deliveryMode || 'delivery',
        status: 'pending',
      });

      // Create order items
      const orderItemsData = items.map(item => ({
        orderId: order.id,
        productId: item.productId,
        quantity: item.quantity,
        unitPrice: item.unitPrice,
        totalPrice: (parseFloat(item.unitPrice) * item.quantity).toString(),
      }));
      
      await storage.createOrderItems(orderItemsData);

      // Create WhatsApp notification for distributor
      await storage.createNotification({
        userId: distributorId,
        message: `New order ${orderNumber} from ${user.businessName || user.firstName}`,
        type: 'order_placed',
        sentAt: null,
        isDelivered: false,
      });

      res.status(201).json(order);
    } catch (error) {
      console.error("Error creating order:", error);
      res.status(500).json({ message: "Failed to create order" });
    }
  });

  app.patch('/api/orders/:id/status', isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const user = await storage.getUser(userId);
      
      if (user?.role !== 'distributor') {
        return res.status(403).json({ message: "Only distributors can update order status" });
      }

      const { status } = z.object({ status: z.string() }).parse(req.body);
      const order = await storage.updateOrderStatus(req.params.id, status);
      
      // Create WhatsApp notification for retailer
      await storage.createNotification({
        userId: order.retailerId,
        message: `Order ${order.orderNumber} status updated to: ${status}`,
        type: 'order_status_update',
        sentAt: null,
        isDelivered: false,
      });

      res.json(order);
    } catch (error) {
      console.error("Error updating order status:", error);
      res.status(500).json({ message: "Failed to update order status" });
    }
  });

  // Analytics routes
  app.get('/api/analytics/stats', isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const user = await storage.getUser(userId);
      
      if (!user) {
        return res.status(404).json({ message: "User not found" });
      }

      const stats = await storage.getOrderStats(userId, user.role);
      
      // Add role-specific stats
      if (user.role === 'retailer') {
        const distributors = await storage.getDistributors();
        stats.activeDistributors = distributors.length;
      }
      
      res.json(stats);
    } catch (error) {
      console.error("Error fetching analytics:", error);
      res.status(500).json({ message: "Failed to fetch analytics" });
    }
  });

  // Distributors routes
  app.get('/api/distributors', async (req, res) => {
    try {
      const distributors = await storage.getDistributors();
      res.json(distributors);
    } catch (error) {
      console.error("Error fetching distributors:", error);
      res.status(500).json({ message: "Failed to fetch distributors" });
    }
  });

  // Inventory routes (for distributors)
  app.get('/api/inventory', isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const user = await storage.getUser(userId);
      
      if (user?.role !== 'distributor') {
        return res.status(403).json({ message: "Only distributors can view inventory" });
      }

      const inventory = await storage.getInventoryByDistributor(userId);
      res.json(inventory);
    } catch (error) {
      console.error("Error fetching inventory:", error);
      res.status(500).json({ message: "Failed to fetch inventory" });
    }
  });

  // WhatsApp notifications routes
  app.get('/api/notifications', isAuthenticated, async (req: any, res) => {
    try {
      const notifications = await storage.getPendingNotifications();
      res.json(notifications);
    } catch (error) {
      console.error("Error fetching notifications:", error);
      res.status(500).json({ message: "Failed to fetch notifications" });
    }
  });

  // Partnership routes
  app.get("/api/partnerships", isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const partnerships = await storage.getPartnerships(userId);
      res.json(partnerships);
    } catch (error) {
      console.error("Error fetching partnerships:", error);
      res.status(500).json({ message: "Failed to fetch partnerships" });
    }
  });

  app.get("/api/partners/available", isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const user = await storage.getUser(userId);
      if (!user) {
        return res.status(404).json({ message: "User not found" });
      }
      const availablePartners = await storage.getAvailablePartners(userId, user.role);
      res.json(availablePartners);
    } catch (error) {
      console.error("Error fetching available partners:", error);
      res.status(500).json({ message: "Failed to fetch available partners" });
    }
  });

  app.post("/api/partnerships/request", isAuthenticated, async (req: any, res) => {
    try {
      const requesterId = req.user.claims.sub;
      const { partnerId, partnershipType } = req.body;
      
      if (!partnerId || !partnershipType) {
        return res.status(400).json({ message: "Partner ID and partnership type are required" });
      }

      const partnership = await storage.sendPartnershipRequest(requesterId, partnerId, partnershipType);
      res.json(partnership);
    } catch (error) {
      console.error("Error sending partnership request:", error);
      res.status(500).json({ message: "Failed to send partnership request" });
    }
  });

  app.patch("/api/partnerships/:id/respond", isAuthenticated, async (req: any, res) => {
    try {
      const { id } = req.params;
      const { status } = req.body;
      
      if (!['approved', 'rejected'].includes(status)) {
        return res.status(400).json({ message: "Invalid status" });
      }

      const partnership = await storage.respondToPartnershipRequest(id, status);
      res.json(partnership);
    } catch (error) {
      console.error("Error responding to partnership request:", error);
      res.status(500).json({ message: "Failed to respond to partnership request" });
    }
  });

  // Global search routes
  app.get("/api/partners/search", isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const user = await storage.getUser(userId);
      const productSearchTerm = req.query.product || req.query[1]; // Handle both query patterns
      
      if (!user) {
        return res.status(404).json({ message: "User not found" });
      }

      if (productSearchTerm && productSearchTerm.length > 2) {
        // Search partners by product
        const partners = await storage.searchPartnersByProduct(productSearchTerm, user.role);
        res.json(partners);
      } else {
        // Return empty array for short search terms
        res.json([]);
      }
    } catch (error) {
      console.error("Error searching partners:", error);
      res.status(500).json({ message: "Failed to search partners" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
