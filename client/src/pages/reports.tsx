import { useQuery } from "@tanstack/react-query";
import { useAuth } from "@/hooks/useAuth";
import Header from "@/components/layout/header";
import MobileNav from "@/components/layout/mobile-nav";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FileText, Download, Calendar, BarChart3, TrendingUp, Package } from "lucide-react";
import { useEffect } from "react";
import { useToast } from "@/hooks/use-toast";

export default function Reports() {
  const { user, isLoading } = useAuth();
  const { toast } = useToast();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !user) {
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
  }, [user, isLoading, toast]);

  const { data: stats } = useQuery({
    queryKey: ["/api/analytics/stats"],
    enabled: !!user,
  });

  const reportTypes = [
    {
      title: "Monthly Order Report",
      description: "Complete summary of orders for the current month",
      icon: Calendar,
      type: "monthly",
      available: true
    },
    {
      title: "Product Performance",
      description: "Analysis of top-selling products and categories",
      icon: BarChart3,
      type: "products",
      available: true
    },
    {
      title: "Financial Summary",
      description: "Revenue and expense breakdown",
      icon: TrendingUp,
      type: "financial",
      available: true
    },
    {
      title: "Inventory Report",
      description: "Stock levels and inventory management",
      icon: Package,
      type: "inventory",
      available: user?.role === 'distributor'
    }
  ];

  if (isLoading || !user) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading reports...</p>
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
            Reports & Analytics
          </h1>
          <p className="text-gray-600 mt-1">
            Download detailed reports and view business analytics
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <Card className="stat-card">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                  <Package className="h-5 w-5 text-primary" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Orders</p>
                  <p className="text-2xl font-semibold text-gray-900" data-testid="text-total-orders">
                    {stats?.totalOrders || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="stat-card">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-secondary/10 rounded-lg flex items-center justify-center">
                  <TrendingUp className="h-5 w-5 text-secondary" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Monthly Revenue</p>
                  <p className="text-2xl font-semibold text-gray-900" data-testid="text-monthly-revenue">
                    ₹{stats?.monthlySpend || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="stat-card">
            <CardContent className="p-6">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-accent/10 rounded-lg flex items-center justify-center">
                  <BarChart3 className="h-5 w-5 text-accent" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Pending Orders</p>
                  <p className="text-2xl font-semibold text-gray-900" data-testid="text-pending-orders">
                    {stats?.pendingOrders || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Available Reports */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="flex items-center">
              <FileText className="h-5 w-5 mr-2" />
              Available Reports
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {reportTypes.filter(report => report.available).map((report, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
                        <report.icon className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900" data-testid={`text-report-title-${index}`}>
                          {report.title}
                        </h3>
                        <p className="text-sm text-gray-600 mt-1" data-testid={`text-report-description-${index}`}>
                          {report.description}
                        </p>
                        <Badge variant="secondary" className="mt-2">
                          Ready to download
                        </Badge>
                      </div>
                    </div>
                    <Button size="sm" className="action-button-primary" data-testid={`button-download-${report.type}`}>
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Reports */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Reports</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                {
                  name: "January 2024 - Monthly Report",
                  date: "2024-02-01",
                  size: "2.3 MB",
                  type: "PDF"
                },
                {
                  name: "Q4 2023 - Financial Summary", 
                  date: "2024-01-15",
                  size: "1.8 MB",
                  type: "PDF"
                },
                {
                  name: "December 2023 - Product Performance",
                  date: "2023-12-31",
                  size: "3.1 MB",
                  type: "PDF"
                }
              ].map((report, index) => (
                <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                      <FileText className="h-4 w-4 text-red-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900" data-testid={`text-recent-report-name-${index}`}>
                        {report.name}
                      </p>
                      <p className="text-sm text-gray-600">
                        {new Date(report.date).toLocaleDateString()} • {report.size} • {report.type}
                      </p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" data-testid={`button-download-recent-${index}`}>
                    <Download className="h-4 w-4 mr-1" />
                    Download
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <MobileNav />
    </div>
  );
}
