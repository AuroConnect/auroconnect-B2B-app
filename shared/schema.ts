import { sql, relations } from "drizzle-orm";
import {
  index,
  jsonb,
  pgTable,
  timestamp,
  varchar,
  text,
  integer,
  decimal,
  boolean,
  pgEnum,
  uuid,
} from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// Session storage table for Replit Auth
export const sessions = pgTable(
  "sessions",
  {
    sid: varchar("sid").primaryKey(),
    sess: jsonb("sess").notNull(),
    expire: timestamp("expire").notNull(),
  },
  (table) => [index("IDX_session_expire").on(table.expire)],
);

// Enums
export const userRoleEnum = pgEnum("user_role", ["retailer", "distributor", "manufacturer", "admin"]);
export const orderStatusEnum = pgEnum("order_status", ["pending", "confirmed", "packed", "out_for_delivery", "delivered", "cancelled"]);
export const deliveryModeEnum = pgEnum("delivery_mode", ["pickup", "delivery"]);

// User table
export const users = pgTable("users", {
  id: uuid("id").primaryKey().default(sql`gen_random_uuid()`),
  email: varchar("email").unique(),
  firstName: varchar("first_name"),
  lastName: varchar("last_name"),
  profileImageUrl: varchar("profile_image_url"),
  role: userRoleEnum("role").notNull().default("retailer"),
  businessName: text("business_name"),
  address: text("address"),
  phoneNumber: varchar("phone_number"),
  whatsappNumber: varchar("whatsapp_number"),
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// Categories table
export const categories = pgTable("categories", {
  id: uuid("id").primaryKey().default(sql`gen_random_uuid()`),
  name: varchar("name").notNull(),
  description: text("description"),
  createdAt: timestamp("created_at").defaultNow(),
});

// Products table
export const products = pgTable("products", {
  id: uuid("id").primaryKey().default(sql`gen_random_uuid()`),
  name: varchar("name").notNull(),
  description: text("description"),
  sku: varchar("sku").notNull().unique(),
  categoryId: uuid("category_id").references(() => categories.id),
  manufacturerId: uuid("manufacturer_id").references(() => users.id),
  imageUrl: text("image_url"),
  basePrice: decimal("base_price", { precision: 10, scale: 2 }),
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// Distributor inventory
export const inventory = pgTable("inventory", {
  id: uuid("id").primaryKey().default(sql`gen_random_uuid()`),
  distributorId: uuid("distributor_id").references(() => users.id),
  productId: uuid("product_id").references(() => products.id),
  quantity: integer("quantity").notNull().default(0),
  sellingPrice: decimal("selling_price", { precision: 10, scale: 2 }),
  isAvailable: boolean("is_available").default(true),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// Orders table
export const orders = pgTable("orders", {
  id: uuid("id").primaryKey().default(sql`gen_random_uuid()`),
  orderNumber: varchar("order_number").notNull().unique(),
  retailerId: uuid("retailer_id").references(() => users.id),
  distributorId: uuid("distributor_id").references(() => users.id),
  status: orderStatusEnum("status").default("pending"),
  deliveryMode: deliveryModeEnum("delivery_mode").default("delivery"),
  totalAmount: decimal("total_amount", { precision: 10, scale: 2 }),
  notes: text("notes"),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// Order items table
export const orderItems = pgTable("order_items", {
  id: uuid("id").primaryKey().default(sql`gen_random_uuid()`),
  orderId: uuid("order_id").references(() => orders.id),
  productId: uuid("product_id").references(() => products.id),
  quantity: integer("quantity").notNull(),
  unitPrice: decimal("unit_price", { precision: 10, scale: 2 }),
  totalPrice: decimal("total_price", { precision: 10, scale: 2 }),
});

// Invoices table
export const invoices = pgTable("invoices", {
  id: uuid("id").primaryKey().default(sql`gen_random_uuid()`),
  invoiceNumber: varchar("invoice_number").notNull().unique(),
  orderId: uuid("order_id").references(() => orders.id),
  pdfUrl: text("pdf_url"),
  sentAt: timestamp("sent_at"),
  createdAt: timestamp("created_at").defaultNow(),
});

// WhatsApp notifications table
export const whatsappNotifications = pgTable("whatsapp_notifications", {
  id: uuid("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: uuid("user_id").references(() => users.id),
  message: text("message").notNull(),
  type: varchar("type").notNull(), // order_update, invoice_sent, etc.
  sentAt: timestamp("sent_at"),
  isDelivered: boolean("is_delivered").default(false),
  createdAt: timestamp("created_at").defaultNow(),
});

// Relations
export const userRelations = relations(users, ({ many }) => ({
  products: many(products),
  inventory: many(inventory),
  retailerOrders: many(orders, { relationName: "retailerOrders" }),
  distributorOrders: many(orders, { relationName: "distributorOrders" }),
  notifications: many(whatsappNotifications),
}));

export const categoryRelations = relations(categories, ({ many }) => ({
  products: many(products),
}));

export const productRelations = relations(products, ({ one, many }) => ({
  category: one(categories, {
    fields: [products.categoryId],
    references: [categories.id],
  }),
  manufacturer: one(users, {
    fields: [products.manufacturerId],
    references: [users.id],
  }),
  inventory: many(inventory),
  orderItems: many(orderItems),
}));

export const inventoryRelations = relations(inventory, ({ one }) => ({
  distributor: one(users, {
    fields: [inventory.distributorId],
    references: [users.id],
  }),
  product: one(products, {
    fields: [inventory.productId],
    references: [products.id],
  }),
}));

export const orderRelations = relations(orders, ({ one, many }) => ({
  retailer: one(users, {
    fields: [orders.retailerId],
    references: [users.id],
    relationName: "retailerOrders",
  }),
  distributor: one(users, {
    fields: [orders.distributorId],
    references: [users.id],
    relationName: "distributorOrders",
  }),
  orderItems: many(orderItems),
  invoice: one(invoices),
}));

export const orderItemRelations = relations(orderItems, ({ one }) => ({
  order: one(orders, {
    fields: [orderItems.orderId],
    references: [orders.id],
  }),
  product: one(products, {
    fields: [orderItems.productId],
    references: [products.id],
  }),
}));

export const invoiceRelations = relations(invoices, ({ one }) => ({
  order: one(orders, {
    fields: [invoices.orderId],
    references: [orders.id],
  }),
}));

export const whatsappNotificationRelations = relations(whatsappNotifications, ({ one }) => ({
  user: one(users, {
    fields: [whatsappNotifications.userId],
    references: [users.id],
  }),
}));

// Insert schemas
export const insertUserSchema = createInsertSchema(users).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const insertCategorySchema = createInsertSchema(categories).omit({
  id: true,
  createdAt: true,
});

export const insertProductSchema = createInsertSchema(products).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const insertInventorySchema = createInsertSchema(inventory).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const insertOrderSchema = createInsertSchema(orders).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const insertOrderItemSchema = createInsertSchema(orderItems).omit({
  id: true,
});

// Business partnerships/connections table
export const partnerships = pgTable("partnerships", {
  id: uuid("id").primaryKey().default(sql`gen_random_uuid()`),
  requesterId: uuid("requester_id").notNull().references(() => users.id),
  partnerId: uuid("partner_id").notNull().references(() => users.id),
  status: varchar("status", { enum: ["pending", "approved", "rejected"] }).notNull().default("pending"),
  partnershipType: varchar("partnership_type", { enum: ["supplier", "distributor", "retailer"] }).notNull(),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow(),
});

// Favorites table for users to save their preferred partners
export const favorites = pgTable("favorites", {
  id: uuid("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: uuid("user_id").notNull().references(() => users.id),
  favoriteUserId: uuid("favorite_user_id").notNull().references(() => users.id),
  favoriteType: varchar("favorite_type", { enum: ["manufacturer", "distributor", "retailer"] }).notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

// Product search history for better recommendations
export const searchHistory = pgTable("search_history", {
  id: uuid("id").primaryKey().default(sql`gen_random_uuid()`),
  userId: uuid("user_id").notNull().references(() => users.id),
  searchTerm: varchar("search_term").notNull(),
  searchType: varchar("search_type", { enum: ["product", "manufacturer", "distributor"] }).notNull(),
  resultCount: integer("result_count").notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

export const insertInvoiceSchema = createInsertSchema(invoices).omit({
  id: true,
  createdAt: true,
});

export const insertPartnershipSchema = createInsertSchema(partnerships).omit({
  id: true,
  createdAt: true,
  updatedAt: true,
});

export const insertFavoriteSchema = createInsertSchema(favorites).omit({
  id: true,
  createdAt: true,
});

export const insertSearchHistorySchema = createInsertSchema(searchHistory).omit({
  id: true,
  createdAt: true,
});

// Types
export type UpsertUser = typeof users.$inferInsert;
export type User = typeof users.$inferSelect;

export const partnershipsRelations = relations(partnerships, ({ one }) => ({
  requester: one(users, {
    fields: [partnerships.requesterId],
    references: [users.id],
    relationName: "partnershipRequester",
  }),
  partner: one(users, {
    fields: [partnerships.partnerId],
    references: [users.id],
    relationName: "partnershipPartner",
  }),
}));

export const favoritesRelations = relations(favorites, ({ one }) => ({
  user: one(users, {
    fields: [favorites.userId],
    references: [users.id],
    relationName: "favoriteUser",
  }),
  favoriteUser: one(users, {
    fields: [favorites.favoriteUserId],
    references: [users.id],
    relationName: "favoritedUser",
  }),
}));

export const searchHistoryRelations = relations(searchHistory, ({ one }) => ({
  user: one(users, {
    fields: [searchHistory.userId],
    references: [users.id],
  }),
}));

export const usersRelations = relations(users, ({ many }) => ({
  sentPartnershipRequests: many(partnerships, { relationName: "partnershipRequester" }),
  receivedPartnershipRequests: many(partnerships, { relationName: "partnershipPartner" }),
  manufacturerProducts: many(products),
  distributorInventory: many(inventory),
  customerOrders: many(orders, { relationName: "customerOrders" }),
  supplierOrders: many(orders, { relationName: "supplierOrders" }),
  favorites: many(favorites, { relationName: "favoriteUser" }),
  favoritedBy: many(favorites, { relationName: "favoritedUser" }),
  searchHistory: many(searchHistory),
}));

export type Partnership = typeof partnerships.$inferSelect;
export type InsertPartnership = typeof partnerships.$inferInsert;
export type Favorite = typeof favorites.$inferSelect;
export type InsertFavorite = typeof favorites.$inferInsert;
export type SearchHistory = typeof searchHistory.$inferSelect;
export type InsertSearchHistory = typeof searchHistory.$inferInsert;
export type InsertUser = z.infer<typeof insertUserSchema>;
export type Category = typeof categories.$inferSelect;
export type InsertCategory = z.infer<typeof insertCategorySchema>;
export type Product = typeof products.$inferSelect;
export type InsertProduct = z.infer<typeof insertProductSchema>;
export type Inventory = typeof inventory.$inferSelect;
export type InsertInventory = z.infer<typeof insertInventorySchema>;
export type Order = typeof orders.$inferSelect;
export type InsertOrder = z.infer<typeof insertOrderSchema>;
export type OrderItem = typeof orderItems.$inferSelect;
export type InsertOrderItem = z.infer<typeof insertOrderItemSchema>;
export type Invoice = typeof invoices.$inferSelect;
export type InsertInvoice = z.infer<typeof insertInvoiceSchema>;
export type WhatsappNotification = typeof whatsappNotifications.$inferSelect;
