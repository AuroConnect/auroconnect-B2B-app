import { sql, relations } from "drizzle-orm";
import {
  index,
  json,
  mysqlTable,
  timestamp,
  varchar,
  text,
  int,
  decimal,
  boolean,
  mysqlEnum,
  char,
} from "drizzle-orm/mysql-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

// Session storage table for Replit Auth
export const sessions = mysqlTable(
  "sessions",
  {
    sid: varchar("sid", { length: 255 }).primaryKey(),
    sess: json("sess").notNull(),
    expire: timestamp("expire").notNull(),
  },
  (table) => [index("IDX_session_expire").on(table.expire)],
);

// Enums
export const userRoleEnum = mysqlEnum("user_role", ["retailer", "distributor", "manufacturer", "admin"]);
export const orderStatusEnum = mysqlEnum("order_status", ["pending", "confirmed", "packed", "out_for_delivery", "delivered", "cancelled"]);
export const deliveryModeEnum = mysqlEnum("delivery_mode", ["pickup", "delivery"]);

// User table
export const users = mysqlTable("users", {
  id: char("id", { length: 36 }).primaryKey().default(sql`(UUID())`),
  email: varchar("email", { length: 255 }).unique(),
  firstName: varchar("first_name", { length: 255 }),
  lastName: varchar("last_name", { length: 255 }),
  profileImageUrl: varchar("profile_image_url", { length: 500 }),
  role: userRoleEnum("role").notNull().default("retailer"),
  businessName: text("business_name"),
  address: text("address"),
  phoneNumber: varchar("phone_number", { length: 50 }),
  whatsappNumber: varchar("whatsapp_number", { length: 50 }),
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow(),
});

// Categories table
export const categories = mysqlTable("categories", {
  id: char("id", { length: 36 }).primaryKey().default(sql`(UUID())`),
  name: varchar("name", { length: 255 }).notNull(),
  description: text("description"),
  createdAt: timestamp("created_at").defaultNow(),
});

// Products table
export const products = mysqlTable("products", {
  id: char("id", { length: 36 }).primaryKey().default(sql`(UUID())`),
  name: varchar("name", { length: 255 }).notNull(),
  description: text("description"),
  sku: varchar("sku", { length: 255 }).notNull().unique(),
  categoryId: char("category_id", { length: 36 }).references(() => categories.id),
  manufacturerId: char("manufacturer_id", { length: 36 }).references(() => users.id),
  imageUrl: text("image_url"),
  basePrice: decimal("base_price", { precision: 10, scale: 2 }),
  isActive: boolean("is_active").default(true),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow(),
});

// Distributor inventory
export const inventory = mysqlTable("inventory", {
  id: char("id", { length: 36 }).primaryKey().default(sql`(UUID())`),
  distributorId: char("distributor_id", { length: 36 }).references(() => users.id),
  productId: char("product_id", { length: 36 }).references(() => products.id),
  quantity: int("quantity").notNull().default(0),
  sellingPrice: decimal("selling_price", { precision: 10, scale: 2 }),
  isAvailable: boolean("is_available").default(true),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow(),
});

// Orders table
export const orders = mysqlTable("orders", {
  id: char("id", { length: 36 }).primaryKey().default(sql`(UUID())`),
  orderNumber: varchar("order_number", { length: 255 }).notNull().unique(),
  retailerId: char("retailer_id", { length: 36 }).references(() => users.id),
  distributorId: char("distributor_id", { length: 36 }).references(() => users.id),
  status: orderStatusEnum("status").default("pending"),
  deliveryMode: deliveryModeEnum("delivery_mode").default("delivery"),
  totalAmount: decimal("total_amount", { precision: 10, scale: 2 }),
  notes: text("notes"),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow(),
});

// Order items table
export const orderItems = mysqlTable("order_items", {
  id: char("id", { length: 36 }).primaryKey().default(sql`(UUID())`),
  orderId: char("order_id", { length: 36 }).references(() => orders.id),
  productId: char("product_id", { length: 36 }).references(() => products.id),
  quantity: int("quantity").notNull(),
  unitPrice: decimal("unit_price", { precision: 10, scale: 2 }),
  totalPrice: decimal("total_price", { precision: 10, scale: 2 }),
});

// Invoices table
export const invoices = mysqlTable("invoices", {
  id: char("id", { length: 36 }).primaryKey().default(sql`(UUID())`),
  invoiceNumber: varchar("invoice_number", { length: 255 }).notNull().unique(),
  orderId: char("order_id", { length: 36 }).references(() => orders.id),
  pdfUrl: text("pdf_url"),
  sentAt: timestamp("sent_at"),
  createdAt: timestamp("created_at").defaultNow(),
});

// WhatsApp notifications table
export const whatsappNotifications = mysqlTable("whatsapp_notifications", {
  id: char("id", { length: 36 }).primaryKey().default(sql`(UUID())`),
  userId: char("user_id", { length: 36 }).references(() => users.id),
  message: text("message").notNull(),
  type: varchar("type", { length: 50 }).notNull(), // order_update, invoice_sent, etc.
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
export const partnerships = mysqlTable("partnerships", {
  id: char("id", { length: 36 }).primaryKey().default(sql`(UUID())`),
  requesterId: char("requester_id", { length: 36 }).notNull().references(() => users.id),
  partnerId: char("partner_id", { length: 36 }).notNull().references(() => users.id),
  status: varchar("status", { length: 50, enum: ["pending", "approved", "rejected"] }).notNull().default("pending"),
  partnershipType: varchar("partnership_type", { length: 50, enum: ["supplier", "distributor", "retailer"] }).notNull(),
  createdAt: timestamp("created_at").defaultNow(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow(),
});

// Favorites table for users to save their preferred partners
export const favorites = mysqlTable("favorites", {
  id: char("id", { length: 36 }).primaryKey().default(sql`(UUID())`),
  userId: char("user_id", { length: 36 }).notNull().references(() => users.id),
  favoriteUserId: char("favorite_user_id", { length: 36 }).notNull().references(() => users.id),
  favoriteType: varchar("favorite_type", { length: 50, enum: ["manufacturer", "distributor", "retailer"] }).notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});

// Product search history for better recommendations
export const searchHistory = mysqlTable("search_history", {
  id: char("id", { length: 36 }).primaryKey().default(sql`(UUID())`),
  userId: char("user_id", { length: 36 }).notNull().references(() => users.id),
  searchTerm: varchar("search_term", { length: 255 }).notNull(),
  searchType: varchar("search_type", { length: 50, enum: ["product", "manufacturer", "distributor"] }).notNull(),
  resultCount: int("result_count").notNull(),
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
