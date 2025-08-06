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
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState("distributors");
  const [selectedPartner, setSelectedPartner] = useState<User | null>(null);
  const [isPartnerDetailsOpen, setIsPartnerDetailsOpen] = useState(false);

  // Fetch favorites
  const { data: favorites = [], isLoading: favoritesLoading } = useQuery<Favorite[]>({
    queryKey: ["api", "favorites"],
    enabled: isAuthenticated,
  });

  // Fetch distributors
  const { data: distributors = [], isLoading: distributorsLoading } = useQuery<User[]>({
    queryKey: ["api", "partners", "distributors", searchTerm],
    enabled: isAuthenticated && (activeTab === "distributors" || user?.role === "manufacturer"),
  });

  // Fetch manufacturers (only for distributors)
  const { data: manufacturers = [], isLoading: manufacturersLoading } = useQuery<User[]>({
    queryKey: ["api", "partners", "manufacturers", searchTerm],
    enabled: isAuthenticated && activeTab === "manufacturers" && user?.role === "distributor",
  });

  // Add to favorites mutation
  const addToFavoritesMutation = useMutation({
    mutationFn: async ({ favoriteUserId, favoriteType }: { favoriteUserId: string; favoriteType: string }) => {
      await apiRequest("POST", "/api/favorites", { favoriteUserId, favoriteType });
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
          window.location.href = "/";
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
      await apiRequest("DELETE", `/api/favorites/${favoriteUserId}`);
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
          window.location.href = "/";
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
    return favorites.some(fav => fav.favoriteUserId === partnerId);
  };

  const getFavoriteId = (partnerId: string) => {
    const favorite = favorites.find(fav => fav.favoriteUserId === partnerId);
    return favorite?.id;
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

  const filteredPartners = (() => {
    const partners = activeTab === "distributors" ? distributors : manufacturers;
    return partners.filter((partner) => 
      partner.businessName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      partner.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      `${partner.firstName} ${partner.lastName}`.toLowerCase().includes(searchTerm.toLowerCase())
    );
  })();

  const filteredFavorites = favorites.filter((favorite) => 
    favorite.favoriteUser.businessName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    favorite.favoriteUser.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    `${favorite.favoriteUser.firstName} ${favorite.favoriteUser.lastName}`.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">
            Browse Partners
          </h1>
          <p className="text-gray-600 mt-1">
            Discover and connect with manufacturers and distributors
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
          <TabsList className="enhanced-tabs grid w-full grid-cols-3">
            <TabsTrigger 
              value="favorites" 
              className="enhanced-tab-trigger"
            >
              <Heart className="h-4 w-4" />
              Favorites ({favorites.length})
            </TabsTrigger>
            <TabsTrigger 
              value="distributors" 
              className="enhanced-tab-trigger"
            >
              <Package className="h-4 w-4" />
              Distributors
            </TabsTrigger>
            {user?.role === "distributor" && (
              <TabsTrigger 
                value="manufacturers" 
                className="enhanced-tab-trigger"
              >
                <Building2 className="h-4 w-4" />
                Manufacturers
              </TabsTrigger>
            )}
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
                        <Button size="sm">
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

          {/* Distributors Tab */}
          <TabsContent value="distributors" className="space-y-4">
            {distributorsLoading ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse bg-gray-200 h-48 rounded-lg" />
                ))}
              </div>
            ) : filteredPartners.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <Package className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    {searchTerm ? "No distributors found" : "No distributors available"}
                  </h3>
                  <p className="text-gray-500">
                    {searchTerm ? "Try adjusting your search terms" : "Check back later for new distributors"}
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
                          <Package className="h-4 w-4" />
                          <Badge variant="outline">Distributor</Badge>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => 
                            isFavorite(partner.id) 
                              ? handleRemoveFromFavorites(partner.id)
                              : handleAddToFavorites(partner)
                          }
                          className={isFavorite(partner.id) ? "text-red-500 hover:text-red-700" : "text-gray-400 hover:text-red-500"}
                        >
                          {isFavorite(partner.id) ? (
                            <Heart className="h-4 w-4" />
                          ) : (
                            <Heart className="h-4 w-4" />
                          )}
                        </Button>
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
                        <Button size="sm">
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

          {/* Manufacturers Tab (only for distributors) */}
          {user?.role === "distributor" && (
            <TabsContent value="manufacturers" className="space-y-4">
              {manufacturersLoading ? (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="animate-pulse bg-gray-200 h-48 rounded-lg" />
                  ))}
                </div>
              ) : filteredPartners.length === 0 ? (
                <Card>
                  <CardContent className="text-center py-12">
                    <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      {searchTerm ? "No manufacturers found" : "No manufacturers available"}
                    </h3>
                    <p className="text-gray-500">
                      {searchTerm ? "Try adjusting your search terms" : "Check back later for new manufacturers"}
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
                            <Building2 className="h-4 w-4" />
                            <Badge variant="outline">Manufacturer</Badge>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => 
                              isFavorite(partner.id) 
                                ? handleRemoveFromFavorites(partner.id)
                                : handleAddToFavorites(partner)
                            }
                            className={isFavorite(partner.id) ? "text-red-500 hover:text-red-700" : "text-gray-400 hover:text-red-500"}
                          >
                            {isFavorite(partner.id) ? (
                              <Heart className="h-4 w-4" />
                            ) : (
                              <Heart className="h-4 w-4" />
                            )}
                          </Button>
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
                          <Button size="sm">
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
          )}
        </Tabs>

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
      </div>

      <MobileNav />
    </div>
  );
} 