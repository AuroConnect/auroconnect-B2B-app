import { useAuth } from "@/hooks/useAuth";
import { useQuery } from "@tanstack/react-query";
import Header from "@/components/layout/header";
import MobileNav from "@/components/layout/mobile-nav";
import StatsCards from "@/components/dashboard/stats-cards";
import RecentOrders from "@/components/dashboard/recent-orders";
import QuickActions from "@/components/dashboard/quick-actions";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageCircle, TrendingUp, Users, Package } from "lucide-react";
import { useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import type { User } from "@/hooks/useAuth";

export default function Dashboard() {
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
        window.location.href = "/";
      }, 500);
      return;
    }
  }, [user, isLoading, toast]);

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ["api", "analytics", "stats"],
    enabled: !!user,
  });

  const { data: notifications } = useQuery({
    queryKey: ["api", "notifications"],
    enabled: !!user,
  });

  if (isLoading || !user) {
    return (
      <div className="min-h-screen auromart-gradient-bg flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-white border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome Message */}
        <div className="mb-8">
          <div className="flex items-center mb-4">
            <div className="w-12 h-12 auromart-gradient-primary rounded-2xl flex items-center justify-center mr-4">
              <Users className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900" data-testid="text-welcome">
                Welcome back, {(user as User)?.firstName || (user as User)?.businessName}!
              </h1>
              <p className="text-gray-600" data-testid="text-role">
                {(user as User)?.role?.charAt(0).toUpperCase() + (user as User)?.role?.slice(1)} Dashboard
              </p>
            </div>
          </div>
        </div>

        {/* Stats Cards */}
        <StatsCards stats={stats} isLoading={statsLoading} userRole={(user as User)?.role || 'retailer'} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
          {/* Recent Orders */}
          <div className="lg:col-span-2">
            <RecentOrders />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <QuickActions userRole={(user as User)?.role || 'retailer'} />

            {/* WhatsApp Notifications */}
            <Card className="dashboard-card whatsapp-section">
              <CardHeader className="pb-4">
                <CardTitle className="flex items-center whatsapp-header">
                  <div className="w-8 h-8 whatsapp-icon rounded-lg flex items-center justify-center mr-3">
                    <MessageCircle className="h-4 w-4 text-white" />
                  </div>
                  WhatsApp Updates
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {notifications && Array.isArray(notifications) && notifications.length > 0 ? (
                    notifications.slice(0, 3).map((notification: any, index: number) => (
                      <div key={notification.id} className="flex items-start space-x-3 p-3 whatsapp-notification rounded-lg">
                        <div className="w-2 h-2 whatsapp-dot rounded-full mt-2"></div>
                        <div>
                          <p className="text-sm text-gray-900 font-medium" data-testid={`text-notification-${index}`}>
                            {notification.message}
                          </p>
                          <p className="text-xs text-gray-600">
                            {new Date(notification.createdAt).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <div className="w-12 h-12 whatsapp-icon rounded-2xl flex items-center justify-center mx-auto mb-3">
                        <MessageCircle className="h-6 w-6 text-white" />
                      </div>
                      <p className="text-sm whatsapp-empty">No recent notifications</p>
                      <p className="text-xs whatsapp-empty-subtitle mt-1">WhatsApp updates will appear here</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Performance Insights */}
            <Card className="dashboard-card">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <div className="w-8 h-8 auromart-gradient-accent rounded-lg flex items-center justify-center mr-3">
                    <TrendingUp className="h-4 w-4 text-white" />
                  </div>
                  Performance Insights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Order Success Rate</span>
                    <span className="text-lg font-semibold text-green-600">98.5%</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Avg Response Time</span>
                    <span className="text-lg font-semibold text-blue-600">2.3h</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Customer Satisfaction</span>
                    <span className="text-lg font-semibold text-purple-600">4.8/5</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
      
      <MobileNav />
    </div>
  );
}
