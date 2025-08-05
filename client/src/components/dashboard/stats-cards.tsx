import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface StatsCardsProps {
  stats: any;
  isLoading: boolean;
  userRole: string;
}

export default function StatsCards({ stats, isLoading, userRole }: StatsCardsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader className="animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            </CardHeader>
            <CardContent className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-2/3"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const getStatsForRole = () => {
    const baseStats = [
      {
        title: "Total Orders",
        value: stats?.totalOrders || 0,
        change: "+12%",
        trend: "up" as const,
        description: "from last month"
      },
      {
        title: "Revenue",
        value: `$${(stats?.totalRevenue || 0).toLocaleString()}`,
        change: "+8%",
        trend: "up" as const,
        description: "from last month"
      }
    ];

    switch (userRole) {
      case 'retailer':
        return [
          ...baseStats,
          {
            title: "Pending Orders",
            value: stats?.pendingOrders || 0,
            change: "0%",
            trend: "neutral" as const,
            description: "awaiting fulfillment"
          },
          {
            title: "Suppliers",
            value: stats?.activeSuppliers || 5,
            change: "+2",
            trend: "up" as const,
            description: "active partnerships"
          }
        ];
      case 'distributor':
        return [
          ...baseStats,
          {
            title: "Inventory Items",
            value: stats?.inventoryCount || 0,
            change: "+15%",
            trend: "up" as const,
            description: "from last month"
          },
          {
            title: "Active Retailers",
            value: stats?.activeRetailers || 8,
            change: "+3",
            trend: "up" as const,
            description: "new connections"
          }
        ];
      case 'manufacturer':
        return [
          ...baseStats,
          {
            title: "Products",
            value: stats?.productsCount || 0,
            change: "+5%",
            trend: "up" as const,
            description: "total catalog"
          },
          {
            title: "Production Volume",
            value: `${(stats?.productionVolume || 1250).toLocaleString()} units`,
            change: "+18%",
            trend: "up" as const,
            description: "this month"
          }
        ];
      default:
        return baseStats;
    }
  };

  const statsData = getStatsForRole();

  const getTrendIcon = (trend: "up" | "down" | "neutral") => {
    switch (trend) {
      case "up":
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case "down":
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  const getTrendColor = (trend: "up" | "down" | "neutral") => {
    switch (trend) {
      case "up":
        return "text-green-600";
      case "down":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {statsData.map((stat, index) => (
        <Card key={index} data-testid={`stat-card-${index}`}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-gray-600">
              {stat.title}
            </CardTitle>
            {getTrendIcon(stat.trend)}
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-900" data-testid={`stat-value-${index}`}>
              {stat.value}
            </div>
            <div className="flex items-center space-x-1 text-xs">
              <span className={getTrendColor(stat.trend)}>
                {stat.change}
              </span>
              <span className="text-gray-500">{stat.description}</span>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}