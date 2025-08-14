import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";
import Header from "@/components/layout/header";
import MobileNav from "@/components/layout/mobile-nav";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { 
  Search, 
  Filter, 
  Plus, 
  Edit, 
  Trash2, 
  Package, 
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Download,
  Upload,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  XCircle,
  FileSpreadsheet,
  Settings,
  Bell
} from "lucide-react";

interface InventoryItem {
  id: string;
  productId: string;
  productName: string;
  sku: string;
  quantity: number;
  reservedQuantity: number;
  availableQuantity: number;
  lowStockThreshold: number;
  autoRestockQuantity: number;
  isLowStock: boolean;
  needsRestock: boolean;
  sellingPrice: number;
  isAvailable: boolean;
  lastRestockDate: string;
  createdAt: string;
  updatedAt: string;
}

interface InventoryAnalytics {
  totalItems: number;
  totalQuantity: number;
  totalReserved: number;
  totalAvailable: number;
  lowStockCount: number;
  outOfStockCount: number;
  totalValue: number;
  averageStockLevel: number;
}

export default function Inventory() {
  const { user, isLoading } = useAuth();
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [isAddStockOpen, setIsAddStockOpen] = useState(false);
  const [isBulkUploadOpen, setIsBulkUploadOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [stockAdjustment, setStockAdjustment] = useState({
    quantity: "",
    reason: "",
    type: "add" as "add" | "subtract"
  });
  const [bulkFile, setBulkFile] = useState<File | null>(null);
  const [activeTab, setActiveTab] = useState("overview");

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

  // Fetch inventory data
  const { data: inventoryData, isLoading: inventoryLoading, error: inventoryError } = useQuery<{
    inventory: InventoryItem[];
    summary: {
      totalItems: number;
      lowStockItems: number;
      outOfStockItems: number;
    };
  }>({
    queryKey: ["api", "inventory"],
    enabled: !!user && !isLoading,
    retry: 3,
    staleTime: 30000,
  });

  // Fetch inventory analytics
  const { data: analytics, isLoading: analyticsLoading } = useQuery<{
    analytics: InventoryAnalytics;
  }>({
    queryKey: ["api", "inventory", "analytics"],
    enabled: !!user && !isLoading,
    retry: 3,
    staleTime: 30000,
  });

  // Fetch low stock alerts
  const { data: lowStockAlerts, isLoading: lowStockLoading } = useQuery<{
    lowStockItems: InventoryItem[];
    count: number;
  }>({
    queryKey: ["api", "inventory", "low-stock"],
    enabled: !!user && !isLoading,
    retry: 3,
    staleTime: 30000,
  });

  const inventory = inventoryData?.inventory || [];
  const analyticsData = analytics?.analytics;

  // Update stock mutation
  const updateStockMutation = useMutation({
    mutationFn: async ({ itemId, quantity, reason, type }: { itemId: string; quantity: number; reason: string; type: string }) => {
      const response = await apiRequest("PUT", `/api/inventory/${itemId}`, { 
        quantity, 
        reason, 
        type 
      });
      return response.json();
    },
    onSuccess: () => {
      toast({
        title: "Stock Updated",
        description: "Inventory stock has been updated successfully.",
      });
      queryClient.invalidateQueries({ queryKey: ["api", "inventory"] });
      setIsAddStockOpen(false);
      setStockAdjustment({ quantity: "", reason: "", type: "add" });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to update stock.",
        variant: "destructive",
      });
    },
  });

  // Auto-restock mutation
  const autoRestockMutation = useMutation({
    mutationFn: async () => {
      const response = await apiRequest("POST", "/api/inventory/auto-restock");
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Auto-Restock Completed",
        description: `Successfully restocked ${data.restockedItems?.length || 0} items.`,
      });
      queryClient.invalidateQueries({ queryKey: ["api", "inventory"] });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to auto-restock.",
        variant: "destructive",
      });
    },
  });

  // Bulk upload mutation
  const bulkUploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await apiRequest("POST", "/api/inventory/bulk-update", formData, true);
      return response.json();
    },
    onSuccess: (data) => {
      toast({
        title: "Bulk Upload Completed",
        description: `Successfully updated ${data.results?.success || 0} items.`,
      });
      queryClient.invalidateQueries({ queryKey: ["api", "inventory"] });
      setIsBulkUploadOpen(false);
      setBulkFile(null);
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to upload file.",
        variant: "destructive",
      });
    },
  });

  // Filter inventory items
  const filteredInventory = inventory.filter((item: InventoryItem) => {
    const matchesSearch = item.productName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.sku.toLowerCase().includes(searchTerm.toLowerCase());
    
    let matchesStatus = true;
    if (statusFilter === "low_stock") matchesStatus = item.isLowStock;
    else if (statusFilter === "out_of_stock") matchesStatus = item.availableQuantity === 0;
    else if (statusFilter === "available") matchesStatus = item.availableQuantity > 0;
    
    return matchesSearch && matchesStatus;
  });

  const handleUpdateStock = () => {
    if (!selectedItem || !stockAdjustment.quantity || !stockAdjustment.reason) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields.",
        variant: "destructive",
      });
      return;
    }

    const quantity = parseInt(stockAdjustment.quantity);
    if (isNaN(quantity) || quantity <= 0) {
      toast({
        title: "Invalid Quantity",
        description: "Please enter a valid quantity.",
        variant: "destructive",
      });
      return;
    }

    updateStockMutation.mutate({
      itemId: selectedItem.id,
      quantity,
      reason: stockAdjustment.reason,
      type: stockAdjustment.type,
    });
  };

  const handleAutoRestock = () => {
    autoRestockMutation.mutate();
  };

  const handleBulkUpload = () => {
    if (!bulkFile) {
      toast({
        title: "No File Selected",
        description: "Please select a file to upload.",
        variant: "destructive",
      });
      return;
    }

    bulkUploadMutation.mutate(bulkFile);
  };

  const getStatusBadge = (item: InventoryItem) => {
    if (item.availableQuantity === 0) {
      return <Badge variant="destructive">Out of Stock</Badge>;
    } else if (item.isLowStock) {
      return <Badge variant="secondary">Low Stock</Badge>;
    } else {
      return <Badge variant="default">In Stock</Badge>;
    }
  };

  const getStockProgress = (item: InventoryItem) => {
    const percentage = (item.availableQuantity / (item.lowStockThreshold * 2)) * 100;
    return Math.min(percentage, 100);
  };

  if (isLoading || inventoryLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading inventory...</p>
          </div>
        </div>
        <MobileNav />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Main Content */}
          <div className="flex-1">
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4 mb-6">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Inventory Management</h1>
                <p className="text-gray-600 mt-1">Manage your product inventory and stock levels</p>
              </div>
              
              <div className="flex flex-wrap gap-2">
                <Button
                  onClick={() => setIsBulkUploadOpen(true)}
                  variant="outline"
                  size="sm"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Bulk Upload
                </Button>
                <Button
                  onClick={handleAutoRestock}
                  disabled={autoRestockMutation.isPending}
                  variant="outline"
                  size="sm"
                >
                  <RefreshCw className={`w-4 h-4 mr-2 ${autoRestockMutation.isPending ? 'animate-spin' : ''}`} />
                  Auto Restock
                </Button>
                <Button
                  onClick={() => setIsSettingsOpen(true)}
                  variant="outline"
                  size="sm"
                >
                  <Settings className="w-4 h-4 mr-2" />
                  Settings
                </Button>
              </div>
            </div>

            {/* Analytics Cards */}
            {analyticsData && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Total Items</p>
                        <p className="text-2xl font-bold text-gray-900">{analyticsData.totalItems}</p>
                      </div>
                      <Package className="w-8 h-8 text-blue-600" />
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Available Stock</p>
                        <p className="text-2xl font-bold text-gray-900">{analyticsData.totalAvailable}</p>
                      </div>
                      <CheckCircle className="w-8 h-8 text-green-600" />
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Low Stock Items</p>
                        <p className="text-2xl font-bold text-orange-600">{analyticsData.lowStockCount}</p>
                      </div>
                      <AlertTriangle className="w-8 h-8 text-orange-600" />
                    </div>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-gray-600">Total Value</p>
                        <p className="text-2xl font-bold text-gray-900">₹{analyticsData.totalValue?.toLocaleString()}</p>
                      </div>
                      <BarChart3 className="w-8 h-8 text-purple-600" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="low-stock">Low Stock Alerts</TabsTrigger>
                <TabsTrigger value="analytics">Analytics</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="mt-6">
                {/* Search and Filters */}
                <div className="flex flex-col lg:flex-row gap-4 mb-6">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input
                      placeholder="Search products by name or SKU..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-full lg:w-48">
                      <SelectValue placeholder="Filter by status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Items</SelectItem>
                      <SelectItem value="available">Available</SelectItem>
                      <SelectItem value="low_stock">Low Stock</SelectItem>
                      <SelectItem value="out_of_stock">Out of Stock</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Inventory Table */}
                <Card>
                  <CardHeader>
                    <CardTitle>Inventory Items ({filteredInventory.length})</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left py-3 px-4 font-medium">Product</th>
                            <th className="text-left py-3 px-4 font-medium">SKU</th>
                            <th className="text-left py-3 px-4 font-medium">Stock Level</th>
                            <th className="text-left py-3 px-4 font-medium">Status</th>
                            <th className="text-left py-3 px-4 font-medium">Price</th>
                            <th className="text-left py-3 px-4 font-medium">Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {filteredInventory.map((item: InventoryItem) => (
                            <tr key={item.id} className="border-b hover:bg-gray-50">
                              <td className="py-3 px-4">
                                <div>
                                  <p className="font-medium">{item.productName}</p>
                                  <p className="text-sm text-gray-500">ID: {item.productId}</p>
                                </div>
                              </td>
                              <td className="py-3 px-4">
                                <code className="bg-gray-100 px-2 py-1 rounded text-sm">{item.sku}</code>
                              </td>
                              <td className="py-3 px-4">
                                <div className="space-y-2">
                                  <div className="flex justify-between text-sm">
                                    <span>Available: {item.availableQuantity}</span>
                                    <span>Reserved: {item.reservedQuantity}</span>
                                  </div>
                                  <Progress value={getStockProgress(item)} className="h-2" />
                                  <p className="text-xs text-gray-500">
                                    Threshold: {item.lowStockThreshold}
                                  </p>
                                </div>
                              </td>
                              <td className="py-3 px-4">
                                {getStatusBadge(item)}
                              </td>
                              <td className="py-3 px-4">
                                ₹{item.sellingPrice?.toLocaleString() || 'N/A'}
                              </td>
                              <td className="py-3 px-4">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => {
                                    setSelectedItem(item);
                                    setIsAddStockOpen(true);
                                  }}
                                >
                                  <Edit className="w-4 h-4 mr-1" />
                                  Update
                                </Button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="low-stock" className="mt-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="w-5 h-5 text-orange-600" />
                      Low Stock Alerts ({lowStockAlerts?.lowStockItems?.length || 0})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {lowStockAlerts?.lowStockItems?.length > 0 ? (
                      <div className="space-y-4">
                        {lowStockAlerts.lowStockItems.map((item: InventoryItem) => (
                          <div key={item.id} className="flex items-center justify-between p-4 border rounded-lg bg-orange-50">
                            <div className="flex-1">
                              <h4 className="font-medium">{item.productName}</h4>
                              <p className="text-sm text-gray-600">SKU: {item.sku}</p>
                              <p className="text-sm text-orange-600">
                                Available: {item.availableQuantity} / Threshold: {item.lowStockThreshold}
                              </p>
                            </div>
                            <div className="flex gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  setSelectedItem(item);
                                  setIsAddStockOpen(true);
                                }}
                              >
                                Restock
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <CheckCircle className="w-12 h-12 text-green-600 mx-auto mb-4" />
                        <p className="text-gray-600">No low stock alerts at the moment!</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="analytics" className="mt-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Inventory Analytics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {analyticsData ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <h4 className="font-medium mb-4">Stock Distribution</h4>
                          <div className="space-y-3">
                            <div className="flex justify-between">
                              <span>Total Quantity</span>
                              <span className="font-medium">{analyticsData.totalQuantity}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Reserved Stock</span>
                              <span className="font-medium">{analyticsData.totalReserved}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Available Stock</span>
                              <span className="font-medium">{analyticsData.totalAvailable}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Average Stock Level</span>
                              <span className="font-medium">{Math.round(analyticsData.averageStockLevel)}</span>
                            </div>
                          </div>
                        </div>
                        
                        <div>
                          <h4 className="font-medium mb-4">Stock Status</h4>
                          <div className="space-y-3">
                            <div className="flex justify-between">
                              <span>In Stock Items</span>
                              <span className="font-medium text-green-600">
                                {analyticsData.totalItems - analyticsData.lowStockCount - analyticsData.outOfStockCount}
                              </span>
                            </div>
                            <div className="flex justify-between">
                              <span>Low Stock Items</span>
                              <span className="font-medium text-orange-600">{analyticsData.lowStockCount}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Out of Stock Items</span>
                              <span className="font-medium text-red-600">{analyticsData.outOfStockCount}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Total Value</span>
                              <span className="font-medium">₹{analyticsData.totalValue?.toLocaleString()}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <p className="text-gray-600">No analytics data available</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>

      {/* Update Stock Dialog */}
      <Dialog open={isAddStockOpen} onOpenChange={setIsAddStockOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Update Stock Level</DialogTitle>
            <DialogDescription>
              Update the stock level for {selectedItem?.productName}
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="quantity">Quantity</Label>
              <Input
                id="quantity"
                type="number"
                value={stockAdjustment.quantity}
                onChange={(e) => setStockAdjustment({ ...stockAdjustment, quantity: e.target.value })}
                placeholder="Enter quantity"
              />
            </div>
            
            <div>
              <Label htmlFor="type">Type</Label>
              <Select
                value={stockAdjustment.type}
                onValueChange={(value: "add" | "subtract") => setStockAdjustment({ ...stockAdjustment, type: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="add">Add Stock</SelectItem>
                  <SelectItem value="subtract">Remove Stock</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="reason">Reason</Label>
              <Input
                id="reason"
                value={stockAdjustment.reason}
                onChange={(e) => setStockAdjustment({ ...stockAdjustment, reason: e.target.value })}
                placeholder="Enter reason for adjustment"
              />
            </div>
          </div>
          
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsAddStockOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleUpdateStock}
              disabled={updateStockMutation.isPending}
            >
              {updateStockMutation.isPending ? "Updating..." : "Update Stock"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Bulk Upload Dialog */}
      <Dialog open={isBulkUploadOpen} onOpenChange={setIsBulkUploadOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Bulk Upload Inventory</DialogTitle>
            <DialogDescription>
              Upload an Excel file to update multiple inventory items at once.
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="file">Excel File</Label>
              <Input
                id="file"
                type="file"
                accept=".xlsx,.xls"
                onChange={(e) => setBulkFile(e.target.files?.[0] || null)}
              />
              <p className="text-sm text-gray-500 mt-1">
                File should contain: SKU, Quantity, Low Stock Threshold, Auto Restock Quantity, Selling Price
              </p>
            </div>
          </div>
          
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsBulkUploadOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleBulkUpload}
              disabled={bulkUploadMutation.isPending || !bulkFile}
            >
              {bulkUploadMutation.isPending ? "Uploading..." : "Upload"}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <MobileNav />
    </div>
  );
}
