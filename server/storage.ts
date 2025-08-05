import {
  users,
  categories,
  products,
  inventory,
  orders,
  orderItems,
  invoices,
  whatsappNotifications,
  partnerships,
  type User,
  type UpsertUser,
  type Category,
  type InsertCategory,
  type Product,
  type InsertProduct,
  type Inventory,
  type InsertInventory,
  type Order,
  type InsertOrder,
  type OrderItem,
  type InsertOrderItem,
  type Invoice,
  type InsertInvoice,
  type WhatsappNotification,
  type Partnership,
  type InsertPartnership,
} from "@shared/schema";
import { db } from "./db";
import { eq, and, desc, sql, or } from "drizzle-orm";

export interface IStorage {
  // User operations (mandatory for Replit Auth)
  getUser(id: string): Promise<User | undefined>;
  upsertUser(user: UpsertUser): Promise<User>;
  getUserByEmail(email: string): Promise<User | undefined>;
  
  // Category operations
  getCategories(): Promise<Category[]>;
  createCategory(category: InsertCategory): Promise<Category>;
  
  // Product operations
  getProducts(categoryId?: string): Promise<Product[]>;
  getProductById(id: string): Promise<Product | undefined>;
  createProduct(product: InsertProduct): Promise<Product>;
  
  // Inventory operations
  getInventoryByDistributor(distributorId: string): Promise<Inventory[]>;
  getAvailableProducts(categoryId?: string): Promise<(Product & { inventory: Inventory })[]>;
  updateInventory(inventoryData: InsertInventory): Promise<Inventory>;
  
  // Order operations
  createOrder(order: InsertOrder): Promise<Order>;
  getOrdersByRetailer(retailerId: string): Promise<Order[]>;
  getOrdersByDistributor(distributorId: string): Promise<Order[]>;
  getOrderById(id: string): Promise<Order | undefined>;
  updateOrderStatus(orderId: string, status: string): Promise<Order>;
  
  // Order item operations
  createOrderItems(items: InsertOrderItem[]): Promise<OrderItem[]>;
  getOrderItems(orderId: string): Promise<(OrderItem & { product: Product })[]>;
  
  // Invoice operations
  createInvoice(invoice: InsertInvoice): Promise<Invoice>;
  getInvoiceByOrderId(orderId: string): Promise<Invoice | undefined>;
  
  // WhatsApp notification operations
  createNotification(notification: Omit<WhatsappNotification, 'id' | 'createdAt'>): Promise<WhatsappNotification>;
  getPendingNotifications(): Promise<WhatsappNotification[]>;
  markNotificationSent(id: string): Promise<void>;
  
  // Analytics operations
  getOrderStats(userId: string, role: string): Promise<any>;
  getDistributors(): Promise<User[]>;
  getManufacturers(): Promise<User[]>;
  
  // Partnership operations
  getPartnerships(userId: string): Promise<(Partnership & { partner: User })[]>;
  getAvailablePartners(userId: string, userRole: string): Promise<User[]>;
  sendPartnershipRequest(requesterId: string, partnerId: string, partnershipType: string): Promise<Partnership>;
  respondToPartnershipRequest(partnershipId: string, status: 'approved' | 'rejected'): Promise<Partnership>;
  
  // Global search operations
  searchPartnersByProduct(productName: string, userRole: string): Promise<User[]>;
  getGlobalPartners(userRole: string): Promise<User[]>;
  
  // Registration operations
  createUser(userData: InsertUser): Promise<User>;
}

export class DatabaseStorage implements IStorage {
  // User operations
  async getUser(id: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.id, id));
    return user;
  }

  async upsertUser(userData: UpsertUser): Promise<User> {
    const [user] = await db
      .insert(users)
      .values(userData)
      .onConflictDoUpdate({
        target: users.id,
        set: {
          ...userData,
          updatedAt: new Date(),
        },
      })
      .returning();
    return user;
  }

  async getUserByEmail(email: string): Promise<User | undefined> {
    const [user] = await db.select().from(users).where(eq(users.email, email));
    return user;
  }

  // Category operations
  async getCategories(): Promise<Category[]> {
    return await db.select().from(categories);
  }

  async createCategory(category: InsertCategory): Promise<Category> {
    const [newCategory] = await db.insert(categories).values(category).returning();
    return newCategory;
  }

  // Product operations
  async getProducts(categoryId?: string): Promise<Product[]> {
    if (categoryId) {
      return await db.select().from(products).where(and(
        eq(products.isActive, true),
        eq(products.categoryId, categoryId)
      ));
    }
    return await db.select().from(products).where(eq(products.isActive, true));
  }

  async getProductById(id: string): Promise<Product | undefined> {
    const [product] = await db.select().from(products).where(eq(products.id, id));
    return product;
  }

  async createProduct(product: InsertProduct): Promise<Product> {
    const [newProduct] = await db.insert(products).values(product).returning();
    return newProduct;
  }

  // Inventory operations
  async getInventoryByDistributor(distributorId: string): Promise<Inventory[]> {
    return await db
      .select()
      .from(inventory)
      .where(eq(inventory.distributorId, distributorId));
  }

  async getAvailableProducts(categoryId?: string): Promise<(Product & { inventory: Inventory })[]> {
    let whereConditions = and(
      eq(products.isActive, true),
      eq(inventory.isAvailable, true),
      sql`${inventory.quantity} > 0`
    );

    if (categoryId) {
      whereConditions = and(
        whereConditions,
        eq(products.categoryId, categoryId)
      );
    }

    const results = await db
      .select()
      .from(products)
      .innerJoin(inventory, eq(products.id, inventory.productId))
      .where(whereConditions);
      
    return results.map(result => ({
      ...result.products,
      inventory: result.inventory
    }));
  }

  async updateInventory(inventoryData: InsertInventory): Promise<Inventory> {
    const [updatedInventory] = await db
      .insert(inventory)
      .values(inventoryData)
      .onConflictDoUpdate({
        target: [inventory.distributorId, inventory.productId],
        set: {
          ...inventoryData,
          updatedAt: new Date(),
        },
      })
      .returning();
    return updatedInventory;
  }

  // Order operations
  async createOrder(order: InsertOrder): Promise<Order> {
    const [newOrder] = await db.insert(orders).values(order).returning();
    return newOrder;
  }

  async getOrdersByRetailer(retailerId: string): Promise<Order[]> {
    return await db
      .select()
      .from(orders)
      .where(eq(orders.retailerId, retailerId))
      .orderBy(desc(orders.createdAt));
  }

  async getOrdersByDistributor(distributorId: string): Promise<Order[]> {
    return await db
      .select()
      .from(orders)
      .where(eq(orders.distributorId, distributorId))
      .orderBy(desc(orders.createdAt));
  }

  async getOrderById(id: string): Promise<Order | undefined> {
    const [order] = await db.select().from(orders).where(eq(orders.id, id));
    return order;
  }

  async updateOrderStatus(orderId: string, status: string): Promise<Order> {
    const [updatedOrder] = await db
      .update(orders)
      .set({ status: status as any, updatedAt: new Date() })
      .where(eq(orders.id, orderId))
      .returning();
    return updatedOrder;
  }

  // Order item operations
  async createOrderItems(items: InsertOrderItem[]): Promise<OrderItem[]> {
    return await db.insert(orderItems).values(items).returning();
  }

  async getOrderItems(orderId: string): Promise<(OrderItem & { product: Product })[]> {
    const results = await db
      .select()
      .from(orderItems)
      .innerJoin(products, eq(orderItems.productId, products.id))
      .where(eq(orderItems.orderId, orderId));
    
    return results.map(result => ({
      ...result.order_items,
      product: result.products
    }));
  }

  // Invoice operations
  async createInvoice(invoice: InsertInvoice): Promise<Invoice> {
    const [newInvoice] = await db.insert(invoices).values(invoice).returning();
    return newInvoice;
  }

  async getInvoiceByOrderId(orderId: string): Promise<Invoice | undefined> {
    const [invoice] = await db.select().from(invoices).where(eq(invoices.orderId, orderId));
    return invoice;
  }

  // WhatsApp notification operations
  async createNotification(notification: Omit<WhatsappNotification, 'id' | 'createdAt'>): Promise<WhatsappNotification> {
    const [newNotification] = await db.insert(whatsappNotifications).values(notification).returning();
    return newNotification;
  }

  async getPendingNotifications(): Promise<WhatsappNotification[]> {
    return await db
      .select()
      .from(whatsappNotifications)
      .where(eq(whatsappNotifications.isDelivered, false));
  }

  async markNotificationSent(id: string): Promise<void> {
    await db
      .update(whatsappNotifications)
      .set({ isDelivered: true, sentAt: new Date() })
      .where(eq(whatsappNotifications.id, id));
  }

  // Analytics operations
  async getOrderStats(userId: string, role: string): Promise<any> {
    const whereClause = role === 'retailer' 
      ? eq(orders.retailerId, userId)
      : eq(orders.distributorId, userId);

    const totalOrders = await db
      .select({ count: sql<number>`count(*)` })
      .from(orders)
      .where(whereClause);

    const pendingOrders = await db
      .select({ count: sql<number>`count(*)` })
      .from(orders)
      .where(and(whereClause, eq(orders.status, 'pending')));

    const monthlySpend = await db
      .select({ total: sql<number>`sum(${orders.totalAmount})` })
      .from(orders)
      .where(and(
        whereClause,
        sql`${orders.createdAt} >= date_trunc('month', current_date)`
      ));

    return {
      totalOrders: totalOrders[0]?.count || 0,
      pendingOrders: pendingOrders[0]?.count || 0,
      monthlySpend: monthlySpend[0]?.total || 0,
    };
  }

  async getDistributors(): Promise<User[]> {
    return await db
      .select()
      .from(users)
      .where(and(eq(users.role, 'distributor'), eq(users.isActive, true)));
  }

  async getManufacturers(): Promise<User[]> {
    return await db
      .select()
      .from(users)
      .where(and(eq(users.role, 'manufacturer'), eq(users.isActive, true)));
  }

  // Partnership operations
  async getPartnerships(userId: string): Promise<(Partnership & { partner: User })[]> {
    const results = await db
      .select()
      .from(partnerships)
      .innerJoin(users, eq(partnerships.partnerId, users.id))
      .where(and(
        eq(partnerships.requesterId, userId),
        eq(partnerships.status, 'approved')
      ));
    
    return results.map(result => ({
      ...result.partnerships,
      partner: result.users
    }));
  }

  async getAvailablePartners(userId: string, userRole: string): Promise<User[]> {
    // Business logic: 
    // - Retailers can only see distributors
    // - Distributors can see both retailers and manufacturers
    // - Manufacturers can only see distributors
    // - Exclude users who are already partners or have pending requests
    
    let allowedRoles: string[] = [];
    switch (userRole) {
      case 'retailer':
        allowedRoles = ['distributor'];
        break;
      case 'distributor':
        allowedRoles = ['retailer', 'manufacturer'];
        break;
      case 'manufacturer':
        allowedRoles = ['distributor'];
        break;
      default:
        return [];
    }

    // Get existing partnership connections
    const existingPartnerships = await db
      .select({ partnerId: partnerships.partnerId })
      .from(partnerships)
      .where(eq(partnerships.requesterId, userId));

    const existingPartnerIds = existingPartnerships.map(p => p.partnerId);
    
    // Get available partners excluding existing ones
    let whereConditions = and(
      sql`${users.role} IN (${allowedRoles.map(role => `'${role}'`).join(', ')})`,
      eq(users.isActive, true),
      sql`${users.id} != ${userId}`
    );

    if (existingPartnerIds.length > 0) {
      whereConditions = and(
        whereConditions,
        sql`${users.id} NOT IN (${sql.join(existingPartnerIds.map(id => sql`${id}`), sql`, `)})`
      );
    }

    const availablePartners = await db
      .select()
      .from(users)
      .where(whereConditions);

    return availablePartners;
  }

  async sendPartnershipRequest(requesterId: string, partnerId: string, partnershipType: string): Promise<Partnership> {
    const [partnership] = await db
      .insert(partnerships)
      .values({
        requesterId,
        partnerId,
        partnershipType: partnershipType as "supplier" | "distributor" | "retailer",
        status: 'pending'
      })
      .returning();
    
    return partnership;
  }

  async respondToPartnershipRequest(partnershipId: string, status: 'approved' | 'rejected'): Promise<Partnership> {
    const [partnership] = await db
      .update(partnerships)
      .set({ 
        status, 
        updatedAt: new Date() 
      })
      .where(eq(partnerships.id, partnershipId))
      .returning();
    
    return partnership;
  }

  // Global search operations
  async searchPartnersByProduct(productName: string, userRole: string): Promise<User[]> {
    // Search for partners who have the specific product in their inventory
    let allowedRoles: string[] = [];
    switch (userRole) {
      case 'retailer':
        allowedRoles = ['distributor'];
        break;
      case 'distributor':
        allowedRoles = ['manufacturer']; // distributors search for manufacturers who produce the product
        break;
      default:
        return [];
    }

    const partnersWithProduct = await db
      .select({
        id: users.id,
        email: users.email,
        firstName: users.firstName,
        lastName: users.lastName,
        role: users.role,
        businessName: users.businessName,
        profileImageUrl: users.profileImageUrl,
        isActive: users.isActive,
        address: users.address,
        phoneNumber: users.phoneNumber,
        whatsappNumber: users.whatsappNumber,
        createdAt: users.createdAt,
        updatedAt: users.updatedAt,
      })
      .from(users)
      .innerJoin(inventory, eq(users.id, inventory.distributorId))
      .innerJoin(products, eq(inventory.productId, products.id))
      .where(and(
        sql`${users.role} IN (${allowedRoles.map(role => `'${role}'`).join(', ')})`,
        eq(users.isActive, true),
        sql`LOWER(${products.name}) LIKE LOWER(${'%' + productName + '%'})`,
        eq(inventory.isAvailable, true),
        sql`${inventory.quantity} > 0`
      ));

    return partnersWithProduct;
  }

  async getGlobalPartners(userRole: string): Promise<User[]> {
    // Similar to getAvailablePartners but without excluding existing partnerships
    let allowedRoles: string[] = [];
    switch (userRole) {
      case 'retailer':
        allowedRoles = ['distributor'];
        break;
      case 'distributor':
        allowedRoles = ['retailer', 'manufacturer'];
        break;
      case 'manufacturer':
        allowedRoles = ['distributor'];
        break;
      default:
        return [];
    }

    const globalPartners = await db
      .select()
      .from(users)
      .where(and(
        sql`${users.role} IN (${allowedRoles.map(role => `'${role}'`).join(', ')})`,
        eq(users.isActive, true)
      ));

    return globalPartners;
  }

  // Registration operations
  async createUser(userData: InsertUser): Promise<User> {
    const [user] = await db
      .insert(users)
      .values({
        ...userData,
        isActive: true,
      })
      .returning();
    return user;
  }
}

export const storage = new DatabaseStorage();
