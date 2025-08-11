import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ShoppingCart, Eye, Package, Edit, Trash2 } from "lucide-react";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

interface ProductGridProps {
  products: any[];
  isLoading: boolean;
  userRole: string;
  categories?: any[];
}

export default function ProductGrid({ products, isLoading, userRole, categories = [] }: ProductGridProps) {
  const { toast } = useToast();
  const queryClient = useQueryClient();
  const [editingProduct, setEditingProduct] = useState<any>(null);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editForm, setEditForm] = useState({
    name: "",
    description: "",
    sku: "",
    categoryId: "",
    basePrice: "",
    imageUrl: "",
    isActive: true
  });

  // Update product mutation
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
      queryClient.invalidateQueries({ queryKey: ["api", "products"] });
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

  // Delete product mutation
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
      queryClient.invalidateQueries({ queryKey: ["api", "products"] });
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

  const handleEditProduct = (product: any) => {
    setEditingProduct(product);
    setEditForm({
      name: product.name || "",
      description: product.description || "",
      sku: product.sku || "",
      categoryId: product.categoryId || "",
      basePrice: product.basePrice?.toString() || "",
      imageUrl: product.imageUrl || "",
      isActive: product.isActive !== false
    });
    setIsEditDialogOpen(true);
  };

  const handleUpdateProduct = () => {
    if (!editForm.name || !editForm.sku || !editForm.basePrice) {
      toast({
        title: "Missing Information",
        description: "Please fill in all required fields.",
        variant: "destructive",
      });
      return;
    }

    const productData = {
      name: editForm.name,
      description: editForm.description,
      sku: editForm.sku,
      basePrice: parseFloat(editForm.basePrice),
      categoryId: editForm.categoryId || null,
      imageUrl: editForm.imageUrl || null,
      isActive: editForm.isActive
    };

    updateProductMutation.mutate(productData);
  };

  const handleDeleteProduct = () => {
    if (confirm("Are you sure you want to delete this product? This action cannot be undone.")) {
      deleteProductMutation.mutate();
    }
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
          <Card key={i} className="animate-pulse">
            <div className="aspect-square bg-gray-200 rounded-t-lg"></div>
            <CardContent className="p-4">
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-6 bg-gray-200 rounded w-1/3"></div>
            </CardContent>
            <CardFooter className="p-4 pt-0">
              <div className="h-9 bg-gray-200 rounded w-full"></div>
            </CardFooter>
          </Card>
        ))}
      </div>
    );
  }

  if (!products || products.length === 0) {
    return (
      <div className="text-center py-12">
        <Package className="h-16 w-16 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Products Found</h3>
        <p className="text-gray-500">Try adjusting your search or filter criteria.</p>
      </div>
    );
  }

  // Add to cart mutation
  const addToCartMutation = useMutation({
    mutationFn: async (product: any) => {
      return apiRequest(`/api/cart/add`, {
        method: "POST",
        body: JSON.stringify({
          productId: product.id,
          quantity: 1
        }),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["api", "cart"] });
      toast({
        title: "Added to Cart",
        description: "Product has been added to your cart successfully.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to add product to cart.",
        variant: "destructive",
      });
    },
  });

  const handleAddToCart = (product: any) => {
    addToCartMutation.mutate(product);
  };

  const getActionButton = (product: any) => {
    switch (userRole) {
      case 'retailer':
        return (
          <Button 
            className="w-full" 
            onClick={() => handleAddToCart(product)}
            disabled={addToCartMutation.isPending}
            data-testid={`button-add-to-cart-${product.id}`}
          >
            <ShoppingCart className="h-4 w-4 mr-2" />
            {addToCartMutation.isPending ? "Adding..." : "Add to Cart"}
          </Button>
        );
      case 'distributor':
        return (
          <Button 
            variant="outline" 
            className="w-full"
            data-testid={`button-manage-stock-${product.id}`}
          >
            <Package className="h-4 w-4 mr-2" />
            Manage Stock
          </Button>
        );
      case 'manufacturer':
        return (
          <div className="flex gap-2 w-full">
            <Button 
              variant="outline" 
              className="flex-1"
              onClick={() => handleEditProduct(product)}
              data-testid={`button-edit-product-${product.id}`}
            >
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => handleEditProduct(product)}
              data-testid={`button-view-product-${product.id}`}
            >
              <Eye className="h-4 w-4" />
            </Button>
          </div>
        );
      default:
        return (
          <Button 
            variant="outline" 
            className="w-full"
            data-testid={`button-view-product-${product.id}`}
          >
            <Eye className="h-4 w-4 mr-2" />
            View Details
          </Button>
        );
    }
  };

  return (
    <>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {products.map((product) => (
          <Card key={product.id} className="group hover:shadow-lg transition-shadow" data-testid={`product-card-${product.id}`}>
                         <div className="aspect-square bg-gray-100 rounded-t-lg relative overflow-hidden">
               {product.imageUrl ? (
                 <img 
                   src={product.imageUrl} 
                   alt={product.name}
                   className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                 />
               ) : (
                 <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
                   <Package className="h-16 w-16 text-gray-400" />
                 </div>
               )}
               <div className="absolute top-2 right-2 flex gap-1">
                 <Badge variant="secondary" className="bg-white/90 text-gray-700">
                   {product.sku}
                 </Badge>
                 {product.isActive === false && (
                   <Badge variant="destructive" className="bg-red-100 text-red-800">
                     Inactive
                   </Badge>
                 )}
               </div>
             </div>
            <CardContent className="p-4">
              <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2" data-testid={`product-name-${product.id}`}>
                {product.name}
              </h3>
              <p className="text-sm text-gray-600 mb-3 line-clamp-2" data-testid={`product-description-${product.id}`}>
                {product.description}
              </p>
              <div className="flex items-center justify-between">
                <div className="text-lg font-bold text-primary" data-testid={`product-price-${product.id}`}>
                  ${(product.inventory?.sellingPrice || product.basePrice || 0).toLocaleString()}
                </div>
                {product.inventory && (
                  <div className="text-sm text-gray-500">
                    Stock: {product.inventory.quantity}
                  </div>
                )}
              </div>
            </CardContent>
            <CardFooter className="p-4 pt-0">
              {getActionButton(product)}
            </CardFooter>
          </Card>
        ))}
      </div>

      {/* Edit Product Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto bg-white border border-gray-200 shadow-xl">
          <DialogHeader className="pb-6">
            <DialogTitle className="text-xl font-semibold text-gray-900">Edit Product</DialogTitle>
            <DialogDescription className="text-gray-600">
              Update your product information. All changes will be saved immediately.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6">
            {/* Product Name */}
            <div className="space-y-2">
              <Label htmlFor="edit-name" className="text-sm font-medium">
                Product Name *
              </Label>
              <Input
                id="edit-name"
                value={editForm.name}
                onChange={(e) => setEditForm(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Enter product name"
                className="w-full"
              />
            </div>

            {/* SKU and Category - Side by side on desktop */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-sku" className="text-sm font-medium">
                  SKU *
                </Label>
                <Input
                  id="edit-sku"
                  value={editForm.sku}
                  onChange={(e) => setEditForm(prev => ({ ...prev, sku: e.target.value }))}
                  placeholder="Enter SKU"
                  className="w-full"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-category" className="text-sm font-medium">
                  Category
                </Label>
                <Select value={editForm.categoryId} onValueChange={(value) => setEditForm(prev => ({ ...prev, categoryId: value }))}>
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent className="bg-white border border-gray-200 shadow-lg">
                    {categories.map((category: any) => (
                      <SelectItem key={category.id} value={category.id} className="hover:bg-gray-50">
                        {category.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Description */}
            <div className="space-y-2">
              <Label htmlFor="edit-description" className="text-sm font-medium">
                Description
              </Label>
              <Textarea
                id="edit-description"
                value={editForm.description}
                onChange={(e) => setEditForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Enter product description"
                className="w-full min-h-[100px]"
              />
            </div>

            {/* Price and Image - Side by side on desktop */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-price" className="text-sm font-medium">
                  Base Price *
                </Label>
                <Input
                  id="edit-price"
                  type="number"
                  step="0.01"
                  min="0"
                  value={editForm.basePrice}
                  onChange={(e) => setEditForm(prev => ({ ...prev, basePrice: e.target.value }))}
                  placeholder="0.00"
                  className="w-full"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-image" className="text-sm font-medium">
                  Image URL
                </Label>
                <Input
                  id="edit-image"
                  type="url"
                  value={editForm.imageUrl}
                  onChange={(e) => setEditForm(prev => ({ ...prev, imageUrl: e.target.value }))}
                  placeholder="https://example.com/image.jpg"
                  className="w-full"
                />
              </div>
            </div>

            {/* Active Status */}
            <div className="space-y-2">
              <Label htmlFor="edit-active" className="text-sm font-medium">
                Product Status
              </Label>
              <Select value={editForm.isActive ? "active" : "inactive"} onValueChange={(value) => setEditForm(prev => ({ ...prev, isActive: value === "active" }))}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent className="bg-white border border-gray-200 shadow-lg">
                  <SelectItem value="active" className="hover:bg-gray-50">
                    Active
                  </SelectItem>
                  <SelectItem value="inactive" className="hover:bg-gray-50">
                    Inactive
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="flex justify-between gap-3 pt-6 border-t">
            <Button 
              variant="destructive" 
              onClick={handleDeleteProduct}
              disabled={deleteProductMutation.isPending}
              className="px-6 py-2"
            >
              {deleteProductMutation.isPending ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </>
              )}
            </Button>
            <div className="flex gap-3">
              <Button 
                variant="outline" 
                onClick={() => setIsEditDialogOpen(false)}
                className="px-6 py-2"
              >
                Cancel
              </Button>
              <Button 
                onClick={handleUpdateProduct}
                disabled={updateProductMutation.isPending}
                className="px-6 py-2"
              >
                {updateProductMutation.isPending ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                    Updating...
                  </>
                ) : (
                  "Update Product"
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}