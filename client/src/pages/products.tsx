import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";
import Header from "@/components/layout/header";
import MobileNav from "@/components/layout/mobile-nav";
import ProductGrid from "@/components/products/product-grid";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Search, Filter, Plus, Grid, List, Upload, Download, Edit, Trash2, Package, Eye, ShoppingCart, Heart, X } from "lucide-react";
import { useRef } from "react";
import type { User } from "@/hooks/useAuth";
import React from "react";

interface Product {
  id: string;
  name: string;
  description: string;
  basePrice: number;
  sku: string;
  categoryId: string;
  manufacturerId: string;
  imageUrl?: string;
  isActive: boolean;
  stockQuantity: number;
  createdAt?: string;
  updatedAt?: string;
  category?: {
    id: string;
    name: string;
  };
  manufacturer?: {
    id: string;
    businessName: string;
  };
}

interface Category {
  id: string;
  name: string;
  description?: string;
}

interface Favorite {
  id: string;
  productId: string;
  userId: string;
}

export default function Products() {
  const { user, isLoading, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [sortBy, setSortBy] = useState("name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [selectedManufacturer, setSelectedManufacturer] = useState("all");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const bulkUploadRef = useRef<HTMLInputElement>(null);
  
  // Get user role early to avoid hoisting issues
  const userRole = (user as User)?.role || 'retailer';

  // Add Product Form State
  const [newProduct, setNewProduct] = useState({
    name: "",
    description: "",
    sku: "",
    categoryId: "",
    basePrice: "",
    stockQuantity: "",
    imageUrl: "",
    brand: "",
    unit: "pcs"
  });

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      toast({
        title: "Authentication Required",
        description: "Please log in to access the products page.",
        variant: "destructive",
      });
      setTimeout(() => {
        window.location.href = "/";
      }, 2000);
      return;
    }
  }, [isAuthenticated, isLoading, toast]);

  const { data: categories, isLoading: categoriesLoading, error: categoriesError } = useQuery<Category[]>({
    queryKey: ["api", "products", "categories"],
    enabled: !!isAuthenticated && !!user,
    retry: 3,
    staleTime: 30000,
  });

  // Get manufacturers for distributor filter
  const { data: manufacturers, isLoading: manufacturersLoading } = useQuery<any[]>({
    queryKey: ["api", "manufacturers"],
    enabled: !!isAuthenticated && !!user && userRole === 'distributor',
    retry: 3,
    staleTime: 30000,
  });

  const { data: products, isLoading: productsLoading, error: productsError } = useQuery<Product[]>({
    queryKey: ["api", "products", selectedCategory === "all" ? "" : `?categoryId=${selectedCategory}`],
    enabled: !!isAuthenticated && !!user,
    retry: 3,
    staleTime: 30000,
  });

  const { data: favorites = [], isLoading: favoritesLoading } = useQuery<Favorite[]>({
    queryKey: ["api", "favorites"],
    enabled: !!isAuthenticated && !!user,
  });

  // Add Product Mutation
  const addProductMutation = useMutation({
    mutationFn: async (productData: any) => {
      const response = await apiRequest("POST", "/api/products", productData);
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Product Added",
        description: "Product has been successfully added to your catalog.",
      });
      queryClient.invalidateQueries({ queryKey: ["api", "products"] });
      setIsAddDialogOpen(false);
      setNewProduct({
        name: "",
        description: "",
        sku: "",
        categoryId: "",
        basePrice: "",
        stockQuantity: "",
        imageUrl: "",
        brand: "",
        unit: "pcs"
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to add product.",
        variant: "destructive",
      });
    },
  });

  // Bulk Upload Mutation
  const bulkUploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiRequest("POST", "/api/products/bulk-upload", formData, true);
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Bulk Upload Complete",
        description: `${data.added} products added, ${data.failed} failed.`,
      });
      queryClient.invalidateQueries({ queryKey: ["api", "products"] });
    },
    onError: (error: any) => {
      toast({
        title: "Bulk Upload Failed",
        description: error.message || "Failed to upload products.",
        variant: "destructive",
      });
    },
  });

  // Filter and sort products
  const filteredAndSortedProducts = React.useMemo(() => {
    if (!products || !Array.isArray(products)) return [];
    
    // First filter by category
    let filtered = products;
    if (selectedCategory !== "all") {
      filtered = products.filter((product: Product) => 
        product.categoryId === selectedCategory
      );
    }
    
    // Filter by manufacturer (for distributors)
    if (userRole === 'distributor' && selectedManufacturer !== "all") {
      filtered = filtered.filter((product: Product) => 
        product.manufacturerId === selectedManufacturer
      );
    }
    
    // Then filter by search term
    filtered = filtered.filter((product: Product) =>
      product.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      product.sku?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    
    // Then sort
    filtered.sort((a: Product, b: Product) => {
      let aValue: any, bValue: any;
      
      switch (sortBy) {
        case "name":
          aValue = a.name?.toLowerCase() || "";
          bValue = b.name?.toLowerCase() || "";
          break;
        case "price":
          aValue = a.basePrice || 0;
          bValue = b.basePrice || 0;
          break;
                 case "createdAt":
           aValue = a.createdAt ? new Date(a.createdAt).getTime() : 0;
           bValue = b.createdAt ? new Date(b.createdAt).getTime() : 0;
           break;
        default:
          aValue = a.name?.toLowerCase() || "";
          bValue = b.name?.toLowerCase() || "";
      }
      
      if (sortOrder === "asc") {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
    
    return filtered;
  }, [products, searchTerm, selectedCategory, sortBy, sortOrder]);

  const handleAddProduct = () => {
    if (!newProduct.name || !newProduct.sku || !newProduct.basePrice) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields.",
        variant: "destructive",
      });
      return;
    }

    const productData = {
      name: newProduct.name,
      description: newProduct.description,
      sku: newProduct.sku,
      categoryId: newProduct.categoryId || null,
      basePrice: parseFloat(newProduct.basePrice),
      stockQuantity: parseInt(newProduct.stockQuantity) || 0,
      imageUrl: newProduct.imageUrl || null,
      brand: newProduct.brand,
      unit: newProduct.unit
    };

    addProductMutation.mutate(productData);
  };

  const handleBulkUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      if (file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' || 
          file.type === 'application/vnd.ms-excel') {
        bulkUploadMutation.mutate(file);
      } else {
        toast({
          title: "Invalid File",
          description: "Please upload an Excel file (.xlsx or .xls).",
          variant: "destructive",
        });
      }
    }
  };

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen auromart-gradient-bg flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading products...</p>
        </div>
      </div>
    );
  }

  // Show authentication required message
  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen auromart-gradient-bg flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
            <Package className="h-8 w-8 text-white" />
          </div>
          <h2 className="text-xl font-semibold text-white mb-2">Authentication Required</h2>
          <p className="text-white/80">Please log in to access the products page.</p>
        </div>
      </div>
    );
  }

  // Handle API errors
  if (productsError || categoriesError) {
    console.error('Products Error:', productsError);
    console.error('Categories Error:', categoriesError);
    return (
      <div className="min-h-screen auromart-gradient-bg flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Package className="h-8 w-8 text-red-600" />
          </div>
          <h2 className="text-xl font-semibold text-white mb-2">Error Loading Products</h2>
          <p className="text-white/80 mb-4">Unable to load products. Please try again.</p>
          <Button 
            onClick={() => window.location.reload()} 
            className="bg-white text-gray-900 hover:bg-gray-100"
          >
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Products</h1>
            <p className="text-gray-600 mt-2">
              {userRole === 'manufacturer' ? 'Manage your product catalog' : 
               userRole === 'distributor' ? 'Browse manufacturer products' : 
               'Browse distributor products'}
            </p>
          </div>
          
          {userRole === 'manufacturer' && (
            <div className="flex gap-3 mt-4 sm:mt-0">
              <Button 
                onClick={() => setIsAddDialogOpen(true)}
                className="action-button-primary"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add Product
              </Button>
              <Button variant="outline" onClick={() => bulkUploadRef.current?.click()}>
                <Upload className="h-4 w-4 mr-2" />
                Bulk Upload
              </Button>
              <input
                ref={bulkUploadRef}
                type="file"
                accept=".xlsx,.xls"
                className="hidden"
                onChange={handleBulkUpload}
              />
            </div>
          )}
        </div>

        {/* Search and Filter Bar */}
        <Card className="mb-6">
          <CardContent className="p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search products..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>

              {/* Category Filter */}
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-full sm:w-48">
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories?.map((category: Category) => (
                    <SelectItem key={category.id} value={category.id}>
                      {category.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Manufacturer Filter (for distributors only) */}
              {userRole === 'distributor' && (
                <Select value={selectedManufacturer} onValueChange={setSelectedManufacturer}>
                  <SelectTrigger className="w-full sm:w-48">
                    <SelectValue placeholder="All Manufacturers" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Manufacturers</SelectItem>
                    {manufacturers?.map((manufacturer: any) => (
                      <SelectItem key={manufacturer.id} value={manufacturer.id}>
                        {manufacturer.businessName}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}

              {/* Sort */}
              <Select value={`${sortBy}-${sortOrder}`} onValueChange={(value) => {
                const [field, order] = value.split('-');
                setSortBy(field);
                setSortOrder(order as "asc" | "desc");
              }}>
                <SelectTrigger className="w-full sm:w-48">
                  <SelectValue placeholder="Sort by" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="name-asc">Name (A-Z)</SelectItem>
                  <SelectItem value="name-desc">Name (Z-A)</SelectItem>
                  <SelectItem value="price-asc">Price (Low to High)</SelectItem>
                  <SelectItem value="price-desc">Price (High to Low)</SelectItem>
                  <SelectItem value="createdAt-asc">Date Added (Oldest First)</SelectItem>
                  <SelectItem value="createdAt-desc">Date Added (Newest First)</SelectItem>
                </SelectContent>
              </Select>

              {/* View Mode Toggle */}
              <div className="flex border rounded-md">
                <Button
                  variant={viewMode === "grid" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setViewMode("grid")}
                  className="rounded-r-none"
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === "list" ? "default" : "ghost"}
                  size="sm"
                  onClick={() => setViewMode("list")}
                  className="rounded-l-none"
                >
                  <List className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Products Display */}
        <ProductGrid 
          products={filteredAndSortedProducts} 
          isLoading={productsLoading || categoriesLoading}
          userRole={userRole}
          categories={categories || []}
        />
      </div>

      {/* Add Product Dialog */}
      <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
        <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Add New Product</DialogTitle>
            <DialogDescription>
              Add a new product to your catalog. Fill in the required information below.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-6">
            {/* Product Name */}
            <div className="space-y-2">
              <Label htmlFor="name" className="text-sm font-medium">
                Product Name *
              </Label>
              <Input
                id="name"
                value={newProduct.name}
                onChange={(e) => setNewProduct(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Enter product name"
                className="w-full"
              />
            </div>

            {/* SKU and Category */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="sku" className="text-sm font-medium">
                  SKU *
                </Label>
                <Input
                  id="sku"
                  value={newProduct.sku}
                  onChange={(e) => setNewProduct(prev => ({ ...prev, sku: e.target.value }))}
                  placeholder="Enter SKU"
                  className="w-full"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="category" className="text-sm font-medium">
                  Category
                </Label>
                <Select value={newProduct.categoryId} onValueChange={(value) => setNewProduct(prev => ({ ...prev, categoryId: value }))}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories?.map((category: Category) => (
                      <SelectItem key={category.id} value={category.id}>
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Brand and Unit */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="brand" className="text-sm font-medium">
                  Brand
                </Label>
                <Input
                  id="brand"
                  value={newProduct.brand}
                  onChange={(e) => setNewProduct(prev => ({ ...prev, brand: e.target.value }))}
                  placeholder="Enter brand name"
                  className="w-full"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="unit" className="text-sm font-medium">
                  Unit
                </Label>
                <Select value={newProduct.unit} onValueChange={(value) => setNewProduct(prev => ({ ...prev, unit: value }))}>
                  <SelectTrigger className="w-full">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pcs">Pieces</SelectItem>
                    <SelectItem value="kg">Kilograms</SelectItem>
                    <SelectItem value="m">Meters</SelectItem>
                    <SelectItem value="l">Liters</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="description" className="text-sm font-medium">
                Description
              </Label>
              <Textarea
                id="description"
                value={newProduct.description}
                onChange={(e) => setNewProduct(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Enter product description"
                className="w-full min-h-[100px]"
              />
            </div>

            {/* Price and Stock */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="price" className="text-sm font-medium">
                  Base Price *
                </Label>
                <Input
                  id="price"
                  type="number"
                  step="0.01"
                  min="0"
                  value={newProduct.basePrice}
                  onChange={(e) => setNewProduct(prev => ({ ...prev, basePrice: e.target.value }))}
                  placeholder="0.00"
                  className="w-full"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="stock" className="text-sm font-medium">
                  Stock Quantity
                </Label>
                <Input
                  id="stock"
                  type="number"
                  min="0"
                  value={newProduct.stockQuantity}
                  onChange={(e) => setNewProduct(prev => ({ ...prev, stockQuantity: e.target.value }))}
                  placeholder="0"
                  className="w-full"
                />
              </div>
            </div>

            {/* Image Upload */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">
                Product Image
              </Label>
              <div className="space-y-3">
                {/* Image URL Option */}
                <div>
                  <Label htmlFor="imageUrl" className="text-xs text-gray-600">
                    Image URL (Google Drive, Unsplash, etc.)
                  </Label>
                  <Input
                    id="imageUrl"
                    type="url"
                    value={newProduct.imageUrl}
                    onChange={(e) => setNewProduct(prev => ({ ...prev, imageUrl: e.target.value }))}
                    placeholder="https://drive.google.com/... or https://images.unsplash.com/..."
                    className="w-full"
                  />
                </div>
                
                {/* File Upload Option */}
                <div>
                  <Label htmlFor="imageFile" className="text-xs text-gray-600">
                    Or Upload Image File (JPEG, PNG, GIF)
                  </Label>
                  <div className="flex gap-2">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => fileInputRef.current?.click()}
                      className="flex-1"
                    >
                      <Upload className="h-4 w-4 mr-2" />
                      Choose File
                    </Button>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="image/jpeg,image/png,image/gif"
                      className="hidden"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          // For now, we'll create a local URL for preview
                          // In a real app, you'd upload to a server
                          const imageUrl = URL.createObjectURL(file);
                          setNewProduct(prev => ({ ...prev, imageUrl }));
                        }
                      }}
                    />
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Supported formats: JPEG, PNG, GIF (no size limit)
                  </p>
                </div>
                
                {/* Image Preview */}
                {newProduct.imageUrl && (
                  <div className="mt-2">
                    <Label className="text-xs text-gray-600">Preview:</Label>
                    <div className="mt-1 w-32 h-32 border rounded-lg overflow-hidden">
                      <img
                        src={newProduct.imageUrl}
                        alt="Product preview"
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none';
                        }}
                      />
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleAddProduct}
              disabled={addProductMutation.isPending}
              className="action-button-primary"
            >
              {addProductMutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Adding...
                </>
              ) : (
                "Add Product"
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      
      <MobileNav />
    </div>
  );
}
