import { useState, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { MessageCircle, Bell, Download, CheckCircle, XCircle, Truck, Package } from "lucide-react";
import { getQueryFn } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";

interface WhatsAppNotification {
  id: string;
  message: string;
  type: string;
  sentAt: string;
  isDelivered: boolean;
  createdAt: string;
}

export default function WhatsAppNotifications() {
  const { toast } = useToast();
  const [unreadCount, setUnreadCount] = useState(0);

  const { data: notifications = [], isLoading, refetch } = useQuery<WhatsAppNotification[]>({
    queryKey: ["api", "whatsapp", "notifications"],
    queryFn: getQueryFn({ on401: "throw" }),
  });

  useEffect(() => {
    // Count unread notifications (notifications from last 24 hours)
    const now = new Date();
    const unread = notifications.filter(n => {
      const sentTime = new Date(n.sentAt);
      const hoursDiff = (now.getTime() - sentTime.getTime()) / (1000 * 60 * 60);
      return hoursDiff <= 24;
    }).length;
    setUnreadCount(unread);
  }, [notifications]);

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'order_alert':
        return <Bell className="h-4 w-4 text-blue-600" />;
      case 'status_update':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'delivery_update':
        return <Truck className="h-4 w-4 text-orange-600" />;
      case 'invoice_sent':
        return <Download className="h-4 w-4 text-purple-600" />;
      default:
        return <MessageCircle className="h-4 w-4 text-gray-600" />;
    }
  };

  const getNotificationBadge = (type: string) => {
    switch (type) {
      case 'order_alert':
        return <Badge variant="secondary" className="bg-blue-100 text-blue-800">Order Alert</Badge>;
      case 'status_update':
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Status Update</Badge>;
      case 'delivery_update':
        return <Badge variant="secondary" className="bg-orange-100 text-orange-800">Delivery Update</Badge>;
      case 'invoice_sent':
        return <Badge variant="secondary" className="bg-purple-100 text-purple-800">Invoice</Badge>;
      default:
        return <Badge variant="secondary">Notification</Badge>;
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 1) {
      const diffInMinutes = Math.floor(diffInHours * 60);
      return `${diffInMinutes} minutes ago`;
    } else if (diffInHours < 24) {
      return `${Math.floor(diffInHours)} hours ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  if (isLoading) {
    return (
      <Card className="dashboard-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            WhatsApp Notifications
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <div className="w-8 h-8 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto"></div>
            <p className="text-sm text-gray-600 mt-2">Loading notifications...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="dashboard-card">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            WhatsApp Notifications
            {unreadCount > 0 && (
              <Badge variant="destructive" className="ml-2">
                {unreadCount}
              </Badge>
            )}
          </CardTitle>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => refetch()}
            className="text-xs"
          >
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {notifications.length === 0 ? (
            <div className="text-center py-8">
              <MessageCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No notifications yet</p>
              <p className="text-sm text-gray-500">WhatsApp updates will appear here</p>
            </div>
          ) : (
            notifications.slice(0, 5).map((notification) => (
              <div key={notification.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 mt-1">
                    {getNotificationIcon(notification.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      {getNotificationBadge(notification.type)}
                      <span className="text-xs text-gray-500">
                        {formatTime(notification.sentAt)}
                      </span>
                    </div>
                    <div className="text-sm text-gray-900 whitespace-pre-line">
                      {notification.message}
                    </div>
                    <div className="flex items-center gap-2 mt-2">
                      {notification.isDelivered && (
                        <div className="flex items-center gap-1 text-xs text-green-600">
                          <CheckCircle className="h-3 w-3" />
                          Delivered
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
          
          {notifications.length > 5 && (
            <div className="text-center pt-4">
              <Button variant="outline" size="sm">
                View All Notifications
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
} 