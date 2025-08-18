import { useState, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Edit, Trash2, Eye, EyeOff, Plus, Upload, Download, Search, Package } from "lucide-react";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { useAuth } from "@/hooks/useAuth";
import Header from "@/components/layout/header";
import MobileNav from "@/components/layout/mobile-nav";

export default function MyProducts() {
  const { toast } = useToast();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const bulkUploadRef = useRef<HTMLInputElement>(null);

  const userRole = (user as any)?.role || 'retailer';

  // State management
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedDistributor, setSelectedDistributor] = useState("all");
  const [viewMode, setViewMode] = useState<"grid" | "list">("list");
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<any>(null);

  // Form states
  const [newProduct, setNewProduct] = useState({
    name: "",
    description: "",
    sku: "",
    categoryId: "",
    basePrice: "",
    stockQuantity: "",
    brand: "",
    unit: "Pieces",
    imageUrl: "",
    isActive: true,
    assignedDistributors: [] as string[]
  });

  const [editForm, setEditForm] = useState({
    name: "",
    description: "",
    sku: "",
    categoryId: "",
    basePrice: "",
    stockQuantity: "",
    brand: "",
    unit: "Pieces",
    imageUrl: "",
    isActive: true
  });

  // Image upload state
  const [imageUploadType, setImageUploadType] = useState<"url" | "file">("url");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>("");

  // Fetch categories
  const { data: categories = [] } = useQuery({
    queryKey: ["api", "products", "categories"],
    queryFn: async () => {
      const response = await apiRequest("GET", "/api/products/categories");
      return response.json();
    },
  });

  // Fetch distributors for manufacturer
  const { data: distributors = [] } = useQuery({
    queryKey: ["api", "distributors"],
    queryFn: async () => {
      const response = await apiRequest("GET", "/api/users/distributors");
      return response.json();
    },
    enabled: userRole === 'manufacturer',
  });

  // Fetch my products (only owned by current user)
  const { data: myProducts = [], isLoading, error: productsError } = useQuery({
    queryKey: ["api", "my-products", selectedCategory, selectedDistributor],
    queryFn: async () => {
      console.log('🔍 Fetching my-products...');
      
      // Check authentication first
      const token = localStorage.getItem('authToken');
      console.log('🔍 Auth token present:', !!token);
      console.log('🔍 Token preview:', token?.substring(0, 50) + '...');
      
      if (!token) {
        console.error('❌ No authentication token found!');
        throw new Error('No authentication token found');
      }
      
      try {
        let url = "/api/my-products";
        const params = new URLSearchParams();
        
        if (selectedCategory !== "all") {
          params.append('categoryId', selectedCategory);
        }
        if (selectedDistributor !== "all") {
          params.append('distributorId', selectedDistributor);
        }
        
        if (params.toString()) {
          url += `?${params.toString()}`;
        }
        
        const response = await apiRequest("GET", url);
        console.log('🔍 My-products response status:', response.status);
        console.log('🔍 My-products response headers:', Object.fromEntries(response.headers.entries()));
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('❌ My-products API error:', errorText);
          throw new Error(`Failed to fetch products: ${response.status} - ${errorText}`);
        }
        
        const data = await response.json();
        console.log('✅ My-products data received:', data.length, 'products');
        console.log('✅ First product sample:', data[0]);
        return data;
      } catch (error) {
        console.error('❌ My-products fetch error:', error);
        throw error;
      }
    },
    enabled: userRole === 'manufacturer' || userRole === 'distributor',
    refetchInterval: 2000, // Refetch every 2 seconds
    staleTime: 0, // Always consider data stale
    retry: 5,
    retryDelay: 1000,
    refetchOnWindowFocus: true,
    refetchOnMount: true,
  });

  // Debug logging
  console.log('My Products Debug:', {
    userRole,
    myProducts: myProducts.length,
    isLoading,
    productsError,
    products: myProducts,
    hasToken: !!localStorage.getItem('authToken'),
    token: localStorage.getItem('authToken')?.substring(0, 20) + '...'
  });

  // Show error state
  if (productsError) {
    console.error('Products fetch error:', productsError);
  }

  // Check if user is authenticated
  const isAuthenticated = !!localStorage.getItem('authToken');
  if (!isAuthenticated) {
    console.error('❌ No authentication token found!');
    console.log('🔍 Attempting to redirect to login...');
    // Force redirect to login if not authenticated
    window.location.href = '/';
    return null;
  }
  
  console.log('🔍 Authentication check passed');
  console.log('🔍 User role:', userRole);
  console.log('🔍 User data:', user);

  // Filter and sort products
  const filteredAndSortedProducts = myProducts
    .filter((product: any) => {
      const matchesSearch = product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           product.sku.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           (product.brand && product.brand.toLowerCase().includes(searchTerm.toLowerCase()));
      return matchesSearch;
    })
    .sort((a: any, b: any) => a.name.localeCompare(b.name));

  // Mutations
  const addProductMutation = useMutation({
    mutationFn: async (productData: any) => {
      const response = await apiRequest("POST", "/api/products", productData);
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Product Added",
        description: "Product has been successfully added.",
      });
      queryClient.invalidateQueries({ queryKey: ["api", "my-products"] });
      setIsAddDialogOpen(false);
             setNewProduct({
         name: "",
         description: "",
         sku: "",
         categoryId: "",
         basePrice: "",
         stockQuantity: "",
         brand: "",
         unit: "Pieces",
         imageUrl: "",
         isActive: true,
         assignedDistributors: []
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

  const updateProductMutation = useMutation({
    mutationFn: async (productData: any) => {
      const response = await apiRequest("PUT", `/api/products/${editingProduct.id}`, productData);
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Product Updated",
        description: "Product has been successfully updated.",
      });
      queryClient.invalidateQueries({ queryKey: ["api", "my-products"] });
      setIsEditDialogOpen(false);
      setEditingProduct(null);
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to update product.",
        variant: "destructive",
      });
    },
  });

  const deleteProductMutation = useMutation({
    mutationFn: async () => {
      const response = await apiRequest("DELETE", `/api/products/${editingProduct.id}`);
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Product Deleted",
        description: "Product has been successfully deleted.",
      });
      queryClient.invalidateQueries({ queryKey: ["api", "my-products"] });
      setIsEditDialogOpen(false);
      setEditingProduct(null);
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to delete product.",
        variant: "destructive",
      });
    },
  });

  const toggleVisibilityMutation = useMutation({
    mutationFn: async ({ productId, isActive }: { productId: string; isActive: boolean }) => {
      const response = await apiRequest("PUT", `/api/products/${productId}`, { isActive });
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Product Updated",
        description: "Product visibility has been updated.",
      });
      queryClient.invalidateQueries({ queryKey: ["api", "my-products"] });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to update product visibility.",
        variant: "destructive",
      });
    },
  });

  const bulkUploadMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      const response = await apiRequest("POST", "/api/products/bulk-upload", formData);
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Bulk Upload Successful",
        description: `Successfully uploaded ${data.uploadedCount} products.`,
      });
      queryClient.invalidateQueries({ queryKey: ["api", "my-products"] });
      if (bulkUploadRef.current) {
        bulkUploadRef.current.value = "";
      }
    },
    onError: (error: any) => {
      toast({
        title: "Bulk Upload Failed",
        description: error.message || "Failed to upload products.",
        variant: "destructive",
      });
    },
  });

  // Event handlers
  const handleAddProduct = () => {
    if (!newProduct.name || !newProduct.sku || !newProduct.basePrice || !newProduct.stockQuantity) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields (Name, SKU, Base Price, Stock Quantity).",
        variant: "destructive",
      });
      return;
    }

    const productData = {
      name: newProduct.name,
      description: newProduct.description,
      sku: newProduct.sku,
      basePrice: parseFloat(newProduct.basePrice),
      stockQuantity: parseInt(newProduct.stockQuantity) || 0,
      brand: newProduct.brand || null,
      unit: newProduct.unit,
      categoryId: newProduct.categoryId || null,
      imageUrl: newProduct.imageUrl || null,
      isActive: newProduct.isActive,
      assignedDistributors: newProduct.assignedDistributors
    };

    addProductMutation.mutate(productData);
  };

  const handleEditProduct = (product: any) => {
    setEditingProduct(product);
    setEditForm({
      name: product.name || "",
      description: product.description || "",
      sku: product.sku || "",
      categoryId: product.categoryId || "",
      basePrice: product.basePrice?.toString() || "",
      stockQuantity: product.stockQuantity?.toString() || "",
      brand: product.brand || "",
      unit: product.unit || "Pieces",
      imageUrl: product.imageUrl || "",
      isActive: product.isActive !== false
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdateProduct = () => {
    if (!editForm.name || !editForm.sku || !editForm.basePrice || !editForm.stockQuantity) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields (Name, SKU, Base Price, Stock Quantity).",
        variant: "destructive",
      });
      return;
    }

    const productData = {
      name: editForm.name,
      description: editForm.description,
      sku: editForm.sku,
      basePrice: parseFloat(editForm.basePrice),
      stockQuantity: parseInt(editForm.stockQuantity) || 0,
      brand: editForm.brand || null,
      unit: editForm.unit,
      categoryId: editForm.categoryId || null,
      imageUrl: editForm.imageUrl || null,
      isActive: editForm.isActive
    };

    updateProductMutation.mutate(productData);
  };

  const handleDeleteProduct = () => {
    if (confirm("Are you sure you want to delete this product?")) {
      deleteProductMutation.mutate();
    }
  };

  const handleToggleVisibility = (productId: string, currentStatus: boolean) => {
    toggleVisibilityMutation.mutate({ productId, isActive: !currentStatus });
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleBulkUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file);
      bulkUploadMutation.mutate(formData);
    }
  };

  const downloadTemplate = () => {
    const template = [
      ['name', 'description', 'sku', 'categoryId', 'basePrice', 'stockQuantity', 'brand', 'unit', 'imageUrl'],
      ['Sample Product', 'Sample description', 'SAMPLE-001', '', '100.00', '100', 'Sample Brand', 'Pieces', 'https://example.com/image.jpg']
    ];
    
    const csvContent = template.map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'product_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  // Show loading state
  if (isLoading) {
    return (
      <div className="min-h-screen">
        <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Products</h1>
            <p className="text-gray-600 mt-2">Manage your own products</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {Array.from({ length: 8 }).map((_, index) => (
            <Card key={index} className="animate-pulse">
              <div className="aspect-square bg-gray-200 rounded-t-lg"></div>
              <CardContent className="p-4">
                <div className="h-4 bg-gray-200 rounded mb-2"></div>
                <div className="h-3 bg-gray-200 rounded mb-3"></div>
                <div className="h-3 bg-gray-200 rounded mb-3"></div>
                <div className="flex items-center justify-between">
                  <div className="h-6 bg-gray-200 rounded w-20"></div>
                  <div className="h-8 bg-gray-200 rounded w-24"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
        </div>
        <MobileNav />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header />
      
    <div className="container mx-auto px-4 py-8">
             {/* Enhanced Header */}
       <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 mb-8 border border-blue-100">
         <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
           <div>
             <h1 className="text-3xl font-bold text-gray-900 mb-2">My Products</h1>
             <p className="text-gray-600">Manage your product catalog and inventory</p>
           </div>
           <div className="flex flex-wrap gap-3">
             <Button
               onClick={downloadTemplate}
               variant="outline"
               className="flex items-center gap-2 bg-white hover:bg-gray-50 border-blue-200 text-blue-700 hover:text-blue-800"
             >
               <Download className="h-4 w-4" />
               Download Template
             </Button>
             <Button
               onClick={() => bulkUploadRef.current?.click()}
               variant="outline"
               className="flex items-center gap-2 bg-white hover:bg-gray-50 border-green-200 text-green-700 hover:text-green-800"
             >
               <Upload className="h-4 w-4" />
               Bulk Upload
             </Button>
             <Button
               onClick={() => setIsAddDialogOpen(true)}
               className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all duration-200"
             >
               <Plus className="h-4 w-4" />
               Add New Product
             </Button>
           </div>
         </div>
       </div>

             {/* Enhanced Filters and Search */}
       <div className="bg-white rounded-lg border border-gray-200 p-4 mb-6 shadow-sm">
         <div className="flex flex-col lg:flex-row gap-4">
           <div className="flex-1">
             <div className="relative">
               <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
               <Input
                 placeholder="Search products by name, SKU, or brand..."
                 value={searchTerm}
                 onChange={(e) => setSearchTerm(e.target.value)}
                 className="pl-10 border-gray-300 focus:border-blue-500 focus:ring-blue-500"
               />
             </div>
           </div>
                       <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-full lg:w-48 border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map((category: any) => (
                  <SelectItem key={category.id} value={category.id}>
                    {category.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {userRole === 'manufacturer' && (
              <Select value={selectedDistributor} onValueChange={setSelectedDistributor}>
                <SelectTrigger className="w-full lg:w-48 border-gray-300 focus:border-blue-500 focus:ring-blue-500">
                  <SelectValue placeholder="All Distributors" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Distributors</SelectItem>
                  {distributors.map((distributor: any) => (
                    <SelectItem key={distributor.id} value={distributor.id}>
                      {distributor.businessName || `${distributor.firstName} ${distributor.lastName}`}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
           <div className="flex gap-2">
             <Button
               variant={viewMode === "grid" ? "default" : "outline"}
               size="sm"
               onClick={() => setViewMode("grid")}
               className={viewMode === "grid" ? "bg-blue-600 hover:bg-blue-700" : "border-gray-300"}
             >
               Grid View
             </Button>
             <Button
               variant={viewMode === "list" ? "default" : "outline"}
               size="sm"
               onClick={() => setViewMode("list")}
               className={viewMode === "list" ? "bg-blue-600 hover:bg-blue-700" : "border-gray-300"}
             >
               List View
             </Button>
           </div>
         </div>
       </div>

        {/* Products Display */}
        {viewMode === "list" ? (
          <div className="space-y-4">
            {filteredAndSortedProducts.map((product: any) => (
              <Card key={product.id} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden">
                        {product.imageUrl ? (
                          <img
                            src={product.imageUrl}
                            alt={product.name}
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-gray-400">
                            <Package className="h-6 w-6" />
                          </div>
                        )}
                      </div>
                      <div>
                        <h3 className="font-semibold text-lg text-gray-900">
                          {product.name}
                        </h3>
                        <p className="text-sm text-gray-600 mb-1">
                          SKU: {product.sku} | Brand: {product.brand || 'N/A'}
                        </p>
                        <p className="text-sm text-gray-500 line-clamp-2">
                          {product.description}
                        </p>
                                                 <p className="text-sm text-gray-500">
                           Stock: {product.stockQuantity || 0} {product.unit || 'Pieces'}
                         </p>
                         {product.category && (
                           <Badge variant="outline" className="mt-1">
                             {product.category.name}
                           </Badge>
                         )}
                         {userRole === 'manufacturer' && product.assignedDistributors && product.assignedDistributors.length > 0 && (
                           <div className="mt-2">
                             <p className="text-xs text-gray-500 mb-1">Assigned to:</p>
                             <div className="flex flex-wrap gap-1">
                               {product.assignedDistributors.slice(0, 2).map((dist: any) => (
                                 <Badge key={dist.id} variant="secondary" className="text-xs">
                                   {dist.name}
                                 </Badge>
                               ))}
                               {product.assignedDistributors.length > 2 && (
                                 <Badge variant="secondary" className="text-xs">
                                   +{product.assignedDistributors.length - 2} more
                                 </Badge>
                               )}
                             </div>
                           </div>
                         )}
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="font-semibold text-lg text-gray-900">
                          ₹{product.basePrice?.toLocaleString() || "0"}
                        </div>
                        <Badge variant={product.isActive ? "default" : "secondary"}>
                          {product.isActive ? "Active" : "Hidden"}
                        </Badge>
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditProduct(product)}
                        >
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleToggleVisibility(product.id, product.isActive)}
                        >
                          {product.isActive ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setEditingProduct(product);
                            setIsEditDialogOpen(true);
                          }}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredAndSortedProducts.map((product: any) => (
          <Card key={product.id} className="group hover:shadow-lg transition-shadow">
            <div className="aspect-square bg-gray-100 rounded-t-lg overflow-hidden">
              {product.imageUrl ? (
                <img
                  src={product.imageUrl}
                  alt={product.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-gray-400">
                  <span>No Image</span>
                </div>
              )}
            </div>
            <CardContent className="p-4">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-lg text-gray-900 truncate">
                  {product.name}
                </h3>
                <Badge variant={product.isActive ? "default" : "secondary"}>
                  {product.isActive ? "Active" : "Hidden"}
                </Badge>
              </div>
              <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                {product.description}
              </p>
              <div className="flex items-center justify-between mb-3">
                <span className="text-lg font-bold text-gray-900">
                  ₹{product.basePrice?.toLocaleString() || "0"}
                </span>
                <span className="text-sm text-gray-500">SKU: {product.sku}</span>
              </div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm text-gray-600">
                  Brand: {product.brand || 'N/A'}
                </span>
                <span className="text-sm text-gray-600">
                  Stock: {product.stockQuantity || 0} {product.unit || 'Pieces'}
                </span>
              </div>
                             {product.category && (
                 <Badge variant="outline" className="mb-3">
                   {product.category.name}
                 </Badge>
               )}
               {userRole === 'manufacturer' && product.assignedDistributors && product.assignedDistributors.length > 0 && (
                 <div className="mb-3">
                   <p className="text-xs text-gray-500 mb-1">Assigned to:</p>
                   <div className="flex flex-wrap gap-1">
                     {product.assignedDistributors.slice(0, 1).map((dist: any) => (
                       <Badge key={dist.id} variant="secondary" className="text-xs">
                         {dist.name}
                       </Badge>
                     ))}
                     {product.assignedDistributors.length > 1 && (
                       <Badge variant="secondary" className="text-xs">
                         +{product.assignedDistributors.length - 1} more
                       </Badge>
                     )}
                   </div>
                 </div>
               )}
            </CardContent>
            <CardFooter className="p-4 pt-0">
              <div className="flex gap-2 w-full">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleEditProduct(product)}
                  className="flex-1"
                >
                  <Edit className="h-4 w-4 mr-2" />
                  Edit
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleToggleVisibility(product.id, product.isActive)}
                >
                  {product.isActive ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setEditingProduct(product);
                    setIsEditDialogOpen(true);
                  }}
                  className="text-red-600 hover:text-red-700"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </CardFooter>
          </Card>
        ))}
      </div>
        )}

             {filteredAndSortedProducts.length === 0 && (
         <div className="text-center py-16">
           <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
             <Package className="h-12 w-12 text-blue-600" />
           </div>
           <h3 className="text-2xl font-bold text-gray-900 mb-3">No products found</h3>
           <p className="text-gray-600 mb-6 max-w-md mx-auto">
             {searchTerm || selectedCategory !== "all" 
               ? "Try adjusting your search or filters to find what you're looking for."
               : "Start building your product catalog by adding your first product."
             }
           </p>
           {!searchTerm && selectedCategory === "all" && (
             <div className="flex flex-col sm:flex-row gap-3 justify-center">
               <Button 
                 onClick={() => setIsAddDialogOpen(true)}
                 className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all duration-200"
               >
                 <Plus className="h-4 w-4 mr-2" />
                 Add Your First Product
               </Button>
               <Button 
                 onClick={downloadTemplate}
                 variant="outline"
                 className="border-blue-200 text-blue-700 hover:bg-blue-50"
               >
                 <Download className="h-4 w-4 mr-2" />
                 Download Template
               </Button>
             </div>
           )}
         </div>
       )}

             {/* Enhanced Add Product Dialog */}
       <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
         <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
           <DialogHeader className="text-center">
             <DialogTitle className="text-2xl font-bold text-gray-900">Add New Product</DialogTitle>
             <DialogDescription className="text-gray-600">
               Create a new product for your catalog with all the details.
             </DialogDescription>
           </DialogHeader>
                     <div className="space-y-6">
             {/* Basic Information */}
             <div className="bg-gray-50 rounded-lg p-4">
               <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 <div>
                   <Label htmlFor="name" className="text-sm font-medium text-gray-700">Product Name *</Label>
                   <Input
                     id="name"
                     name="name"
                     value={newProduct.name}
                     onChange={(e) => setNewProduct({ ...newProduct, name: e.target.value })}
                     placeholder="Enter product name"
                     className="mt-1"
                   />
                 </div>
                 <div>
                   <Label htmlFor="sku" className="text-sm font-medium text-gray-700">SKU *</Label>
                   <Input
                     id="sku"
                     name="sku"
                     value={newProduct.sku}
                     onChange={(e) => setNewProduct({ ...newProduct, sku: e.target.value })}
                     placeholder="Enter SKU"
                     className="mt-1"
                   />
                 </div>
                 <div className="md:col-span-2">
                   <Label htmlFor="description" className="text-sm font-medium text-gray-700">Description</Label>
                   <Textarea
                     id="description"
                     name="description"
                     value={newProduct.description}
                     onChange={(e) => setNewProduct({ ...newProduct, description: e.target.value })}
                     placeholder="Enter product description"
                     className="mt-1"
                     rows={3}
                   />
                 </div>
               </div>
             </div>

             {/* Category and Brand */}
             <div className="bg-gray-50 rounded-lg p-4">
               <h3 className="text-lg font-semibold text-gray-900 mb-4">Category & Brand</h3>
               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 <div>
                   <Label htmlFor="category" className="text-sm font-medium text-gray-700">Category</Label>
                   <Select value={newProduct.categoryId} onValueChange={(value) => setNewProduct({ ...newProduct, categoryId: value })}>
                     <SelectTrigger className="mt-1">
                       <SelectValue placeholder="Select category" />
                     </SelectTrigger>
                     <SelectContent>
                       {categories.map((category: any) => (
                         <SelectItem key={category.id} value={category.id}>
                           {category.name}
                         </SelectItem>
                       ))}
                     </SelectContent>
                   </Select>
                 </div>
                 <div>
                   <Label htmlFor="brand" className="text-sm font-medium text-gray-700">Brand</Label>
                   <Input
                     id="brand"
                     name="brand"
                     value={newProduct.brand}
                     onChange={(e) => setNewProduct({ ...newProduct, brand: e.target.value })}
                     placeholder="Enter brand name"
                     className="mt-1"
                   />
                 </div>
               </div>
             </div>

             {/* Pricing and Inventory */}
             <div className="bg-gray-50 rounded-lg p-4">
               <h3 className="text-lg font-semibold text-gray-900 mb-4">Pricing & Inventory</h3>
               <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                 <div>
                   <Label htmlFor="basePrice" className="text-sm font-medium text-gray-700">Base Price *</Label>
                   <Input
                     id="basePrice"
                     name="basePrice"
                     type="number"
                     step="0.01"
                     value={newProduct.basePrice}
                     onChange={(e) => setNewProduct({ ...newProduct, basePrice: e.target.value })}
                     placeholder="0.00"
                     className="mt-1"
                   />
                 </div>
                 <div>
                   <Label htmlFor="stockQuantity" className="text-sm font-medium text-gray-700">Stock Quantity *</Label>
                   <Input
                     id="stockQuantity"
                     name="stockQuantity"
                     type="number"
                     value={newProduct.stockQuantity}
                     onChange={(e) => setNewProduct({ ...newProduct, stockQuantity: e.target.value })}
                     placeholder="0"
                     className="mt-1"
                   />
                 </div>
                 <div>
                   <Label htmlFor="unit" className="text-sm font-medium text-gray-700">Unit</Label>
                   <Select value={newProduct.unit} onValueChange={(value) => setNewProduct({ ...newProduct, unit: value })}>
                     <SelectTrigger className="mt-1">
                       <SelectValue placeholder="Select unit" />
                     </SelectTrigger>
                     <SelectContent>
                       <SelectItem value="Pieces">Pieces</SelectItem>
                       <SelectItem value="Kg">Kilograms</SelectItem>
                       <SelectItem value="Liters">Liters</SelectItem>
                       <SelectItem value="Meters">Meters</SelectItem>
                       <SelectItem value="Boxes">Boxes</SelectItem>
                       <SelectItem value="Sets">Sets</SelectItem>
                       <SelectItem value="Pairs">Pairs</SelectItem>
                       <SelectItem value="Units">Units</SelectItem>
                     </SelectContent>
                   </Select>
                 </div>
               </div>
             </div>
                         {/* Product Image */}
             <div className="bg-gray-50 rounded-lg p-4">
               <h3 className="text-lg font-semibold text-gray-900 mb-4">Product Image</h3>
               <div className="space-y-4">
                 <div className="flex gap-2">
                   <Button
                     type="button"
                     variant={imageUploadType === "url" ? "default" : "outline"}
                     size="sm"
                     onClick={() => setImageUploadType("url")}
                     className={imageUploadType === "url" ? "bg-blue-600 hover:bg-blue-700" : "border-gray-300"}
                   >
                     Image URL
                   </Button>
                   <Button
                     type="button"
                     variant={imageUploadType === "file" ? "default" : "outline"}
                     size="sm"
                     onClick={() => setImageUploadType("file")}
                     className={imageUploadType === "file" ? "bg-blue-600 hover:bg-blue-700" : "border-gray-300"}
                   >
                     Upload File
                   </Button>
                 </div>
                 {imageUploadType === "url" ? (
                   <Input
                     value={newProduct.imageUrl}
                     onChange={(e) => setNewProduct({ ...newProduct, imageUrl: e.target.value })}
                     placeholder="https://example.com/product-image.jpg"
                     className="border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                   />
                 ) : (
                   <div>
                     <Input
                       type="file"
                       accept="image/*"
                       onChange={handleFileChange}
                       ref={fileInputRef}
                       className="border-gray-300 focus:border-blue-500 focus:ring-blue-500"
                     />
                     {imagePreview && (
                       <div className="mt-3">
                         <p className="text-sm text-gray-600 mb-2">Preview:</p>
                         <img
                           src={imagePreview}
                           alt="Preview"
                           className="w-24 h-24 object-cover rounded-lg border border-gray-200"
                         />
                       </div>
                     )}
                   </div>
                 )}
               </div>
             </div>

             {/* Distributor Assignment (Manufacturers Only) */}
             {userRole === 'manufacturer' && distributors.length > 0 && (
               <div className="bg-gray-50 rounded-lg p-4">
                 <h3 className="text-lg font-semibold text-gray-900 mb-4">Distributor Assignment</h3>
                 <div className="space-y-3">
                   <p className="text-sm text-gray-600 mb-3">
                     Select distributors who can see and sell this product:
                   </p>
                   <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-40 overflow-y-auto">
                     {distributors.map((distributor: any) => (
                       <div key={distributor.id} className="flex items-center space-x-3">
                         <input
                           type="checkbox"
                           id={`dist-${distributor.id}`}
                           checked={newProduct.assignedDistributors.includes(distributor.id)}
                           onChange={(e) => {
                             const updatedDistributors = e.target.checked
                               ? [...newProduct.assignedDistributors, distributor.id]
                               : newProduct.assignedDistributors.filter((id: string) => id !== distributor.id);
                             setNewProduct({ ...newProduct, assignedDistributors: updatedDistributors });
                           }}
                           className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                         />
                         <Label htmlFor={`dist-${distributor.id}`} className="text-sm font-medium text-gray-700 cursor-pointer">
                           {distributor.businessName || `${distributor.firstName} ${distributor.lastName}`}
                         </Label>
                       </div>
                     ))}
                   </div>
                   {distributors.length === 0 && (
                     <p className="text-sm text-gray-500 italic">
                       No distributors available. Products will be visible to all distributors.
                     </p>
                   )}
                 </div>
               </div>
             )}

             {/* Product Status */}
             <div className="bg-gray-50 rounded-lg p-4">
               <div className="flex items-center space-x-3">
                 <input
                   type="checkbox"
                   id="isActive"
                   checked={newProduct.isActive}
                   onChange={(e) => setNewProduct({ ...newProduct, isActive: e.target.checked })}
                   className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                 />
                 <Label htmlFor="isActive" className="text-sm font-medium text-gray-700">
                   Active (visible in catalog)
                 </Label>
               </div>
             </div>
           </div>
           
           {/* Enhanced Dialog Footer */}
           <div className="flex justify-end gap-3 pt-6 border-t border-gray-200">
             <Button 
               variant="outline" 
               onClick={() => setIsAddDialogOpen(false)}
               className="border-gray-300 text-gray-700 hover:bg-gray-50"
             >
               Cancel
             </Button>
             <Button 
               onClick={handleAddProduct} 
               disabled={addProductMutation.isPending}
               className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all duration-200"
             >
               {addProductMutation.isPending ? (
                 <>
                   <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                   Adding Product...
                 </>
               ) : (
                 <>
                   <Plus className="h-4 w-4 mr-2" />
                   Add Product
                 </>
               )}
             </Button>
           </div>
        </DialogContent>
      </Dialog>

      {/* Edit Product Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Product</DialogTitle>
            <DialogDescription>
              Update product information.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="edit-name">Product Name *</Label>
              <Input
                id="edit-name"
                name="edit-name"
                value={editForm.name}
                onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                placeholder="Enter product name"
              />
            </div>
            <div>
              <Label htmlFor="edit-description">Description</Label>
              <Textarea
                id="edit-description"
                name="edit-description"
                value={editForm.description}
                onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                placeholder="Enter product description"
              />
            </div>
            <div>
              <Label htmlFor="edit-sku">SKU *</Label>
              <Input
                id="edit-sku"
                name="edit-sku"
                value={editForm.sku}
                onChange={(e) => setEditForm({ ...editForm, sku: e.target.value })}
                placeholder="Enter SKU"
              />
            </div>
            <div>
              <Label htmlFor="edit-category">Category</Label>
              <Select value={editForm.categoryId} onValueChange={(value) => setEditForm({ ...editForm, categoryId: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category: any) => (
                    <SelectItem key={category.id} value={category.id}>
                      {category.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="edit-basePrice">Base Price *</Label>
              <Input
                id="edit-basePrice"
                name="edit-basePrice"
                type="number"
                step="0.01"
                value={editForm.basePrice}
                onChange={(e) => setEditForm({ ...editForm, basePrice: e.target.value })}
                placeholder="Enter base price"
              />
            </div>
            <div>
              <Label htmlFor="edit-stockQuantity">Stock Quantity *</Label>
              <Input
                id="edit-stockQuantity"
                name="edit-stockQuantity"
                type="number"
                value={editForm.stockQuantity}
                onChange={(e) => setEditForm({ ...editForm, stockQuantity: e.target.value })}
                placeholder="Enter stock quantity"
              />
            </div>
            <div>
              <Label htmlFor="edit-brand">Brand</Label>
              <Input
                id="edit-brand"
                name="edit-brand"
                value={editForm.brand}
                onChange={(e) => setEditForm({ ...editForm, brand: e.target.value })}
                placeholder="Enter brand name"
              />
            </div>
            <div>
              <Label htmlFor="edit-unit">Unit</Label>
              <Select value={editForm.unit} onValueChange={(value) => setEditForm({ ...editForm, unit: value })}>
                <SelectTrigger>
                  <SelectValue placeholder="Select unit" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Pieces">Pieces</SelectItem>
                  <SelectItem value="Kg">Kilograms</SelectItem>
                  <SelectItem value="Liters">Liters</SelectItem>
                  <SelectItem value="Meters">Meters</SelectItem>
                  <SelectItem value="Boxes">Boxes</SelectItem>
                  <SelectItem value="Sets">Sets</SelectItem>
                  <SelectItem value="Pairs">Pairs</SelectItem>
                  <SelectItem value="Units">Units</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor="edit-imageUrl">Image URL</Label>
              <Input
                id="edit-imageUrl"
                value={editForm.imageUrl}
                onChange={(e) => setEditForm({ ...editForm, imageUrl: e.target.value })}
                placeholder="Enter image URL"
              />
            </div>
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="edit-isActive"
                checked={editForm.isActive}
                onChange={(e) => setEditForm({ ...editForm, isActive: e.target.checked })}
                className="rounded"
              />
              <Label htmlFor="edit-isActive">Active (visible in catalog)</Label>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>
              Cancel
            </Button>
            <Button 
              variant="destructive" 
              onClick={handleDeleteProduct}
              disabled={deleteProductMutation.isPending}
            >
              {deleteProductMutation.isPending ? "Deleting..." : "Delete"}
            </Button>
            <Button onClick={handleUpdateProduct} disabled={updateProductMutation.isPending}>
              {updateProductMutation.isPending ? "Updating..." : "Update"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Hidden file input for bulk upload */}
      <input
        type="file"
        ref={bulkUploadRef}
        onChange={handleBulkUpload}
        accept=".csv,.xlsx,.xls"
        className="hidden"
      />
      </div>
      
      <MobileNav />
    </div>
  );
}
