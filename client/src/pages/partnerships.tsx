import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { apiRequest } from "@/lib/queryClient";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Users, Plus, Search, CheckCircle, XCircle, Clock, Building2 } from "lucide-react";
import { isUnauthorizedError } from "@/lib/authUtils";

interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  companyName: string;
}

interface Partnership {
  id: string;
  requesterId: string;
  partnerId: string;
  status: string;
  partnershipType: string;
  createdAt: string;
  partner: User;
}

export default function Partnerships() {
  const { user, isAuthenticated } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedPartnershipType, setSelectedPartnershipType] = useState<string>("");
  const [isAddPartnerOpen, setIsAddPartnerOpen] = useState(false);
  const [productSearchTerm, setProductSearchTerm] = useState("");
  const [isGlobalSearchOpen, setIsGlobalSearchOpen] = useState(false);

  // Fetch current partnerships
  const { data: partnerships = [], isLoading: partnershipsLoading } = useQuery<Partnership[]>({
    queryKey: ["/api/partnerships"],
    enabled: isAuthenticated,
  });

  // Fetch available partners to connect with
  const { data: availablePartners = [], isLoading: partnersLoading } = useQuery<User[]>({
    queryKey: ["/api/partners/available"],
    enabled: isAuthenticated,
  });

  // Global product search
  const { data: globalSearchResults = [], isLoading: globalSearchLoading } = useQuery<User[]>({
    queryKey: ["/api/partners/search", { product: productSearchTerm }],
    queryFn: () => apiRequest(`/api/partners/search?product=${encodeURIComponent(productSearchTerm)}`, "GET"),
    enabled: isAuthenticated && productSearchTerm.length > 2,
  });

  // Send partnership request mutation
  const sendRequestMutation = useMutation({
    mutationFn: async ({ partnerId, partnershipType }: { partnerId: string; partnershipType: string }) => {
      await apiRequest("/api/partnerships/request", "POST", { partnerId, partnershipType });
    },
    onSuccess: () => {
      toast({
        title: "Partnership Request Sent",
        description: "Your partnership request has been sent successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ["/api/partnerships"] });
      queryClient.invalidateQueries({ queryKey: ["/api/partners/available"] });
      setIsAddPartnerOpen(false);
      setSelectedPartnershipType("");
    },
    onError: (error) => {
      if (isUnauthorizedError(error)) {
        toast({
          title: "Unauthorized",
          description: "You are logged out. Logging in again...",
          variant: "destructive",
        });
        setTimeout(() => {
          window.location.href = "/api/login";
        }, 500);
        return;
      }
      toast({
        title: "Error",
        description: "Failed to send partnership request. Please try again.",
        variant: "destructive",
      });
    },
  });

  const handleSendRequest = (partnerId: string) => {
    if (!selectedPartnershipType) {
      toast({
        title: "Select Partnership Type",
        description: "Please select a partnership type before sending the request.",
        variant: "destructive",
      });
      return;
    }
    sendRequestMutation.mutate({ partnerId, partnershipType: selectedPartnershipType });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "approved":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "rejected":
        return <XCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      approved: "default",
      rejected: "destructive",
      pending: "secondary",
    } as const;

    return (
      <Badge variant={variants[status as keyof typeof variants] || "secondary"}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  const getRoleDescription = (role: string) => {
    switch (role) {
      case "retailer":
        return "Retail business looking for suppliers";
      case "distributor":
        return "Distribution company connecting manufacturers and retailers";
      case "manufacturer":
        return "Manufacturing company producing goods";
      default:
        return "Business partner";
    }
  };

  const filteredPartners = availablePartners.filter((partner) => 
    partner.businessName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.companyName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    partner.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    `${partner.firstName} ${partner.lastName}`.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Business Partnerships
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Manage your business connections and partnerships to streamline your supply chain
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2 xl:grid-cols-3">
          {/* Current Partnerships - My Favorites */}
          <Card data-testid="card-current-partnerships" className="lg:col-span-2 xl:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                My Favorites ({partnerships.length})
              </CardTitle>
              <CardDescription>
                Your trusted business partners and connections
              </CardDescription>
            </CardHeader>
            <CardContent>
              {partnershipsLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="animate-pulse bg-gray-200 dark:bg-gray-700 h-16 rounded" />
                  ))}
                </div>
              ) : partnerships.length === 0 ? (
                <div className="text-center py-8">
                  <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500 dark:text-gray-400">No favorite partners yet</p>
                  <p className="text-sm text-gray-400 dark:text-gray-500">
                    Add trusted partners to your favorites for quick access
                  </p>
                </div>
              ) : (
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {partnerships.map((partnership) => (
                    <div
                      key={partnership.id}
                      className="flex items-center justify-between p-4 border rounded-lg bg-white dark:bg-gray-800 border-green-200 dark:border-green-800"
                      data-testid={`card-partnership-${partnership.id}`}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium text-gray-900 dark:text-white">
                            {partnership.partner.businessName || partnership.partner.companyName || 
                             `${partnership.partner.firstName} ${partnership.partner.lastName}`}
                          </h3>
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                          {getRoleDescription(partnership.partner.role)}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {partnership.partner.email}
                        </p>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        <Badge variant="default" className="bg-green-600">
                          Favorite
                        </Badge>
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {partnership.partnershipType}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Browse Partners by Role */}
          <Card data-testid="card-browse-partners" className="lg:col-span-2 xl:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building2 className="h-5 w-5" />
                Browse {user?.role === 'retailer' ? 'Distributors' : 
                       user?.role === 'distributor' ? 'Partners' : 'Distributors'}
              </CardTitle>
              <CardDescription>
                {user?.role === 'retailer' 
                  ? 'Find distributors to connect with (Note: You cannot connect directly with manufacturers)'
                  : user?.role === 'distributor'
                  ? 'Connect with retailers and manufacturers'
                  : 'Find distributors for your products'
                }
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search by company name, business name, or email..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                    data-testid="input-search-partners"
                  />
                </div>

                {partnersLoading ? (
                  <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="animate-pulse bg-gray-200 dark:bg-gray-700 h-16 rounded" />
                    ))}
                  </div>
                ) : filteredPartners.length === 0 ? (
                  <div className="text-center py-8">
                    <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500 dark:text-gray-400">
                      {searchTerm ? "No partners found" : "No available partners"}
                    </p>
                    <p className="text-sm text-gray-400 dark:text-gray-500">
                      {searchTerm ? "Try adjusting your search terms" : "All potential partners are already connected"}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {filteredPartners.map((partner) => (
                      <div
                        key={partner.id}
                        className="flex items-center justify-between p-4 border rounded-lg bg-white dark:bg-gray-800"
                        data-testid={`card-available-partner-${partner.id}`}
                      >
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900 dark:text-white mb-1">
                            {partner.businessName || partner.companyName || `${partner.firstName} ${partner.lastName}`}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-300">
                            {getRoleDescription(partner.role)}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {partner.email}
                          </p>
                          {partner.address && (
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              📍 {partner.address}
                            </p>
                          )}
                        </div>
                        <Dialog open={isAddPartnerOpen} onOpenChange={setIsAddPartnerOpen}>
                          <DialogTrigger asChild>
                            <Button 
                              size="sm" 
                              onClick={() => setIsAddPartnerOpen(true)}
                              data-testid={`button-connect-${partner.id}`}
                            >
                              Add to Favorites
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Add to Favorites</DialogTitle>
                              <DialogDescription>
                                Add {partner.businessName || partner.companyName || `${partner.firstName} ${partner.lastName}`} to your favorite partners
                              </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4">
                              <div>
                                <label className="text-sm font-medium">Partnership Type</label>
                                <Select 
                                  value={selectedPartnershipType} 
                                  onValueChange={setSelectedPartnershipType}
                                >
                                  <SelectTrigger data-testid="select-partnership-type">
                                    <SelectValue placeholder="Select partnership type" />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {user?.role === 'retailer' && (
                                      <SelectItem value="supplier">Supplier Partnership</SelectItem>
                                    )}
                                    {user?.role === 'distributor' && (
                                      <>
                                        <SelectItem value="supplier">Supplier Partnership</SelectItem>
                                        <SelectItem value="retailer">Retail Partnership</SelectItem>
                                      </>
                                    )}
                                    {user?.role === 'manufacturer' && (
                                      <SelectItem value="distributor">Distribution Partnership</SelectItem>
                                    )}
                                  </SelectContent>
                                </Select>
                              </div>
                              <div className="flex justify-end gap-2">
                                <Button 
                                  variant="outline" 
                                  onClick={() => setIsAddPartnerOpen(false)}
                                  data-testid="button-cancel-request"
                                >
                                  Cancel
                                </Button>
                                <Button 
                                  onClick={() => handleSendRequest(partner.id)}
                                  disabled={sendRequestMutation.isPending}
                                  data-testid="button-send-request"
                                >
                                  {sendRequestMutation.isPending ? "Adding..." : "Add to Favorites"}
                                </Button>
                              </div>
                            </div>
                          </DialogContent>
                        </Dialog>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Global Search - When Favorites Don't Have What You Need */}
          <Card data-testid="card-global-search" className="lg:col-span-2 xl:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5" />
                Global Search
              </CardTitle>
              <CardDescription>
                Can't find what you need from your favorites? Search globally by product name
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search for products (e.g., pencil box, notebook, mobile phones)..."
                    value={productSearchTerm}
                    onChange={(e) => setProductSearchTerm(e.target.value)}
                    className="pl-10"
                    data-testid="input-search-products"
                  />
                </div>

                {productSearchTerm.length > 2 && (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Global search for "{productSearchTerm}"
                      </p>
                      <Badge variant="outline" className="text-blue-600 border-blue-600">
                        Worldwide
                      </Badge>
                    </div>
                    
                    {globalSearchLoading ? (
                      <div className="space-y-4">
                        {[1, 2, 3].map((i) => (
                          <div key={i} className="animate-pulse bg-gray-200 dark:bg-gray-700 h-16 rounded" />
                        ))}
                      </div>
                    ) : globalSearchResults.length === 0 ? (
                      <div className="text-center py-8">
                        <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-500 dark:text-gray-400">No partners found with "{productSearchTerm}"</p>
                        <p className="text-sm text-gray-400 dark:text-gray-500">
                          Try different keywords or check spelling
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-4 max-h-96 overflow-y-auto">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            Found {globalSearchResults.length} {user?.role === 'retailer' ? 'distributors' : 
                                   user?.role === 'distributor' ? 'manufacturers' : 'partners'} with "{productSearchTerm}"
                          </p>
                          <Badge variant="secondary">
                            {user?.role === 'retailer' ? 'Distributors Only' : 
                             user?.role === 'distributor' ? 'Manufacturers Only' : 'Global'}
                          </Badge>
                        </div>
                        {globalSearchResults.map((partner) => (
                          <div
                            key={partner.id}
                            className="flex items-center justify-between p-4 border rounded-lg bg-white dark:bg-gray-800 border-blue-200 dark:border-blue-800"
                            data-testid={`card-global-search-${partner.id}`}
                          >
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-medium text-gray-900 dark:text-white">
                                  {partner.businessName || `${partner.firstName} ${partner.lastName}`}
                                </h3>
                                <Badge variant="outline" className="text-blue-600 border-blue-600">
                                  Has "{productSearchTerm}"
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-600 dark:text-gray-300">
                                {getRoleDescription(partner.role)}
                              </p>
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                {partner.email}
                              </p>
                              {partner.address && (
                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                  📍 {partner.address}
                                </p>
                              )}
                            </div>
                            <div className="flex flex-col gap-2">
                              <Button 
                                size="sm" 
                                variant="outline"
                                className="text-blue-600 border-blue-600 hover:bg-blue-50"
                                data-testid={`button-contact-${partner.id}`}
                              >
                                Contact
                              </Button>
                              <Dialog open={isGlobalSearchOpen} onOpenChange={setIsGlobalSearchOpen}>
                                <DialogTrigger asChild>
                                  <Button 
                                    size="sm"
                                    onClick={() => setIsGlobalSearchOpen(true)}
                                    data-testid={`button-connect-global-${partner.id}`}
                                  >
                                    Add to Favorites
                                  </Button>
                                </DialogTrigger>
                                <DialogContent>
                                  <DialogHeader>
                                    <DialogTitle>Add Global Partner to Favorites</DialogTitle>
                                    <DialogDescription>
                                      Add {partner.businessName || `${partner.firstName} ${partner.lastName}`} to your favorites. 
                                      They have the product "{productSearchTerm}" you were looking for.
                                    </DialogDescription>
                                  </DialogHeader>
                                  <div className="space-y-4">
                                    <div>
                                      <label className="text-sm font-medium">Partnership Type</label>
                                      <Select 
                                        value={selectedPartnershipType} 
                                        onValueChange={setSelectedPartnershipType}
                                      >
                                        <SelectTrigger data-testid="select-global-partnership-type">
                                          <SelectValue placeholder="Select partnership type" />
                                        </SelectTrigger>
                                        <SelectContent>
                                          {user?.role === 'retailer' && (
                                            <SelectItem value="supplier">Supplier Partnership</SelectItem>
                                          )}
                                          {user?.role === 'distributor' && (
                                            <SelectItem value="supplier">Supplier Partnership</SelectItem>
                                          )}
                                          {user?.role === 'manufacturer' && (
                                            <SelectItem value="distributor">Distribution Partnership</SelectItem>
                                          )}
                                        </SelectContent>
                                      </Select>
                                    </div>
                                    <div className="flex justify-end gap-2">
                                      <Button 
                                        variant="outline" 
                                        onClick={() => setIsGlobalSearchOpen(false)}
                                        data-testid="button-cancel-global-request"
                                      >
                                        Cancel
                                      </Button>
                                      <Button 
                                        onClick={() => handleSendRequest(partner.id)}
                                        disabled={sendRequestMutation.isPending}
                                        data-testid="button-send-global-request"
                                      >
                                        {sendRequestMutation.isPending ? "Adding..." : "Add to Favorites"}
                                      </Button>
                                    </div>
                                  </div>
                                </DialogContent>
                              </Dialog>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {productSearchTerm.length > 0 && productSearchTerm.length <= 2 && (
                  <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-2">
                    <Clock className="h-4 w-4" />
                    Type at least 3 characters to search globally...
                  </p>
                )}

                {productSearchTerm.length === 0 && (
                  <div className="text-center py-6">
                    <div className="text-gray-400 mb-2">💡</div>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      When your favorite partners don't have what you need,<br />
                      search here to find {user?.role === 'retailer' ? 'distributors worldwide' : 
                                          user?.role === 'distributor' ? 'manufacturers worldwide' : 'partners worldwide'}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}