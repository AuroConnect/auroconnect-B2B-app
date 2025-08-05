import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ShoppingCart, Eye, Package } from "lucide-react";

interface ProductGridProps {
  products: any[];
  isLoading: boolean;
  userRole: string;
}

export default function ProductGrid({ products, isLoading, userRole }: ProductGridProps) {
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

  const handleAddToCart = (product: any) => {
    // In a real app, this would add to cart
    alert(`Added ${product.name} to cart!`);
  };

  const getActionButton = (product: any) => {
    switch (userRole) {
      case 'retailer':
        return (
          <Button 
            className="w-full" 
            onClick={() => handleAddToCart(product)}
            data-testid={`button-add-to-cart-${product.id}`}
          >
            <ShoppingCart className="h-4 w-4 mr-2" />
            Add to Cart
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
          <Button 
            variant="outline" 
            className="w-full"
            data-testid={`button-edit-product-${product.id}`}
          >
            <Eye className="h-4 w-4 mr-2" />
            Edit Product
          </Button>
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
            <div className="absolute top-2 right-2">
              <Badge variant="secondary" className="bg-white/90 text-gray-700">
                {product.sku}
              </Badge>
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
  );
}