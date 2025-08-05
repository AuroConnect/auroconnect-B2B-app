# AuroMart - B2B Ordering & Billing Platform

## Overview

AuroMart is a comprehensive B2B ordering and billing platform that connects retailers, distributors, and manufacturers in a streamlined marketplace. The application facilitates instant product ordering, real-time inventory management, WhatsApp-based notifications, and automated invoice generation. Built as a full-stack TypeScript application with React frontend and Express backend, it serves as a modern solution for B2B commerce workflows.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: React 18 with TypeScript for type safety and modern development
- **Styling**: TailwindCSS with shadcn/ui component library providing consistent, accessible design system
- **Routing**: Wouter for lightweight client-side routing without heavy dependencies
- **State Management**: TanStack Query (React Query) for server state management and caching
- **Forms**: React Hook Form with Zod validation for type-safe form handling
- **UI Components**: Radix UI primitives wrapped in shadcn/ui for accessibility and customization

### Backend Architecture
- **Runtime**: Node.js with Express.js framework for REST API endpoints
- **Database**: PostgreSQL with Drizzle ORM for type-safe database operations
- **Authentication**: Replit Auth with OpenID Connect for secure user authentication
- **Session Management**: Express sessions with PostgreSQL store for persistent user sessions
- **API Design**: RESTful endpoints with consistent error handling and logging middleware

### Database Design
- **ORM**: Drizzle with code-first schema definition in TypeScript
- **Schema**: Multi-role user system (retailers, distributors, manufacturers, admin) with role-based access
- **Core Entities**: Users, Categories, Products, Inventory, Orders, Order Items, Invoices, WhatsApp Notifications
- **Relationships**: Proper foreign key constraints and joins for data integrity
- **Migrations**: Automated schema migrations through Drizzle Kit

### Authentication & Authorization
- **Provider**: Replit Auth integration with OpenID Connect protocol
- **Session Storage**: PostgreSQL-backed sessions for scalability and persistence
- **Role-Based Access**: Four distinct user roles with different capabilities and dashboard views
- **Security**: HTTP-only cookies, secure session management, and CSRF protection

### Build & Development
- **Bundling**: Vite for fast development builds and hot module replacement
- **Production**: ESBuild for optimized server bundling with external package handling
- **Development**: Concurrent client and server development with proxy setup
- **Deployment**: Single production build with static file serving

## External Dependencies

### Database Services
- **PostgreSQL**: Primary database hosted on Neon for serverless scaling
- **Connection**: Neon serverless driver with WebSocket support for edge compatibility

### Authentication Services
- **Replit Auth**: Integrated OpenID Connect provider for user authentication
- **Session Store**: PostgreSQL-based session storage with connect-pg-simple

### Communication Services
- **WhatsApp Integration**: Planned integration for order notifications and invoice delivery
- **File Generation**: PDF invoice generation for automated billing workflows

### UI & Styling Libraries
- **shadcn/ui**: Comprehensive component library built on Radix UI primitives
- **TailwindCSS**: Utility-first CSS framework with custom design tokens
- **Radix UI**: Low-level accessible component primitives for complex interactions

### Development & Build Tools
- **TypeScript**: Full-stack type safety with shared schema types
- **Vite**: Modern build tool with React plugin and development server
- **ESBuild**: Production server bundling for optimal performance
- **Drizzle Kit**: Database schema management and migration tools