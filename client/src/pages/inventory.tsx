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
  Bell,
  DollarSign
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
  const [isBulkUploading, setIsBulkUploading] = useState(false);
  const [bulkUploadResults, setBulkUploadResults] = useState<any[]>([]);
  const [showBulkResults, setShowBulkResults] = useState(false);

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

  // Bulk Upload Mutation
  const bulkUploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await apiRequest("POST", "/api/inventory/bulk-upload", formData, true);
      return response.json ? await response.json() : response;
    },
    onSuccess: (data) => {
      setBulkUploadResults(data.results || []);
      setShowBulkResults(true);
      setIsBulkUploading(false);
      queryClient.invalidateQueries({ queryKey: ["api", "inventory"] });
      toast({
        title: "Bulk Upload Complete",
        description: `Processed ${data.results?.length || 0} inventory items`,
        variant: "default",
      });
    },
    onError: (error: any) => {
      setIsBulkUploading(false);
      toast({
        title: "Bulk Upload Failed",
        description: error.message || "Failed to upload inventory",
        variant: "destructive",
      });
    }
  });

  // Download Sample CSV
  const downloadSampleCSV = () => {
    const sampleData = [
      {
        productId: "sample-product-1",
        quantity: "100",
        sellingPrice: "150.00",
        lowStockThreshold: "10",
        autoRestockQuantity: "50"
      },
      {
        productId: "sample-product-2",
        quantity: "75",
        sellingPrice: "200.00",
        lowStockThreshold: "15",
        autoRestockQuantity: "60"
      },
      {
        productId: "sample-product-3",
        quantity: "50",
        sellingPrice: "120.00",
        lowStockThreshold: "5",
        autoRestockQuantity: "40"
      },
      {
        productId: "sample-product-4",
        quantity: "200",
        sellingPrice: "80.00",
        lowStockThreshold: "20",
        autoRestockQuantity: "100"
      }
    ];

    const csvContent = [
      "productId,quantity,sellingPrice,lowStockThreshold,autoRestockQuantity",
      ...sampleData.map(row => 
        `"${row.productId}","${row.quantity}","${row.sellingPrice}","${row.lowStockThreshold}","${row.autoRestockQuantity}"`
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_inventory.csv';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  const handleBulkUpload = () => {
    if (!bulkFile) {
      toast({
        title: "No File Selected",
        description: "Please select a CSV or Excel file to upload",
        variant: "destructive",
      });
      return;
    }

    setIsBulkUploading(true);
    bulkUploadMutation.mutate(bulkFile);
  };

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
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
              <div>
            <h1 className="text-2xl font-bold text-gray-900">Inventory Management</h1>
            <p className="text-gray-600 mt-1">
              Manage your product inventory, track stock levels, and set up alerts
            </p>
              </div>
              
          <div className="flex gap-2 mt-4 sm:mt-0">
                <Button
                  onClick={() => setIsBulkUploadOpen(true)}
              className="flex items-center gap-2"
                >
              <Upload className="h-4 w-4" />
                  Bulk Upload
                </Button>
                <Button
              onClick={() => setIsAddStockOpen(true)}
              className="flex items-center gap-2"
            >
              <Plus className="h-4 w-4" />
              Add Stock
                </Button>
              </div>
            </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="stock">Stock Items</TabsTrigger>
            <TabsTrigger value="alerts">Low Stock Alerts</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
            {/* Analytics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Items</CardTitle>
                <Package className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analytics?.analytics?.totalItems || 0}</div>
                <p className="text-xs text-muted-foreground">
                  Active inventory items
                </p>
                  </CardContent>
                </Card>
                
                <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Quantity</CardTitle>
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{analytics?.analytics?.totalQuantity || 0}</div>
                <p className="text-xs text-muted-foreground">
                  Units in stock
                </p>
                  </CardContent>
                </Card>
                
                <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Low Stock Items</CardTitle>
                <AlertTriangle className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">{analytics?.analytics?.lowStockCount || 0}</div>
                <p className="text-xs text-muted-foreground">
                  Need restocking
                </p>
                  </CardContent>
                </Card>
                
                <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Value</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">₹{(analytics?.analytics?.totalValue || 0).toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">
                  Inventory value
                </p>
              </CardContent>
            </Card>
                      </div>

          {/* Stock Level Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Stock Level Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {inventory?.slice(0, 5).map((item) => (
                  <div key={item.id} className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="font-medium">{item.productName}</p>
                      <p className="text-sm text-gray-500">SKU: {item.sku}</p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <p className="text-sm font-medium">{item.availableQuantity} / {item.quantity}</p>
                        <p className="text-xs text-gray-500">Available / Total</p>
                      </div>
                      <Progress 
                        value={(item.availableQuantity / item.quantity) * 100} 
                        className="w-20"
                      />
                    </div>
                  </div>
                ))}
                    </div>
                  </CardContent>
                </Card>
        </TabsContent>

        {/* Stock Items Tab */}
        <TabsContent value="stock" className="space-y-6">
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                  placeholder="Search inventory..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
              </div>
                  </div>
                  
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="All Status" />
                    </SelectTrigger>
                    <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="in-stock">In Stock</SelectItem>
                <SelectItem value="low-stock">Low Stock</SelectItem>
                <SelectItem value="out-of-stock">Out of Stock</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Inventory Table */}
                <Card>
                  <CardHeader>
              <CardTitle>Inventory Items</CardTitle>
                  </CardHeader>
                  <CardContent>
              {inventoryLoading ? (
                <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex items-center space-x-4 animate-pulse">
                      <div className="h-12 w-12 bg-gray-200 rounded"></div>
                      <div className="flex-1 space-y-2">
                        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredInventory.map((item) => (
                    <div key={item.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                          <Package className="h-6 w-6 text-gray-500" />
                        </div>
                                <div>
                          <h3 className="font-medium">{item.productName}</h3>
                          <p className="text-sm text-gray-500">SKU: {item.sku}</p>
                                </div>
                                  </div>
                      
                      <div className="flex items-center space-x-6">
                        <div className="text-right">
                          <p className="font-medium">₹{item.sellingPrice}</p>
                          <p className="text-sm text-gray-500">Selling Price</p>
                        </div>
                        
                        <div className="text-right">
                          <p className={`font-medium ${
                            item.isLowStock ? 'text-orange-600' : 
                            item.availableQuantity === 0 ? 'text-red-600' : 'text-green-600'
                          }`}>
                            {item.availableQuantity}
                          </p>
                          <p className="text-sm text-gray-500">Available</p>
                                </div>
                        
                        <div className="flex items-center space-x-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => {
                                    setSelectedItem(item);
                                    setIsAddStockOpen(true);
                                  }}
                                >
                            <Plus className="h-4 w-4" />
                                </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedItem(item);
                              setIsSettingsOpen(true);
                            }}
                          >
                            <Settings className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                    </div>
              )}
                  </CardContent>
                </Card>
              </TabsContent>

        {/* Low Stock Alerts Tab */}
        <TabsContent value="alerts" className="space-y-6">
                <Card>
                  <CardHeader>
              <CardTitle>Low Stock Alerts</CardTitle>
                  </CardHeader>
                  <CardContent>
              {inventoryLoading ? (
                      <div className="space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex items-center space-x-4 animate-pulse">
                      <div className="h-12 w-12 bg-gray-200 rounded"></div>
                      <div className="flex-1 space-y-2">
                        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="space-y-4">
                  {inventory?.filter(item => item.isLowStock || item.needsRestock).map((item) => (
                    <div key={item.id} className="flex items-center justify-between p-4 border border-orange-200 rounded-lg bg-orange-50">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                          <AlertTriangle className="h-6 w-6 text-orange-600" />
                        </div>
                        <div>
                          <h3 className="font-medium">{item.productName}</h3>
                          <p className="text-sm text-gray-500">SKU: {item.sku}</p>
                              <p className="text-sm text-orange-600">
                            Current: {item.availableQuantity} | Threshold: {item.lowStockThreshold}
                              </p>
                            </div>
                      </div>
                      
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <p className="font-medium text-orange-600">{item.availableQuantity}</p>
                          <p className="text-sm text-gray-500">Available</p>
                        </div>
                        
                              <Button
                                onClick={() => {
                                  setSelectedItem(item);
                            setStockAdjustment({
                              quantity: item.autoRestockQuantity.toString(),
                              reason: "Auto restock - low stock alert",
                              type: "add"
                            });
                                  setIsAddStockOpen(true);
                                }}
                          className="bg-orange-600 hover:bg-orange-700"
                              >
                          <Plus className="h-4 w-4 mr-2" />
                                Restock
                              </Button>
                            </div>
                          </div>
                        ))}
                  
                  {inventory?.filter(item => item.isLowStock || item.needsRestock).length === 0 && (
                      <div className="text-center py-8">
                      <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900">All Good!</h3>
                      <p className="text-gray-500">No low stock alerts at the moment.</p>
                    </div>
                  )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                <CardTitle>Stock Level Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">In Stock</span>
                    <span className="text-sm font-medium text-green-600">
                      {inventory?.filter(item => !item.isLowStock && item.availableQuantity > 0).length || 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Low Stock</span>
                    <span className="text-sm font-medium text-orange-600">
                      {inventory?.filter(item => item.isLowStock).length || 0}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Out of Stock</span>
                    <span className="text-sm font-medium text-red-600">
                      {inventory?.filter(item => item.availableQuantity === 0).length || 0}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Performing Items</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {inventory?.slice(0, 5).map((item, index) => (
                    <div key={item.id} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-sm font-medium text-blue-600">{index + 1}</span>
                        </div>
                        <div>
                          <p className="font-medium text-sm">{item.productName}</p>
                          <p className="text-xs text-gray-500">{item.sku}</p>
                            </div>
                            </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">₹{item.sellingPrice}</p>
                        <p className="text-xs text-gray-500">Price</p>
                            </div>
                            </div>
                  ))}
                          </div>
              </CardContent>
            </Card>
                        </div>
        </TabsContent>

        {/* Bulk Upload Dialog */}
        <Dialog open={isBulkUploadOpen} onOpenChange={setIsBulkUploadOpen}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Bulk Upload Inventory</DialogTitle>
              <DialogDescription>
                Upload multiple inventory items using CSV or Excel file
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                  <h4 className="font-medium">Download Sample File</h4>
                  <p className="text-sm text-gray-500">Get the correct format for bulk upload</p>
                </div>
                <Button onClick={downloadSampleCSV} variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Download Sample CSV
                </Button>
              </div>
              
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">
                    {bulkFile ? bulkFile.name : "Drop your CSV or Excel file here, or click to browse"}
                  </p>
                  <input
                    type="file"
                    accept=".csv,.xlsx,.xls"
                    onChange={(e) => setBulkFile(e.target.files?.[0] || null)}
                    className="hidden"
                    id="bulk-upload"
                  />
                  <label htmlFor="bulk-upload" className="cursor-pointer">
                    <Button variant="outline" size="sm">
                      Choose File
                    </Button>
                  </label>
                </div>
              </div>
              
              {bulkFile && (
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <FileSpreadsheet className="h-5 w-5 text-blue-500" />
                    <span className="text-sm font-medium">{bulkFile.name}</span>
                    <span className="text-xs text-gray-500">
                      ({(bulkFile.size / 1024).toFixed(1)} KB)
                              </span>
                            </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setBulkFile(null)}
                  >
                    <XCircle className="h-4 w-4" />
                  </Button>
                            </div>
              )}
                            </div>
            
            <div className="flex justify-end gap-2 pt-4">
              <Button variant="outline" onClick={() => setIsBulkUploadOpen(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleBulkUpload}
                disabled={!bulkFile || isBulkUploading}
              >
                {isBulkUploading ? "Uploading..." : "Upload Inventory"}
              </Button>
                            </div>
          </DialogContent>
        </Dialog>

        {/* Bulk Upload Results Dialog */}
        <Dialog open={showBulkResults} onOpenChange={setShowBulkResults}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Bulk Upload Results</DialogTitle>
              <DialogDescription>
                Results of your bulk inventory upload
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-sm">
                      {bulkUploadResults.filter(r => r.status === 'success').length} Successful
                    </span>
                          </div>
                  <div className="flex items-center space-x-2">
                    <XCircle className="h-4 w-4 text-red-500" />
                    <span className="text-sm">
                      {bulkUploadResults.filter(r => r.status === 'error').length} Failed
                    </span>
                        </div>
                      </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setShowBulkResults(false);
                    setBulkUploadResults([]);
                    setBulkFile(null);
                    setIsBulkUploadOpen(false);
                  }}
                >
                  Close
                </Button>
              </div>
              
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {bulkUploadResults.map((result, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg border ${
                      result.status === 'success' 
                        ? 'bg-green-50 border-green-200' 
                        : 'bg-red-50 border-red-200'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2">
                          {result.status === 'success' ? (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-500" />
                          )}
                          <span className="font-medium">
                            {result.productName || `Row ${index + 1}`}
                          </span>
                      </div>
                        {result.status === 'error' && (
                          <p className="text-sm text-red-600 mt-1">
                            {result.error}
                          </p>
                        )}
                        {result.status === 'success' && (
                          <p className="text-sm text-green-600 mt-1">
                            Inventory updated successfully
                          </p>
                        )}
          </div>
        </div>
      </div>
                ))}
              </div>
            </div>
          </DialogContent>
        </Dialog>

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

        {/* Settings Dialog */}
        <Dialog open={isSettingsOpen} onOpenChange={setIsSettingsOpen}>
        <DialogContent>
          <DialogHeader>
              <DialogTitle>Settings</DialogTitle>
            <DialogDescription>
                Manage application settings
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
                <h3 className="font-medium">Application Settings</h3>
                <p className="text-sm text-gray-600">
                  Configure application-wide settings here.
              </p>
            </div>
              <div>
                <h3 className="font-medium">Notifications</h3>
                <p className="text-sm text-gray-600">
                  Enable or disable notifications for low stock alerts.
                </p>
          </div>
            </div>
          <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setIsSettingsOpen(false)}>
                Close
            </Button>
          </div>
        </DialogContent>
      </Dialog>
      </div>

      <MobileNav />
    </div>
  );
}
