import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { apiRequest } from "@/lib/queryClient";
import Header from "@/components/layout/header";
import MobileNav from "@/components/layout/mobile-nav";
import ProductGrid from "@/components/products/product-grid";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Search, Package, Building2, Heart, HeartOff, Plus, Upload, X, Image as ImageIcon } from "lucide-react";
import { useEffect, useRef } from "react";
import { useToast } from "@/hooks/use-toast";
import type { User } from "@/hooks/useAuth";

interface Favorite {
  id: string;
  userId: string;
  favoriteUserId: string;
  favoriteType: string;
  createdAt: string;
  favoriteUser: User;
}

interface Product {
  id: string;
  name: string;
  description: string;
  sku: string;
  categoryId: string;
  manufacturerId: string;
  imageUrl: string;
  basePrice: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export default function Products() {
  const { user, isLoading } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [activeTab, setActiveTab] = useState("products");
  const [selectedPartner, setSelectedPartner] = useState<string>("all");
  const [isAddProductOpen, setIsAddProductOpen] = useState(false);
  const [imageUploadType, setImageUploadType] = useState<'url' | 'file'>('url');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [newProduct, setNewProduct] = useState({
    name: "",
    description: "",
    sku: "",
    categoryId: "",
    basePrice: "",
    imageUrl: "",
    imageFile: null as File | null
  });

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !user) {
      toast({
        title: "Unauthorized", 
        description: "You are logged out. Logging in again...",
        variant: "destructive",
      });
      setTimeout(() => {
        window.location.href = "/";
      }, 500);
      return;
    }
  }, [user, isLoading, toast]);

  const { data: categories, isLoading: categoriesLoading, error: categoriesError } = useQuery({
    queryKey: ["api", "products", "categories"],
    enabled: !!user && !isLoading,
    retry: 3,
  });

  const { data: products, isLoading: productsLoading, error: productsError } = useQuery({
    queryKey: ["api", "products", selectedCategory === "all" ? "" : `?categoryId=${selectedCategory}`],
    enabled: !!user && !isLoading,
    retry: 3,
  });

  // Fetch favorites
  const { data: favorites = [], isLoading: favoritesLoading } = useQuery<Favorite[]>({
    queryKey: ["api", "favorites"],
    enabled: !!user,
  });

  // Fetch distributors (for retailers and manufacturers)
  const { data: distributors = [], isLoading: distributorsLoading, error: distributorsError } = useQuery<User[]>({
    queryKey: ["api", "partners", "distributors", searchTerm ? `?search=${searchTerm}` : ""],
    enabled: !!user && !isLoading && (user.role === "retailer" || user.role === "manufacturer"),
    retry: 3,
  });

  // Fetch retailers (for distributors only)
  const { data: retailers = [], isLoading: retailersLoading, error: retailersError } = useQuery<User[]>({
    queryKey: ["api", "partners", "retailers", searchTerm ? `?search=${searchTerm}` : ""],
    enabled: !!user && !isLoading && user?.role === "distributor",
    retry: 3,
  });

  // Fetch manufacturers (for distributors only)
  const { data: manufacturers = [], isLoading: manufacturersLoading, error: manufacturersError } = useQuery<User[]>({
    queryKey: ["api", "partners", "manufacturers", searchTerm ? `?search=${searchTerm}` : ""],
    enabled: !!user && !isLoading && user?.role === "distributor",
    retry: 3,
  });

  // Get available partners based on user role
  const getAvailablePartners = () => {
    if (!user) return [];
    
    if (user.role === "retailer" || user.role === "manufacturer") {
      return distributors;
    } else if (user.role === "distributor") {
      return [...retailers, ...manufacturers];
    }
    
    return [];
  };

  const availablePartners = getAvailablePartners();

  // Filter partners based on search term
  const filteredPartners = availablePartners.filter((partner) =>
    partner.businessName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.firstName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.lastName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Add product mutation
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
      setIsAddProductOpen(false);
      setNewProduct({
        name: "",
        description: "",
        sku: "",
        categoryId: "",
        basePrice: "",
        imageUrl: "",
        imageFile: null
      });
      setImageUploadType('url');
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to add product.",
        variant: "destructive",
      });
    },
  });

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
      imageUrl: imageUploadType === 'url' ? newProduct.imageUrl : null
    };

    addProductMutation.mutate(productData);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith('image/')) {
        setNewProduct(prev => ({ ...prev, imageFile: file, imageUrl: '' }));
        setImageUploadType('file');
      } else {
        toast({
          title: "Invalid File",
          description: "Please upload an image file.",
          variant: "destructive",
        });
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type.startsWith('image/')) {
        setNewProduct(prev => ({ ...prev, imageFile: file, imageUrl: '' }));
        setImageUploadType('file');
      } else {
        toast({
          title: "Invalid File",
          description: "Please upload an image file.",
          variant: "destructive",
        });
      }
    }
  };

  const removeImage = () => {
    setNewProduct(prev => ({ ...prev, imageFile: null, imageUrl: '' }));
    setImageUploadType('url');
  };

  const filteredProducts = Array.isArray(products) ? products.filter((product: any) =>
    product.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.sku?.toLowerCase().includes(searchTerm.toLowerCase())
  ) : [];

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "distributor":
        return <Package className="h-4 w-4" />;
      case "manufacturer":
        return <Building2 className="h-4 w-4" />;
      default:
        return null;
    }
  };

  const getRoleDescription = (role: string) => {
    switch (role) {
      case "retailer":
        return "Retail business looking for suppliers";
      case "distributor":
        return "Distribution company connecting manufacturers and retailers";
      case "manufacturer":
        return "Product manufacturer";
      default:
        return "";
    }
  };

  const isFavorite = (partnerId: string) => {
    return favorites.some(fav => fav.favoriteUserId === partnerId);
  };

  const getFavoriteId = (partnerId: string) => {
    const favorite = favorites.find(fav => fav.favoriteUserId === partnerId);
    return favorite?.id;
  };

  const handleBrowseProducts = (partner: User) => {
    // This will be implemented in Step 3
    toast({
      title: "Browse Products",
      description: `Opening products from ${partner.businessName || partner.firstName}`,
    });
  };

  if (!user) {
    return (
      <div className="min-h-screen auromart-gradient-bg flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading...</p>
        </div>
      </div>
    );
  }

  // Handle API errors
  if (productsError || categoriesError) {
    return (
      <div className="min-h-screen">
        <Header />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Data</h3>
            <p className="text-gray-500 mb-4">
              {productsError?.message || categoriesError?.message || "Failed to load products or categories"}
            </p>
            <Button onClick={() => window.location.reload()}>
              Retry
            </Button>
          </div>
        </div>
        <MobileNav />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Product Catalog
              </h1>
              <p className="text-gray-600 mt-1">
                Browse and order from available products
              </p>
            </div>
            {/* Add Product Button for Distributors and Manufacturers */}
            {(user.role === "distributor" || user.role === "manufacturer") && (
              <Dialog open={isAddProductOpen} onOpenChange={setIsAddProductOpen}>
                <DialogTrigger asChild>
                  <Button className="action-button-primary">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Product
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto bg-white border border-gray-200 shadow-xl">
                  <DialogHeader className="pb-6">
                    <DialogTitle className="text-xl font-semibold text-gray-900">Add New Product</DialogTitle>
                    <DialogDescription className="text-gray-600">
                      Add a new product to your catalog. Fill in the required information below.
                    </DialogDescription>
                  </DialogHeader>
                  <div className="space-y-6">
                    {/* Product Name */}
                    <div className="space-y-2 form-field">
                      <Label htmlFor="name" className="text-sm font-medium">
                        Product Name *
                      </Label>
                      <Input
                        id="name"
                        value={newProduct.name}
                        onChange={(e) => setNewProduct(prev => ({ ...prev, name: e.target.value }))}
                        placeholder="Enter product name"
                        className="w-full enhanced-input"
                      />
                    </div>

                    {/* SKU and Category - Side by side on desktop */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2 form-field">
                        <Label htmlFor="sku" className="text-sm font-medium">
                          SKU *
                        </Label>
                        <Input
                          id="sku"
                          value={newProduct.sku}
                          onChange={(e) => setNewProduct(prev => ({ ...prev, sku: e.target.value }))}
                          placeholder="Enter SKU"
                          className="w-full enhanced-input"
                        />
                      </div>
                      <div className="space-y-2 form-field">
                        <Label htmlFor="category" className="text-sm font-medium">
                          Category
                        </Label>
                        <Select value={newProduct.categoryId} onValueChange={(value) => setNewProduct(prev => ({ ...prev, categoryId: value }))}>
                          <SelectTrigger className="w-full enhanced-select">
                            <SelectValue placeholder="Select category" />
                          </SelectTrigger>
                          <SelectContent className="bg-white border border-gray-200 shadow-lg">
                            {Array.isArray(categories) && categories.map((category: any) => (
                              <SelectItem key={category.id} value={category.id} className="hover:bg-gray-50">
                                {category.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    {/* Description */}
                    <div className="space-y-2 form-field">
                      <Label htmlFor="description" className="text-sm font-medium">
                        Description
                      </Label>
                      <Textarea
                        id="description"
                        value={newProduct.description}
                        onChange={(e) => setNewProduct(prev => ({ ...prev, description: e.target.value }))}
                        placeholder="Enter product description"
                        className="w-full min-h-[100px] enhanced-textarea"
                      />
                    </div>

                    {/* Price and Image - Side by side on desktop */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2 form-field">
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
                          className="w-full enhanced-input"
                        />
                      </div>
                      <div className="space-y-2 form-field">
                        <Label className="text-sm font-medium">
                          Product Image
                        </Label>
                        <div className="space-y-3">
                          {/* Image Upload Type Toggle */}
                          <div className="flex gap-2">
                            <Button
                              type="button"
                              variant={imageUploadType === 'url' ? 'default' : 'outline'}
                              size="sm"
                              onClick={() => setImageUploadType('url')}
                              className="text-xs"
                            >
                              URL
                            </Button>
                            <Button
                              type="button"
                              variant={imageUploadType === 'file' ? 'default' : 'outline'}
                              size="sm"
                              onClick={() => setImageUploadType('file')}
                              className="text-xs"
                            >
                              Upload
                            </Button>
                          </div>

                          {/* URL Input */}
                          {imageUploadType === 'url' && (
                            <Input
                              type="url"
                              value={newProduct.imageUrl}
                              onChange={(e) => setNewProduct(prev => ({ ...prev, imageUrl: e.target.value }))}
                              placeholder="https://example.com/image.jpg"
                              className="w-full enhanced-input"
                            />
                          )}

                          {/* File Upload */}
                          {imageUploadType === 'file' && (
                            <div
                              className={`border-2 border-dashed rounded-lg p-4 text-center transition-colors ${
                                dragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
                              }`}
                              onDragEnter={handleDrag}
                              onDragLeave={handleDrag}
                              onDragOver={handleDrag}
                              onDrop={handleDrop}
                            >
                              <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                onChange={handleFileSelect}
                                className="hidden"
                              />
                              
                              {newProduct.imageFile ? (
                                <div className="space-y-2">
                                  <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                      <ImageIcon className="h-4 w-4 text-green-600" />
                                      <span className="text-sm font-medium">{newProduct.imageFile.name}</span>
                                    </div>
                                    <Button
                                      type="button"
                                      variant="ghost"
                                      size="sm"
                                      onClick={removeImage}
                                      className="text-red-500 hover:text-red-700"
                                    >
                                      <X className="h-4 w-4" />
                                    </Button>
                                  </div>
                                </div>
                              ) : (
                                <div className="space-y-2">
                                  <Upload className="h-8 w-8 text-gray-400 mx-auto" />
                                  <p className="text-sm text-gray-600">
                                    Drag and drop an image here, or{' '}
                                    <button
                                      type="button"
                                      onClick={() => fileInputRef.current?.click()}
                                      className="text-blue-600 hover:text-blue-700 font-medium"
                                    >
                                      browse
                                    </button>
                                  </p>
                                  <p className="text-xs text-gray-500">
                                    Supports: JPG, PNG, GIF (max 5MB)
                                  </p>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="flex justify-end gap-3 pt-6 border-t">
                    <Button 
                      variant="outline" 
                      onClick={() => setIsAddProductOpen(false)}
                      className="px-6 py-2"
                    >
                      Cancel
                    </Button>
                    <Button 
                      onClick={handleAddProduct}
                      disabled={addProductMutation.isPending}
                      className="action-button-primary px-6 py-2"
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
                  </div>
                </DialogContent>
              </Dialog>
            )}
          </div>
        </div>

        {/* Search and Filters */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Search products..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
              <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                <SelectTrigger className="w-full md:w-48">
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent className="bg-white border border-gray-200 shadow-lg">
                  <SelectItem value="all">All Categories</SelectItem>
                  {Array.isArray(categories) && categories.map((category: any) => (
                    <SelectItem key={category.id} value={category.id} className="hover:bg-gray-50">
                      {category.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="enhanced-tabs grid w-full grid-cols-2">
            <TabsTrigger value="products" className="enhanced-tab-trigger">
              <Package className="h-4 w-4" />
              Products
            </TabsTrigger>
            <TabsTrigger value="partners" className="enhanced-tab-trigger">
              <Building2 className="h-4 w-4" />
              Browse by Partner
            </TabsTrigger>
          </TabsList>

          {/* Products Tab */}
          <TabsContent value="products" className="space-y-4">
            <ProductGrid products={filteredProducts} isLoading={productsLoading} userRole={user?.role || 'retailer'} />
          </TabsContent>

          {/* Partners Tab */}
          <TabsContent value="partners" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Browse by Partner</CardTitle>
                <p className="text-sm text-gray-600">
                  {user?.role === "distributor" 
                    ? "Browse products from manufacturers and view order history with retailers"
                    : "Browse products from distributors"
                  }
                </p>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col md:flex-row gap-4 mb-6">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      placeholder="Search partners..."
                      className="pl-10"
                    />
                  </div>
                  <Select value={selectedPartner} onValueChange={setSelectedPartner}>
                    <SelectTrigger className="w-full md:w-48">
                      <SelectValue placeholder="All Partners" />
                    </SelectTrigger>
                    <SelectContent className="bg-white border border-gray-200 shadow-lg">
                      <SelectItem value="all">All Partners</SelectItem>
                      {availablePartners.map((partner) => (
                        <SelectItem key={partner.id} value={partner.id} className="hover:bg-gray-50">
                          {partner.businessName || `${partner.firstName} ${partner.lastName}`}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {filteredPartners.map((partner) => (
                    <Card key={partner.id} className="hover:shadow-md transition-shadow">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-2">
                            {getRoleIcon(partner.role)}
                            <Badge variant="outline">{partner.role}</Badge>
                          </div>
                        </div>
                        <CardTitle className="text-lg">
                          {partner.businessName || `${partner.firstName} ${partner.lastName}`}
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <p className="text-sm text-gray-600">
                          {getRoleDescription(partner.role)}
                        </p>
                        <p className="text-xs text-gray-500">
                          {partner.email}
                        </p>
                        {partner.phoneNumber && (
                          <p className="text-xs text-gray-500">
                            📞 {partner.phoneNumber}
                          </p>
                        )}
                        <div className="flex gap-2 pt-2">
                          <Button
                            size="sm"
                            variant="outline"
                          >
                            <Package className="h-4 w-4 mr-1" />
                            View Details
                          </Button>
                          <Button 
                            size="sm"
                            onClick={() => handleBrowseProducts(partner)}
                          >
                            <Package className="h-4 w-4 mr-1" />
                            Browse Products
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
      
      <MobileNav />
    </div>
  );
}
