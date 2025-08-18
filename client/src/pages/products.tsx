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
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [sortBy, setSortBy] = useState("name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [selectedManufacturer, setSelectedManufacturer] = useState("all");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const bulkUploadRef = useRef<HTMLInputElement>(null);
  
  // Get user role early to avoid hoisting issues
  const userRole = (user as User)?.role || 'retailer';

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
        description: "Multi-port USB-C hub for connectivity",
        sku: "HUB004",
        categoryId: "",
        basePrice: "2500.00",
        imageUrl: "https://example.com/hub1.jpg",
        assignedDistributors: ""
      }
    ];

    const csvContent = [
      ['name', 'description', 'sku', 'categoryId', 'basePrice', 'imageUrl', 'assignedDistributors'],
      ...sampleData.map(item => [
        item.name,
        item.description,
        item.sku,
        item.categoryId,
        item.basePrice,
        item.imageUrl,
        item.assignedDistributors
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'product_sample.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  // Filter and sort products
  const filteredAndSortedProducts = useMemo(() => {
    if (!products) return [];

    let filtered = products.filter((product) => {
      const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           product.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           product.description.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesCategory = selectedCategory === "all" || product.categoryId === selectedCategory;
      
      const matchesManufacturer = selectedManufacturer === "all" || 
                                 product.manufacturerId === selectedManufacturer;

      return matchesSearch && matchesCategory && matchesManufacturer;
    });

    // Sort products
    filtered.sort((a, b) => {
      let aValue: any, bValue: any;
      
      switch (sortBy) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'price':
          aValue = a.basePrice;
          bValue = b.basePrice;
          break;
        case 'createdAt':
          aValue = new Date(a.createdAt || '');
          bValue = new Date(b.createdAt || '');
          break;
        default:
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }, [products, searchTerm, selectedCategory, selectedManufacturer, sortBy, sortOrder]);

  // Pagination
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedProducts = filteredAndSortedProducts.slice(startIndex, endIndex);

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
                onClick={() => window.location.href = '/my-products'}
                className="action-button-primary"
              >
                <Plus className="h-4 w-4 mr-2" />
                Manage My Products
              </Button>
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

        {/* Products Grid */}
        <ProductGrid
          products={paginatedProducts}
          isLoading={productsLoading}
          userRole={userRole}
          categories={categories || []}
        />

        {/* Pagination */}
        {filteredAndSortedProducts.length > itemsPerPage && (
          <div className="flex justify-center mt-8">
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                disabled={currentPage === 1}
              >
                Previous
              </Button>
              <span className="text-sm text-gray-600">
                Page {currentPage} of {Math.ceil(filteredAndSortedProducts.length / itemsPerPage)}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentPage(prev => Math.min(Math.ceil(filteredAndSortedProducts.length / itemsPerPage), prev + 1))}
                disabled={currentPage === Math.ceil(filteredAndSortedProducts.length / itemsPerPage)}
              >
                Next
              </Button>
            </div>
          </div>
        )}

        {/* Bulk Upload Results Dialog */}
        {showBulkResults && (
          <Dialog open={showBulkResults} onOpenChange={setShowBulkResults}>
            <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Bulk Upload Results</DialogTitle>
                <DialogDescription>
                  Results from the bulk upload operation
                </DialogDescription>
              </DialogHeader>
              
              <div className="space-y-4">
                {bulkUploadResults.map((result, index) => (
                  <div key={index} className={`p-3 rounded-lg border ${
                    result.status === 'success' ? 'bg-green-50 border-green-200' :
                    result.status === 'error' ? 'bg-red-50 border-red-200' :
                    'bg-yellow-50 border-yellow-200'
                  }`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{result.name || `Row ${result.row}`}</p>
                        <p className="text-sm text-gray-600">{result.status}</p>
                        {result.error && <p className="text-sm text-red-600">{result.error}</p>}
                      </div>
                      {result.status === 'success' && (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      )}
                      {result.status === 'error' && (
                        <XCircle className="h-5 w-5 text-red-600" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
              
              <DialogFooter>
                <Button onClick={() => setShowBulkResults(false)}>
                  Close
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        )}
      </div>
      
      <MobileNav />
    </div>
  );
}
