import { useState, useEffect, useRef, useMemo } from "react";
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
import { Search, Filter, Plus, Grid, List, Upload, Download, Edit, Trash2, Package, Eye, ShoppingCart, Heart, X, FileSpreadsheet, Settings, Bell, FileText, AlertTriangle, TrendingUp, TrendingDown, BarChart3, AlertCircle, CheckCircle, XCircle } from "lucide-react";
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
    unit: "pcs",
    assignedDistributors: [] as string[],
    assignedRetailers: [] as string[]
  });

  // Bulk Upload State
  const [isBulkUploadOpen, setIsBulkUploadOpen] = useState(false);
  const [bulkFile, setBulkFile] = useState<File | null>(null);
  const [bulkUploadResults, setBulkUploadResults] = useState<any[]>([]);
  const [isBulkUploading, setIsBulkUploading] = useState(false);
  const [showBulkResults, setShowBulkResults] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(10);

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

  // Get distributors for manufacturer assignment
  const { data: distributors = [], isLoading: distributorsLoading } = useQuery<any[]>({
    queryKey: ["api", "partners", "distributors"],
    enabled: !!isAuthenticated && !!user && userRole === 'manufacturer',
    retry: 3,
    staleTime: 30000,
  });

  // Get retailers for distributor assignment
  const { data: retailers = [], isLoading: retailersLoading } = useQuery<any[]>({
    queryKey: ["api", "partners", "retailers"],
    enabled: !!isAuthenticated && !!user && userRole === 'distributor',
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

  // Add Product mutation
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
        unit: "pcs",
        assignedDistributors: [],
        assignedRetailers: []
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
      return response.json ? await response.json() : response;
    },
    onSuccess: (data) => {
      setBulkUploadResults(data.results || []);
      setShowBulkResults(true);
      setIsBulkUploading(false);
      queryClient.invalidateQueries({ queryKey: ["api", "products"] });
      toast({
        title: "Bulk Upload Complete",
        description: `Processed ${data.results?.length || 0} products`,
        variant: "default",
      });
    },
    onError: (error: any) => {
      setIsBulkUploading(false);
      toast({
        title: "Bulk Upload Failed",
        description: error.message || "Failed to upload products",
        variant: "destructive",
      });
    }
  });

  // Download Sample CSV
  const downloadSampleCSV = () => {
    const sampleData = [
      {
        name: "Premium Laptop",
        description: "High-performance laptop with latest specifications",
        sku: "LAPTOP001",
        categoryId: "",
        basePrice: "45000.00",
        imageUrl: "https://example.com/laptop1.jpg",
        assignedDistributors: ""
      },
      {
        name: "Wireless Mouse",
        description: "Ergonomic wireless mouse with precision tracking",
        sku: "MOUSE002",
        categoryId: "",
        basePrice: "1200.00",
        imageUrl: "https://example.com/mouse1.jpg",
        assignedDistributors: ""
      },
      {
        name: "Mechanical Keyboard",
        description: "RGB mechanical keyboard with customizable switches",
        sku: "KEYBOARD003",
        categoryId: "",
        basePrice: "3500.00",
        imageUrl: "https://example.com/keyboard1.jpg",
        assignedDistributors: ""
      },
      {
        name: "USB-C Hub",
        description: "Multi-port USB-C hub for laptop connectivity",
        sku: "HUB004",
        categoryId: "",
        basePrice: "2500.00",
        imageUrl: "https://example.com/hub1.jpg",
        assignedDistributors: ""
      }
    ];

    const csvContent = [
      "name,description,sku,categoryId,basePrice,imageUrl,assignedDistributors",
      ...sampleData.map(row => 
        `"${row.name}","${row.description}","${row.sku}","${row.categoryId}","${row.basePrice}","${row.imageUrl}","${row.assignedDistributors}"`
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_products.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  // Download Error CSV
  const downloadErrorCSV = () => {
    const errorData = bulkUploadResults
      .filter(result => result.status === 'error')
      .map(result => ({
        row: result.row,
        name: result.name || 'N/A',
        error: result.error,
        status: 'ERROR'
      }));

    if (errorData.length === 0) {
      toast({
        title: "No Errors",
        description: "There are no errors to download.",
        variant: "default",
      });
      return;
    }

    const csvContent = [
      "row,name,error,status",
      ...errorData.map(row => 
        `"${row.row}","${row.name}","${row.error}","${row.status}"`
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'bulk_upload_errors.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const handleBulkUpload = () => {
    if (!bulkFile) {
      toast({
        title: "No File Selected",
        description: "Please select a CSV or Excel file to upload",
        variant: "destructive",
      });
      return;
    }

    setIsBulkUploading(true);
    bulkUploadMutation.mutate(bulkFile);
  };

  // Filter and sort products
  const filteredAndSortedProducts = useMemo(() => {
    if (!products || !Array.isArray(products)) return [];
    
    let filtered = products;
    
    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(product => 
        product.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.sku?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Apply category filter
    if (selectedCategory !== "all") {
      filtered = filtered.filter(product => product.categoryId === selectedCategory);
    }
    
    // Apply manufacturer filter for distributors
    if (userRole === 'distributor' && selectedManufacturer !== "all") {
      filtered = filtered.filter(product => product.manufacturerId === selectedManufacturer);
    }
    
    // Sort products
    filtered.sort((a, b) => {
      switch (sortBy) {
        case "name":
          return sortOrder === "asc" 
            ? (a.name || "").localeCompare(b.name || "")
            : (b.name || "").localeCompare(a.name || "");
        case "price":
          return sortOrder === "asc" 
            ? (a.basePrice || 0) - (b.basePrice || 0)
            : (b.basePrice || 0) - (a.basePrice || 0);
        case "sku":
          return sortOrder === "asc" 
            ? (a.sku || "").localeCompare(b.sku || "")
            : (b.sku || "").localeCompare(a.sku || "");
        default:
          return 0;
      }
    });
    
    return filtered;
  }, [products, searchTerm, selectedCategory, selectedManufacturer, sortBy, sortOrder, userRole]);

  // Pagination
  const totalPages = Math.ceil(filteredAndSortedProducts.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedProducts = filteredAndSortedProducts.slice(startIndex, endIndex);

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
      basePrice: parseFloat(newProduct.basePrice),
      categoryId: newProduct.categoryId || null,
      imageUrl: newProduct.imageUrl || null,
      brand: newProduct.brand || null,
      unit: newProduct.unit,
      assignedDistributors: userRole === 'manufacturer' ? newProduct.assignedDistributors : [],
      assignedRetailers: userRole === 'distributor' ? newProduct.assignedRetailers : []
    };

    addProductMutation.mutate(productData);
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
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) {
                    setBulkFile(file);
                  }
                }}
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
          products={paginatedProducts} 
          isLoading={productsLoading || categoriesLoading}
          userRole={userRole}
          categories={categories || []}
        />

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between mt-8">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-700">
                Showing {startIndex + 1} to {Math.min(endIndex, filteredAndSortedProducts.length)} of {filteredAndSortedProducts.length} products
              </span>
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              <div className="flex items-center space-x-1">
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  const pageNum = i + 1;
                  return (
                    <Button
                      key={pageNum}
                      variant={currentPage === pageNum ? "default" : "outline"}
                      size="sm"
                      onClick={() => setCurrentPage(pageNum)}
                      className="w-8 h-8 p-0"
                    >
                      {pageNum}
                    </Button>
                  );
                })}
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                disabled={currentPage === totalPages}
              >
                Next
              </Button>
            </div>
          </div>
        )}
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

            {/* Distributor Assignment (for manufacturers) */}
            {userRole === 'manufacturer' && (
              <div className="space-y-2">
                <Label htmlFor="distributors" className="text-sm font-medium">
                  Assign to Distributors
                </Label>
                <div className="space-y-2">
                  {distributors?.map((distributor: any) => (
                    <div key={distributor.id} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={`dist-${distributor.id}`}
                        checked={newProduct.assignedDistributors.includes(distributor.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNewProduct(prev => ({
                              ...prev,
                              assignedDistributors: [...prev.assignedDistributors, distributor.id]
                            }));
                          } else {
                            setNewProduct(prev => ({
                              ...prev,
                              assignedDistributors: prev.assignedDistributors.filter(id => id !== distributor.id)
                            }));
                          }
                        }}
                        className="rounded"
                      />
                      <Label htmlFor={`dist-${distributor.id}`} className="text-sm">
                        {distributor.businessName || `${distributor.firstName} ${distributor.lastName}`}
                      </Label>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-gray-500">
                  Product will be visible only to selected distributors
                </p>
              </div>
            )}

            {userRole === 'distributor' && (
              <div className="space-y-2">
                <Label htmlFor="retailers" className="text-sm font-medium">
                  Assign to Retailers
                </Label>
                <div className="space-y-2">
                  {retailers?.map((retailer: any) => (
                    <div key={retailer.id} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id={`ret-${retailer.id}`}
                        checked={newProduct.assignedRetailers.includes(retailer.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setNewProduct(prev => ({
                              ...prev,
                              assignedRetailers: [...prev.assignedRetailers, retailer.id]
                            }));
                          } else {
                            setNewProduct(prev => ({
                              ...prev,
                              assignedRetailers: prev.assignedRetailers.filter(id => id !== retailer.id)
                            }));
                          }
                        }}
                        className="rounded"
                      />
                      <Label htmlFor={`ret-${retailer.id}`} className="text-sm">
                        {retailer.businessName || `${retailer.firstName} ${retailer.lastName}`}
                      </Label>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-gray-500">
                  Product will be visible only to selected retailers
                </p>
              </div>
            )}
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
      
      {/* Bulk Upload Dialog */}
      <Dialog open={isBulkUploadOpen} onOpenChange={setIsBulkUploadOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Bulk Upload Products</DialogTitle>
            <DialogDescription>
              Upload multiple products using CSV or Excel file
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h4 className="font-medium">Download Sample File</h4>
                <p className="text-sm text-gray-500">Get the correct format for bulk upload</p>
              </div>
              <Button onClick={downloadSampleCSV} variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Download Sample CSV
              </Button>
            </div>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  {bulkFile ? bulkFile.name : "Drop your CSV or Excel file here, or click to browse"}
                </p>
                <input
                  type="file"
                  accept=".csv,.xlsx,.xls"
                  onChange={(e) => setBulkFile(e.target.files?.[0] || null)}
                  className="hidden"
                  id="bulk-upload"
                />
                <label htmlFor="bulk-upload" className="cursor-pointer">
                  <Button variant="outline" size="sm">
                    Choose File
                  </Button>
                </label>
              </div>
            </div>
            
            {bulkFile && (
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <FileSpreadsheet className="h-5 w-5 text-blue-500" />
                  <span className="text-sm font-medium">{bulkFile.name}</span>
                  <span className="text-xs text-gray-500">
                    ({(bulkFile.size / 1024).toFixed(1)} KB)
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setBulkFile(null)}
                >
                  <XCircle className="h-4 w-4" />
                </Button>
              </div>
            )}
          </div>
          
          <div className="flex justify-end gap-2 pt-4">
            <Button variant="outline" onClick={() => setIsBulkUploadOpen(false)}>
              Cancel
            </Button>
            <Button 
              onClick={handleBulkUpload}
              disabled={!bulkFile || isBulkUploading}
            >
              {isBulkUploading ? "Uploading..." : "Upload Products"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Bulk Upload Results Dialog */}
      <Dialog open={showBulkResults} onOpenChange={setShowBulkResults}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Bulk Upload Results</DialogTitle>
            <DialogDescription>
              Results of your bulk product upload
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
                          <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-sm">
                      {bulkUploadResults.filter(r => r.status === 'success').length} Successful
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <XCircle className="h-4 w-4 text-red-500" />
                    <span className="text-sm">
                      {bulkUploadResults.filter(r => r.status === 'error').length} Failed
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {bulkUploadResults.filter(r => r.status === 'error').length > 0 && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={downloadErrorCSV}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download Errors
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setShowBulkResults(false);
                      setBulkUploadResults([]);
                      setBulkFile(null);
                      setIsBulkUploadOpen(false);
                    }}
                  >
                    Close
                  </Button>
                </div>
              </div>
            
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {bulkUploadResults.map((result, index) => (
                <div
                  key={index}
                  className={`p-3 rounded-lg border ${
                    result.status === 'success' 
                      ? 'bg-green-50 border-green-200' 
                      : 'bg-red-50 border-red-200'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2">
                        {result.status === 'success' ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                        <span className="font-medium">
                          {result.name || `Row ${index + 1}`}
                        </span>
                      </div>
                      {result.status === 'error' && (
                        <p className="text-sm text-red-600 mt-1">
                          {result.error}
                        </p>
                      )}
                      {result.status === 'success' && (
                        <p className="text-sm text-green-600 mt-1">
                          Product created successfully
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </DialogContent>
      </Dialog>
      
      <MobileNav />
    </div>
  );
}
