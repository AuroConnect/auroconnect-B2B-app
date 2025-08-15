import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { 
  Users, 
  Search, 
  Heart, 
  HeartOff, 
  Building2, 
  Package, 
  Star,
  ShoppingCart,
  Eye
} from "lucide-react";
import { isUnauthorizedError } from "@/lib/authUtils";
import Header from "@/components/layout/header";
import MobileNav from "@/components/layout/mobile-nav";
import ProductBrowser from "@/components/products/product-browser";
import type { User } from "@/hooks/useAuth";

interface Favorite {
  id: string;
  userId: string;
  favoriteUserId: string;
  favoriteType: string;
  createdAt: string;
  favoriteUser: User;
}

export default function Partners() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState("distributors");
  const [selectedPartner, setSelectedPartner] = useState<User | null>(null);
  const [isPartnerDetailsOpen, setIsPartnerDetailsOpen] = useState(false);
  const [isProductBrowserOpen, setIsProductBrowserOpen] = useState(false);

  // Determine which tabs to show based on user role
  const getAvailableTabs = () => {
    if (!user) return [];
    
    const tabs = [
      { value: "favorites", label: "Favorites", icon: Heart }
    ];
    
    // Retailer and Manufacturer can only see Distributors
    if (user.role === "retailer" || user.role === "manufacturer") {
      tabs.push({ value: "distributors", label: "Distributors", icon: Package });
    }
    
    // Distributor can see both Retailers and Manufacturers
    if (user.role === "distributor") {
      tabs.push({ value: "retailers", label: "Retailers", icon: Users });
      tabs.push({ value: "manufacturers", label: "Manufacturers", icon: Building2 });
    }
    
    return tabs;
  };

  const availableTabs = getAvailableTabs();

  // Fetch favorites
  const { data: favorites = [], isLoading: favoritesLoading, error: favoritesError } = useQuery<Favorite[]>({
    queryKey: ["api", "favorites"],
    enabled: isAuthenticated && !isLoading,
    retry: 3,
  });

  // Fetch distributors (for retailers and manufacturers)
  const { data: distributors = [], isLoading: distributorsLoading, error: distributorsError } = useQuery<User[]>({
    queryKey: ["api", "partners", "distributors", searchTerm ? `?search=${searchTerm}` : ""],
    enabled: isAuthenticated && !isLoading && (activeTab === "distributors" || user?.role === "manufacturer"),
    retry: 3,
  });

  // Fetch associated distributors for manufacturers
  const { data: associatedDistributors = [], isLoading: associatedDistributorsLoading } = useQuery<User[]>({
    queryKey: ["api", "partners", "associated-distributors"],
    enabled: isAuthenticated && !isLoading && user?.role === "manufacturer",
    retry: 3,
  });

  // Fetch retailers (for distributors only)
  const { data: retailers = [], isLoading: retailersLoading, error: retailersError } = useQuery<User[]>({
    queryKey: ["api", "partners", "retailers", searchTerm ? `?search=${searchTerm}` : ""],
    enabled: isAuthenticated && !isLoading && activeTab === "retailers" && user?.role === "distributor",
    retry: 3,
  });

  // Fetch manufacturers (for distributors only)
  const { data: manufacturers = [], isLoading: manufacturersLoading, error: manufacturersError } = useQuery<User[]>({
    queryKey: ["api", "partners", "manufacturers", searchTerm ? `?search=${searchTerm}` : ""],
    enabled: isAuthenticated && !isLoading && activeTab === "manufacturers" && user?.role === "distributor",
    retry: 3,
  });

  // Get current partners based on active tab and user role
  const getCurrentPartners = () => {
    switch (activeTab) {
      case "distributors":
        // For manufacturers, show only associated distributors
        if (user?.role === "manufacturer") {
          return associatedDistributors;
        }
        return distributors;
      case "retailers":
        return retailers;
      case "manufacturers":
        return manufacturers;
      default:
        return [];
    }
  };

  const getCurrentPartnersLoading = () => {
    switch (activeTab) {
      case "distributors":
        if (user?.role === "manufacturer") {
          return associatedDistributorsLoading;
        }
        return distributorsLoading;
      case "retailers":
        return retailersLoading;
      case "manufacturers":
        return manufacturersLoading;
      default:
        return false;
    }
  };

  // Filter partners based on search term
  const filteredPartners = getCurrentPartners().filter((partner) =>
    partner.businessName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.firstName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.lastName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Filter favorites based on search term
  const filteredFavorites = favorites.filter((favorite) =>
    favorite.favoriteUser.businessName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    favorite.favoriteUser.firstName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    favorite.favoriteUser.lastName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    favorite.favoriteUser.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Add to favorites mutation
  const addToFavoritesMutation = useMutation({
    mutationFn: async ({ favoriteUserId, favoriteType }: { favoriteUserId: string; favoriteType: string }) => {
      const response = await apiRequest("POST", "/api/favorites", { favoriteUserId, favoriteType });
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Added to Favorites",
        description: "Partner has been added to your favorites.",
      });
      queryClient.invalidateQueries({ queryKey: ["api", "favorites"] });
    },
    onError: (error) => {
      if (isUnauthorizedError(error)) {
        toast({
          title: "Unauthorized",
          description: "You are logged out. Logging in again...",
          variant: "destructive",
        });
        setTimeout(() => {
          window.location.reload();
        }, 500);
        return;
      }
      toast({
        title: "Error",
        description: "Failed to add partner to favorites.",
        variant: "destructive",
      });
    },
  });

  // Remove from favorites mutation
  const removeFromFavoritesMutation = useMutation({
    mutationFn: async (favoriteUserId: string) => {
      const response = await apiRequest("DELETE", `/api/favorites/${favoriteUserId}`);
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Removed from Favorites",
        description: "Partner has been removed from your favorites.",
      });
      queryClient.invalidateQueries({ queryKey: ["api", "favorites"] });
    },
    onError: (error) => {
      if (isUnauthorizedError(error)) {
        toast({
          title: "Unauthorized",
          description: "You are logged out. Logging in again...",
          variant: "destructive",
        });
        setTimeout(() => {
          window.location.reload();
        }, 500);
        return;
      }
      toast({
        title: "Error",
        description: "Failed to remove partner from favorites.",
        variant: "destructive",
      });
    },
  });

  const handleAddToFavorites = (partner: User) => {
    addToFavoritesMutation.mutate({
      favoriteUserId: partner.id,
      favoriteType: partner.role,
    });
  };

  const handleRemoveFromFavorites = (favoriteUserId: string) => {
    removeFromFavoritesMutation.mutate(favoriteUserId);
  };

  const isFavorite = (partnerId: string) => {
    return favorites.some((favorite) => favorite.favoriteUserId === partnerId);
  };

  const getFavoriteId = (partnerId: string) => {
    const favorite = favorites.find((favorite) => favorite.favoriteUserId === partnerId);
    return favorite?.id;
  };

  const getRoleDescription = (role: string) => {
    switch (role) {
      case "retailer":
        return "Local business that sells products to customers";
      case "distributor":
        return "Wholesale supplier that connects manufacturers and retailers";
      case "manufacturer":
        return "Product manufacturer that creates and supplies goods";
      default:
        return "Business partner";
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "retailer":
        return <Users className="h-4 w-4 text-blue-600" />;
      case "distributor":
        return <Package className="h-4 w-4 text-green-600" />;
      case "manufacturer":
        return <Building2 className="h-4 w-4 text-purple-600" />;
      default:
        return <Users className="h-4 w-4 text-gray-600" />;
    }
  };

  const handleBrowseProducts = (partner: User) => {
    setSelectedPartner(partner);
    setIsProductBrowserOpen(true);
  };

  if (!isAuthenticated) {
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
  if (favoritesError || distributorsError || retailersError || manufacturersError) {
    return (
      <div className="min-h-screen">
        <Header />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center py-12">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Data</h3>
            <p className="text-gray-500 mb-4">
              {favoritesError?.message || distributorsError?.message || retailersError?.message || manufacturersError?.message || "Failed to load partners data"}
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
          <h1 className="text-3xl font-bold text-gray-900">
            Partner Network
          </h1>
          <p className="text-gray-600 mt-1">
            Discover and connect with {user?.role === "distributor" ? "retailers and manufacturers" : "distributors"}
          </p>
        </div>

        {/* Search */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Search partners by name, business, or email..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="enhanced-tabs grid w-full" style={{ gridTemplateColumns: `repeat(${availableTabs.length}, 1fr)` }}>
            {availableTabs.map((tab) => (
              <TabsTrigger 
                key={tab.value}
                value={tab.value} 
                className="enhanced-tab-trigger"
              >
                <tab.icon className="h-4 w-4" />
                {tab.label === "Favorites" ? `${tab.label} (${favorites.length})` : tab.label}
              </TabsTrigger>
            ))}
          </TabsList>

          {/* Favorites Tab */}
          <TabsContent value="favorites" className="space-y-4">
            {favoritesLoading ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse bg-gray-200 h-48 rounded-lg" />
                ))}
              </div>
            ) : filteredFavorites.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <Heart className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No favorites yet</h3>
                  <p className="text-gray-500">
                    Start adding partners to your favorites for quick access
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {filteredFavorites.map((favorite) => (
                  <Card key={favorite.id} className="hover:shadow-md transition-shadow">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          {getRoleIcon(favorite.favoriteUser.role)}
                          <Badge variant="outline">{favorite.favoriteUser.role}</Badge>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveFromFavorites(favorite.favoriteUserId)}
                          className="text-red-500 hover:text-red-700"
                        >
                          <HeartOff className="h-4 w-4" />
                        </Button>
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
                      {favorite.favoriteUser.phoneNumber && (
                        <p className="text-xs text-gray-500">
                          📞 {favorite.favoriteUser.phoneNumber}
                        </p>
                      )}
                      <div className="flex gap-2 pt-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setSelectedPartner(favorite.favoriteUser);
                            setIsPartnerDetailsOpen(true);
                          }}
                        >
                          <Eye className="h-4 w-4 mr-1" />
                          View Details
                        </Button>
                        <Button 
                          size="sm"
                          onClick={() => handleBrowseProducts(favorite.favoriteUser)}
                        >
                          <ShoppingCart className="h-4 w-4 mr-1" />
                          Browse Products
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Partners Tabs */}
          {availableTabs.slice(1).map((tab) => (
            <TabsContent key={tab.value} value={tab.value} className="space-y-4">
              {getCurrentPartnersLoading() ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="animate-pulse bg-gray-200 h-48 rounded-lg" />
                  ))}
                </div>
              ) : filteredPartners.length === 0 ? (
                <Card>
                  <CardContent className="text-center py-12">
                    <tab.icon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      {searchTerm ? `No ${tab.label.toLowerCase()} found` : `No ${tab.label.toLowerCase()} available`}
                    </h3>
                    <p className="text-gray-500">
                      {searchTerm ? "Try adjusting your search terms" : `Check back later for new ${tab.label.toLowerCase()}`}
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {filteredPartners.map((partner) => (
                    <Card key={partner.id} className="hover:shadow-md transition-shadow">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-2">
                            {getRoleIcon(partner.role)}
                            <Badge variant="outline">{partner.role}</Badge>
                          </div>
                          {!isFavorite(partner.id) ? (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleAddToFavorites(partner)}
                              className="text-gray-500 hover:text-red-500"
                            >
                              <Heart className="h-4 w-4" />
                            </Button>
                          ) : (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleRemoveFromFavorites(partner.id)}
                              className="text-red-500 hover:text-red-700"
                            >
                              <HeartOff className="h-4 w-4" />
                            </Button>
                          )}
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
                            onClick={() => {
                              setSelectedPartner(partner);
                              setIsPartnerDetailsOpen(true);
                            }}
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            View Details
                          </Button>
                          <Button 
                            size="sm"
                            onClick={() => handleBrowseProducts(partner)}
                          >
                            <ShoppingCart className="h-4 w-4 mr-1" />
                            Browse Products
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          ))}
        </Tabs>
      </div>
      
      <MobileNav />

      {/* Partner Details Dialog */}
      <Dialog open={isPartnerDetailsOpen} onOpenChange={setIsPartnerDetailsOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Partner Details</DialogTitle>
            <DialogDescription>
              Detailed information about the selected partner
            </DialogDescription>
          </DialogHeader>
          {selectedPartner && (
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-900">
                  {selectedPartner.businessName || `${selectedPartner.firstName} ${selectedPartner.lastName}`}
                </h3>
                <p className="text-sm text-gray-600">{getRoleDescription(selectedPartner.role)}</p>
              </div>
              <div className="space-y-2">
                <p className="text-sm">
                  <span className="font-medium">Email:</span> {selectedPartner.email}
                </p>
                {selectedPartner.phoneNumber && (
                  <p className="text-sm">
                    <span className="font-medium">Phone:</span> {selectedPartner.phoneNumber}
                  </p>
                )}
                {selectedPartner.whatsappNumber && (
                  <p className="text-sm">
                    <span className="font-medium">WhatsApp:</span> {selectedPartner.whatsappNumber}
                  </p>
                )}
                {selectedPartner.address && (
                  <p className="text-sm">
                    <span className="font-medium">Address:</span> {selectedPartner.address}
                  </p>
                )}
              </div>
              <div className="flex gap-2 pt-4">
                <Button
                  onClick={() => 
                    isFavorite(selectedPartner.id) 
                      ? handleRemoveFromFavorites(selectedPartner.id)
                      : handleAddToFavorites(selectedPartner)
                  }
                  variant={isFavorite(selectedPartner.id) ? "destructive" : "default"}
                  className="flex-1"
                >
                  {isFavorite(selectedPartner.id) ? (
                    <>
                      <HeartOff className="h-4 w-4 mr-1" />
                      Remove from Favorites
                    </>
                  ) : (
                    <>
                      <Heart className="h-4 w-4 mr-1" />
                      Add to Favorites
                    </>
                  )}
                </Button>
                <Button variant="outline" className="flex-1">
                  <ShoppingCart className="h-4 w-4 mr-1" />
                  Browse Products
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Product Browser Modal */}
      {selectedPartner && (
        <ProductBrowser
          partner={selectedPartner}
          isOpen={isProductBrowserOpen}
          onClose={() => {
            setIsProductBrowserOpen(false);
            setSelectedPartner(null);
          }}
        />
      )}
    </div>
  );
} 