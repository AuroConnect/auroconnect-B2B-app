import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
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
  Eye,
  Send,
  Check,
  X,
  UserPlus,
  UserCheck,
  Mail
} from "lucide-react";
import { isUnauthorizedError } from "@/lib/authUtils";
import Header from "@/components/layout/header";
import MobileNav from "@/components/layout/mobile-nav";
import ProductBrowser from "@/components/products/product-browser";
import type { User } from "@/hooks/useAuth";

interface Partnership {
  id: string;
  requester_id: string;
  partner_id: string;
  partnership_type: string;
  status: 'pending' | 'active' | 'declined';
  message?: string;
  created_at: string;
  requester: User;
  partner: User;
}

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
  const [activeTab, setActiveTab] = useState("connected");
  const [selectedPartner, setSelectedPartner] = useState<User | null>(null);
  const [isPartnerDetailsOpen, setIsPartnerDetailsOpen] = useState(false);
  const [isProductBrowserOpen, setIsProductBrowserOpen] = useState(false);
  const [isInviteDialogOpen, setIsInviteDialogOpen] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteMessage, setInviteMessage] = useState("");

  // Fetch connected partners
  const { data: connectedPartners = [], isLoading: connectedLoading } = useQuery<User[]>({
    queryKey: ["api", "partnerships", "connected-partners"],
    enabled: isAuthenticated && !isLoading,
    retry: 3,
  });

  // Fetch available partners for partnership requests
  const { data: availablePartners = [], isLoading: availableLoading } = useQuery<User[]>({
    queryKey: ["api", "partnerships", "available"],
    enabled: isAuthenticated && !isLoading,
    retry: 3,
  });

  // Fetch partnership requests
  const { data: partnershipRequests = [], isLoading: requestsLoading } = useQuery<Partnership[]>({
    queryKey: ["api", "partnerships", "requests"],
    enabled: isAuthenticated && !isLoading,
    retry: 3,
  });

  // Fetch favorites
  const { data: favorites = [], isLoading: favoritesLoading } = useQuery<Favorite[]>({
    queryKey: ["api", "favorites"],
    enabled: isAuthenticated && !isLoading,
    retry: 3,
  });

  // Send partnership request mutation
  const sendRequestMutation = useMutation({
    mutationFn: async ({ email, message }: { email: string; message: string }) => {
      const data = {
        inviteeEmail: email,
        inviteeRole: user?.role === 'manufacturer' ? 'distributor' : 'manufacturer',
        message: message
      };
      
      const response = await apiRequest("POST", "/api/partnerships/send-invite", data);
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Partnership Request Sent",
        description: "Your partnership request has been sent successfully.",
      });
      setIsInviteDialogOpen(false);
      setInviteEmail("");
      setInviteMessage("");
      queryClient.invalidateQueries({ queryKey: ["api", "partnerships", "available"] });
      queryClient.invalidateQueries({ queryKey: ["api", "partnerships", "requests"] });
    },
    onError: (error: any) => {
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
        description: error.message || "Failed to send partnership request.",
        variant: "destructive",
      });
    },
  });

  // Accept partnership request mutation
  const acceptRequestMutation = useMutation({
    mutationFn: async (partnershipId: string) => {
      const response = await apiRequest("POST", `/api/partnerships/${partnershipId}/accept`);
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Partnership Accepted",
        description: "Partnership request has been accepted successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ["api", "partnerships", "connected-partners"] });
      queryClient.invalidateQueries({ queryKey: ["api", "partnerships", "requests"] });
    },
    onError: (error: any) => {
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
        description: error.message || "Failed to accept partnership request.",
        variant: "destructive",
      });
    },
  });

  // Decline partnership request mutation
  const declineRequestMutation = useMutation({
    mutationFn: async (partnershipId: string) => {
      const response = await apiRequest("POST", `/api/partnerships/${partnershipId}/decline`);
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Partnership Declined",
        description: "Partnership request has been declined.",
      });
      queryClient.invalidateQueries({ queryKey: ["api", "partnerships", "requests"] });
    },
    onError: (error: any) => {
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
        description: error.message || "Failed to decline partnership request.",
        variant: "destructive",
      });
    },
  });

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
    onError: (error: any) => {
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
    onError: (error: any) => {
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

  const handleSendRequest = () => {
    if (!inviteEmail.trim()) {
      toast({
        title: "Error",
        description: "Please enter an email address.",
        variant: "destructive",
      });
      return;
    }
    
    sendRequestMutation.mutate({
      email: inviteEmail.trim(),
      message: inviteMessage.trim(),
    });
  };

  const handleAcceptRequest = (partnershipId: string) => {
    acceptRequestMutation.mutate(partnershipId);
  };

  const handleDeclineRequest = (partnershipId: string) => {
    declineRequestMutation.mutate(partnershipId);
  };

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

  // Force refresh function
  const handleForceRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ["api", "partnerships", "connected-partners"] });
    queryClient.invalidateQueries({ queryKey: ["api", "partnerships", "available"] });
    queryClient.invalidateQueries({ queryKey: ["api", "partnerships", "requests"] });
    toast({
      title: "Refreshing Data",
      description: "Partnership data is being refreshed...",
    });
  };

  // Filter partners based on search term
  const filteredConnectedPartners = connectedPartners.filter((partner) =>
    partner.businessName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.firstName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.lastName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredAvailablePartners = availablePartners.filter((partner) =>
    partner.businessName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.firstName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.lastName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredFavorites = favorites.filter((favorite) =>
    favorite.favoriteUser.businessName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    favorite.favoriteUser.firstName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    favorite.favoriteUser.lastName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    favorite.favoriteUser.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
            Connect with {user?.role === "distributor" ? "manufacturers" : "distributors"} and manage partnerships
          </p>
        </div>

                 {/* Search and Refresh */}
         <Card className="mb-8">
           <CardContent className="pt-6">
             <div className="flex gap-4">
               <div className="relative flex-1">
                 <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                 <Input
                   placeholder="Search partners by name, business, or email..."
                   value={searchTerm}
                   onChange={(e) => setSearchTerm(e.target.value)}
                   className="pl-10"
                 />
               </div>
               <Button 
                 onClick={handleForceRefresh}
                 variant="outline"
                 disabled={connectedLoading}
               >
                 🔄 Refresh
               </Button>
             </div>
           </CardContent>
         </Card>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="enhanced-tabs grid w-full" style={{ gridTemplateColumns: "repeat(4, 1fr)" }}>
            <TabsTrigger value="connected" className="enhanced-tab-trigger">
              <UserCheck className="h-4 w-4" />
              Connected ({connectedPartners.length})
            </TabsTrigger>
            <TabsTrigger value="available" className="enhanced-tab-trigger">
              <UserPlus className="h-4 w-4" />
              Available ({availablePartners.length})
            </TabsTrigger>
            <TabsTrigger value="requests" className="enhanced-tab-trigger">
              <Mail className="h-4 w-4" />
              Requests ({partnershipRequests.length})
            </TabsTrigger>
            <TabsTrigger value="favorites" className="enhanced-tab-trigger">
              <Heart className="h-4 w-4" />
              Favorites ({favorites.length})
            </TabsTrigger>
          </TabsList>

          {/* Connected Partners Tab */}
          <TabsContent value="connected" className="space-y-4">
            {connectedLoading ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse bg-gray-200 h-48 rounded-lg" />
                ))}
              </div>
            ) : filteredConnectedPartners.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <UserCheck className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No connected partners</h3>
                  <p className="text-gray-500 mb-4">
                    You haven't connected with any partners yet
                  </p>
                  <Button onClick={() => setActiveTab("available")}>
                    <UserPlus className="h-4 w-4 mr-2" />
                    Find Partners
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {filteredConnectedPartners.map((partner) => (
                  <Card key={partner.id} className="hover:shadow-md transition-shadow">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          {getRoleIcon(partner.role)}
                          <Badge variant="outline">{partner.role}</Badge>
                        </div>
                        <Badge variant="default" className="bg-green-100 text-green-800">
                          Connected
                        </Badge>
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

          {/* Available Partners Tab */}
          <TabsContent value="available" className="space-y-4">
            {availableLoading ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse bg-gray-200 h-48 rounded-lg" />
                ))}
              </div>
            ) : filteredAvailablePartners.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <UserPlus className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    {searchTerm ? "No partners found" : "No available partners"}
                  </h3>
                  <p className="text-gray-500 mb-4">
                    {searchTerm ? "Try adjusting your search terms" : "All potential partners are already connected"}
                  </p>
                  {!searchTerm && (
                    <Button onClick={() => setIsInviteDialogOpen(true)}>
                      <Send className="h-4 w-4 mr-2" />
                      Invite by Email
                    </Button>
                  )}
                </CardContent>
              </Card>
            ) : (
              <>
                <div className="flex justify-between items-center">
                  <h3 className="text-lg font-medium">Available Partners</h3>
                  <Button onClick={() => setIsInviteDialogOpen(true)}>
                    <Send className="h-4 w-4 mr-2" />
                    Invite by Email
                  </Button>
                </div>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {filteredAvailablePartners.map((partner) => (
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
                            onClick={() => {
                              setInviteEmail(partner.email);
                              setIsInviteDialogOpen(true);
                            }}
                          >
                            <Send className="h-4 w-4 mr-1" />
                            Send Request
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </>
            )}
          </TabsContent>

          {/* Partnership Requests Tab */}
          <TabsContent value="requests" className="space-y-4">
            {requestsLoading ? (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="animate-pulse bg-gray-200 h-48 rounded-lg" />
                ))}
              </div>
            ) : partnershipRequests.length === 0 ? (
              <Card>
                <CardContent className="text-center py-12">
                  <Mail className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No pending requests</h3>
                  <p className="text-gray-500">
                    You don't have any pending partnership requests
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {partnershipRequests.map((request) => {
                  const requester = request.requester;
                  return (
                    <Card key={request.id} className="hover:shadow-md transition-shadow">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-2">
                            {getRoleIcon(requester.role)}
                            <Badge variant="outline">{requester.role}</Badge>
                          </div>
                          <Badge variant="secondary">Pending</Badge>
                        </div>
                        <CardTitle className="text-lg">
                          {requester.businessName || `${requester.firstName} ${requester.lastName}`}
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <p className="text-sm text-gray-600">
                          {getRoleDescription(requester.role)}
                        </p>
                        <p className="text-xs text-gray-500">
                          {requester.email}
                        </p>
                        {request.message && (
                          <p className="text-sm text-gray-700 bg-gray-50 p-2 rounded">
                            "{request.message}"
                          </p>
                        )}
                        <div className="flex gap-2 pt-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleAcceptRequest(request.id)}
                            className="text-green-600 hover:text-green-700"
                          >
                            <Check className="h-4 w-4 mr-1" />
                            Accept
                          </Button>
                          <Button 
                            size="sm"
                            variant="outline"
                            onClick={() => handleDeclineRequest(request.id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <X className="h-4 w-4 mr-1" />
                            Decline
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </TabsContent>

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
                <Button 
                  variant="outline" 
                  className="flex-1"
                  onClick={() => handleBrowseProducts(selectedPartner)}
                >
                  <ShoppingCart className="h-4 w-4 mr-1" />
                  Browse Products
                </Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Invite Partner Dialog */}
      <Dialog open={isInviteDialogOpen} onOpenChange={setIsInviteDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Send Partnership Request</DialogTitle>
            <DialogDescription>
              Send a partnership request to connect with a {user?.role === 'manufacturer' ? 'distributor' : 'manufacturer'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Email Address</label>
              <Input
                placeholder={`Enter ${user?.role === 'manufacturer' ? 'distributor' : 'manufacturer'} email`}
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="text-sm font-medium">Message (Optional)</label>
              <Textarea
                placeholder="Add a personal message to your request..."
                value={inviteMessage}
                onChange={(e) => setInviteMessage(e.target.value)}
                rows={3}
              />
            </div>
            <div className="flex gap-2 pt-4">
              <Button
                onClick={handleSendRequest}
                disabled={sendRequestMutation.isPending}
                className="flex-1"
              >
                {sendRequestMutation.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                    Sending...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Send Request
                  </>
                )}
              </Button>
              <Button 
                variant="outline" 
                onClick={() => setIsInviteDialogOpen(false)}
                className="flex-1"
              >
                Cancel
              </Button>
            </div>
          </div>
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