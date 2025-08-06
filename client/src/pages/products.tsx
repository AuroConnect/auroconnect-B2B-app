import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import Header from "@/components/layout/header";
import MobileNav from "@/components/layout/mobile-nav";
import ProductGrid from "@/components/products/product-grid";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Search, Package, Building2, Heart, HeartOff } from "lucide-react";
import { useEffect } from "react";
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

export default function Products() {
  const { user, isLoading } = useAuth();
  const { toast } = useToast();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [activeTab, setActiveTab] = useState("products");
  const [selectedPartner, setSelectedPartner] = useState<string>("all");

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

  const { data: categories, isLoading: categoriesLoading } = useQuery({
    queryKey: ["api", "products", "categories"],
    enabled: !!user,
  });

  const { data: products, isLoading: productsLoading } = useQuery({
    queryKey: ["api", "products", selectedCategory === "all" ? "" : selectedCategory],
    enabled: !!user,
  });

  // Fetch favorites
  const { data: favorites = [], isLoading: favoritesLoading } = useQuery<Favorite[]>({
    queryKey: ["api", "favorites"],
    enabled: !!user,
  });

  // Fetch distributors
  const { data: distributors = [], isLoading: distributorsLoading } = useQuery<User[]>({
    queryKey: ["api", "partners", "distributors"],
    enabled: !!user,
  });

  // Fetch manufacturers (only for distributors)
  const { data: manufacturers = [], isLoading: manufacturersLoading } = useQuery<User[]>({
    queryKey: ["api", "partners", "manufacturers"],
    enabled: !!user && user?.role === "distributor",
  });

  const filteredProducts = Array.isArray(products) ? products.filter((product: any) =>
    product.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.description?.toLowerCase().includes(searchTerm.toLowerCase())
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

  if (isLoading || !user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900" data-testid="text-page-title">
            Product Catalog
          </h1>
          <p className="text-gray-600 mt-1">
            Browse and order from available products
          </p>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="products" className="flex items-center gap-2">
              <Package className="h-4 w-4" />
              Products
            </TabsTrigger>
            <TabsTrigger value="partners" className="flex items-center gap-2">
              <Building2 className="h-4 w-4" />
              Browse by Partner
            </TabsTrigger>
          </TabsList>

          {/* Products Tab */}
          <TabsContent value="products" className="space-y-6">
            {/* Search and Filter */}
            <Card>
              <CardHeader>
                <CardTitle>Search & Filter</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search products..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                      data-testid="input-search-products"
                    />
                  </div>
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="w-full md:w-[200px]" data-testid="select-category">
                      <SelectValue placeholder="All Categories" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      {Array.isArray(categories) && categories.map((category: any) => (
                        <SelectItem key={category.id} value={category.id}>
                          {category.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Product Grid */}
            <ProductGrid 
              products={filteredProducts}
              isLoading={productsLoading}
              userRole={(user as User)?.role || 'retailer'}
            />
          </TabsContent>

          {/* Partners Tab */}
          <TabsContent value="partners" className="space-y-6">
            {/* Partner Filter */}
            <Card>
              <CardHeader>
                <CardTitle>Browse by Partner</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                    <Input
                      placeholder="Search partners..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Select value={selectedPartner} onValueChange={setSelectedPartner}>
                    <SelectTrigger className="w-full md:w-[200px]">
                      <SelectValue placeholder="All Partners" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Partners</SelectItem>
                      <SelectItem value="favorites">My Favorites</SelectItem>
                      <SelectItem value="distributors">Distributors</SelectItem>
                      {user?.role === "distributor" && (
                        <SelectItem value="manufacturers">Manufacturers</SelectItem>
                      )}
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Partners Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {/* Favorites */}
              {selectedPartner === "all" || selectedPartner === "favorites" ? (
                favorites.map((favorite) => (
                  <Card key={favorite.id} className="hover:shadow-md transition-shadow">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          {getRoleIcon(favorite.favoriteUser.role)}
                          <Badge variant="outline">{favorite.favoriteUser.role}</Badge>
                          <Badge variant="secondary" className="text-xs">⭐ Favorite</Badge>
                        </div>
                      </div>
                      <CardTitle className="text-lg">
                        {favorite.favoriteUser.businessName || 
                         `${favorite.favoriteUser.firstName} ${favorite.favoriteUser.lastName}`}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <p className="text-sm text-gray-600">
                        {getRoleDescription(favorite.favoriteUser.role)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {favorite.favoriteUser.email}
                      </p>
                      <Button size="sm" className="w-full">
                        <Package className="h-4 w-4 mr-1" />
                        Browse Products
                      </Button>
                    </CardContent>
                  </Card>
                ))
              ) : null}

              {/* Distributors */}
              {(selectedPartner === "all" || selectedPartner === "distributors") && 
               distributors.map((distributor) => (
                <Card key={distributor.id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <Package className="h-4 w-4" />
                        <Badge variant="outline">Distributor</Badge>
                        {isFavorite(distributor.id) && (
                          <Badge variant="secondary" className="text-xs">⭐ Favorite</Badge>
                        )}
                      </div>
                    </div>
                    <CardTitle className="text-lg">
                      {distributor.businessName || `${distributor.firstName} ${distributor.lastName}`}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <p className="text-sm text-gray-600">
                      {getRoleDescription(distributor.role)}
                    </p>
                    <p className="text-xs text-gray-500">
                      {distributor.email}
                    </p>
                    <Button size="sm" className="w-full">
                      <Package className="h-4 w-4 mr-1" />
                      Browse Products
                    </Button>
                  </CardContent>
                </Card>
              ))}

              {/* Manufacturers (only for distributors) */}
              {user?.role === "distributor" && 
               (selectedPartner === "all" || selectedPartner === "manufacturers") &&
               manufacturers.map((manufacturer) => (
                <Card key={manufacturer.id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4" />
                        <Badge variant="outline">Manufacturer</Badge>
                        {isFavorite(manufacturer.id) && (
                          <Badge variant="secondary" className="text-xs">⭐ Favorite</Badge>
                        )}
                      </div>
                    </div>
                    <CardTitle className="text-lg">
                      {manufacturer.businessName || `${manufacturer.firstName} ${manufacturer.lastName}`}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <p className="text-sm text-gray-600">
                      {getRoleDescription(manufacturer.role)}
                    </p>
                    <p className="text-xs text-gray-500">
                      {manufacturer.email}
                    </p>
                    <Button size="sm" className="w-full">
                      <Building2 className="h-4 w-4 mr-1" />
                      Browse Products
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>

      <MobileNav />
    </div>
  );
}
