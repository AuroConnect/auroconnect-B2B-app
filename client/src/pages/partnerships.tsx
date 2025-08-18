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
import type { User } from "@/hooks/useAuth";

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
  const [productSearchTerm, setProductSearchTerm] = useState("");
  const [isGlobalSearchOpen, setIsGlobalSearchOpen] = useState(false);

  // Fetch current partnerships
  const { data: partnerships = [], isLoading: partnershipsLoading } = useQuery<Partnership[]>({
    queryKey: ["api", "partnerships"],
    enabled: isAuthenticated,
  });

  // Fetch available partners to connect with
  const { data: availablePartners = [], isLoading: partnersLoading } = useQuery<Array<{
    id: string;
    firstName: string;
    lastName: string;
    email: string;
    companyName?: string;
    role: string;
    allowedPartnershipType?: string;
  }>>({
    queryKey: ["api", "partnerships", "available"],
    enabled: isAuthenticated,
  });

  // Global product search
  const { data: globalSearchResults = [], isLoading: globalSearchLoading } = useQuery<Array<{
    id: string;
    firstName: string;
    lastName: string;
    email: string;
    businessName?: string;
    role: string;
  }>>({
    queryKey: ["api", "partners", "search", productSearchTerm],
    enabled: isAuthenticated && productSearchTerm.length > 2,
  });

  // Fetch partnership rules
  const { data: partnershipRules } = useQuery<{
    userRole: string;
    userRules: {
      description: string;
      can_partner_with: string[];
    };
  }>({
    queryKey: ["api", "partnerships", "rules"],
    enabled: isAuthenticated,
  });

  // Send partnership request mutation
  const sendRequestMutation = useMutation({
    mutationFn: async ({ partnerId }: { partnerId: string }) => {
      await apiRequest("POST", "/api/partnerships/create-request", { partnerId });
    },
    onSuccess: () => {
      toast({
        title: "Partnership Request Sent",
        description: "Your partnership request has been sent successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ["api", "partnerships"] });
      queryClient.invalidateQueries({ queryKey: ["api", "partners", "available"] });
    },
    onError: (error: any) => {
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
      
      const errorMessage = error?.message || "Failed to send partnership request. Please try again.";
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    },
  });

  const handleSendRequest = (partnerId: string) => {
    sendRequestMutation.mutate({ partnerId });
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

        {/* Partnership Rules Section */}
        {partnershipRules && (
          <div className="mb-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="h-5 w-5" />
                  Partnership Rules
                </CardTitle>
                <CardDescription>
                  Understanding how partnerships work based on your business role
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
                    Your Role: {partnershipRules.userRole?.charAt(0).toUpperCase() + partnershipRules.userRole?.slice(1)}
                  </h4>
                  <p className="text-blue-800 dark:text-blue-200 text-sm mb-3">
                    {partnershipRules.userRules?.description}
                  </p>
                  <div className="space-y-2">
                    <p className="text-blue-800 dark:text-blue-200 text-sm font-medium">
                      You can partner with:
                    </p>
                    <ul className="list-disc list-inside text-blue-700 dark:text-blue-300 text-sm space-y-1">
                      {partnershipRules.userRules?.can_partner_with?.map((role: string) => (
                        <li key={role}>
                          {role.charAt(0).toUpperCase() + role.slice(1)}s
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        <div className="grid gap-6 lg:grid-cols-3">
          {/* Current Partnerships */}
          <Card data-testid="card-current-partnerships">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Current Partnerships ({partnerships.length})
              </CardTitle>
              <CardDescription>
                Your active business partnerships and connection requests
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
                  <p className="text-gray-500 dark:text-gray-400">No partnerships yet</p>
                  <p className="text-sm text-gray-400 dark:text-gray-500">
                    Start building your network by adding business partners
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {partnerships.map((partnership) => (
                    <div
                      key={partnership.id}
                      className="flex items-center justify-between p-4 border rounded-lg bg-white dark:bg-gray-800"
                      data-testid={`card-partnership-${partnership.id}`}
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-medium text-gray-900 dark:text-white">
                            {partnership.partner.companyName || 
                             `${partnership.partner.firstName} ${partnership.partner.lastName}`}
                          </h3>
                          {getStatusIcon(partnership.status)}
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-300">
                          {getRoleDescription(partnership.partner.role)}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {partnership.partner.email}
                        </p>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        {getStatusBadge(partnership.status)}
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

          {/* Add New Partnership */}
          <Card data-testid="card-add-partnership">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                Find New Partners
              </CardTitle>
              <CardDescription>
                Discover and connect with potential business partners
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search partners by company or name..."
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
                            {partner.companyName || `${partner.firstName} ${partner.lastName}`}
                          </h3>
                          <p className="text-sm text-gray-600 dark:text-gray-300">
                            {getRoleDescription(partner.role)}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {partner.email}
                          </p>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {partner.allowedPartnershipType?.replace('_', ' ').toLowerCase()}
                          </Badge>
                          <Button 
                            size="sm" 
                            onClick={() => handleSendRequest(partner.id)}
                            disabled={sendRequestMutation.isPending}
                            data-testid={`button-connect-${partner.id}`}
                          >
                            {sendRequestMutation.isPending ? "Sending..." : "Connect"}
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Global Product Search */}
          <Card data-testid="card-global-search">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="h-5 w-5" />
                Global Product Search
              </CardTitle>
              <CardDescription>
                Search for products across all partners when your favorites don't have what you need
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                  <Input
                    placeholder="Search for products (e.g., pencil box, notebook)..."
                    value={productSearchTerm}
                    onChange={(e) => setProductSearchTerm(e.target.value)}
                    className="pl-10"
                    data-testid="input-search-products"
                  />
                </div>

                {productSearchTerm.length > 2 && (
                  <div className="space-y-2">
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Searching for "{productSearchTerm}"...
                    </p>
                    
                    {globalSearchLoading ? (
                      <div className="space-y-4">
                        {[1, 2, 3].map((i) => (
                          <div key={i} className="animate-pulse bg-gray-200 dark:bg-gray-700 h-16 rounded" />
                        ))}
                      </div>
                    ) : globalSearchResults.length === 0 ? (
                      <div className="text-center py-8">
                        <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-500 dark:text-gray-400">No partners found with this product</p>
                        <p className="text-sm text-gray-400 dark:text-gray-500">
                          Try searching for a different product or check spelling
                        </p>
                      </div>
                    ) : (
                      <div className="space-y-4 max-h-96 overflow-y-auto">
                        <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
                          Found {globalSearchResults.length} partners with "{productSearchTerm}"
                        </p>
                        {globalSearchResults.map((partner) => (
                          <div
                            key={partner.id}
                            className="flex items-center justify-between p-4 border rounded-lg bg-white dark:bg-gray-800 border-green-200 dark:border-green-800"
                            data-testid={`card-global-search-${partner.id}`}
                          >
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <h3 className="font-medium text-gray-900 dark:text-white">
                                  {partner.businessName || `${partner.firstName} ${partner.lastName}`}
                                </h3>
                                <Badge variant="outline" className="text-green-600 border-green-600">
                                  Has Product
                                </Badge>
                              </div>
                              <p className="text-sm text-gray-600 dark:text-gray-300">
                                {getRoleDescription(partner.role)}
                              </p>
                              <p className="text-xs text-gray-500 dark:text-gray-400">
                                {partner.email}
                              </p>
                            </div>
                            <div className="flex flex-col gap-2">
                              <Button 
                                size="sm" 
                                variant="outline"
                                className="text-green-600 border-green-600 hover:bg-green-50"
                                data-testid={`button-contact-${partner.id}`}
                              >
                                Contact
                              </Button>
                              <Button 
                                size="sm"
                                onClick={() => handleSendRequest(partner.id)}
                                data-testid={`button-connect-global-${partner.id}`}
                              >
                                Connect
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {productSearchTerm.length > 0 && productSearchTerm.length <= 2 && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Type at least 3 characters to search for products
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}