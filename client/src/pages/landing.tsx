import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Building2, ShoppingCart, Factory, Shield, MessageCircle, FileText, BarChart3, Users } from "lucide-react";

export default function Landing() {
  const features = [
    {
      icon: ShoppingCart,
      title: "Smart Ordering",
      description: "Place orders instantly from nearby distributors with real-time inventory"
    },
    {
      icon: MessageCircle,
      title: "WhatsApp Integration",
      description: "Get instant notifications and invoices directly on WhatsApp"
    },
    {
      icon: FileText,
      title: "Auto Invoicing",
      description: "PDF invoices generated and delivered automatically"
    },
    {
      icon: BarChart3,
      title: "Analytics & Reports",
      description: "Comprehensive reporting for all user roles"
    },
    {
      icon: Users,
      title: "Multi-Role Platform",
      description: "Designed for retailers, distributors, manufacturers, and admins"
    },
    {
      icon: Shield,
      title: "Secure & Reliable",
      description: "Built with security and reliability at its core"
    }
  ];

  const roles = [
    {
      icon: Building2,
      title: "Retailers",
      description: "Browse products, place orders, track deliveries, and download reports",
      examples: ["Mattress stores", "Clothing shops", "Electronics retailers", "Grocery stores"]
    },
    {
      icon: Factory,
      title: "Distributors",
      description: "Manage inventory, process orders, and connect with retailers",
      examples: ["Wholesale suppliers", "Regional distributors", "Local stockists"]
    },
    {
      icon: Shield,
      title: "Manufacturers",
      description: "Upload products, track distribution, and analyze market performance",
      examples: ["Brand owners", "Factory owners", "Product manufacturers"]
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-primary">AuroMart</h1>
            </div>
            <div className="flex gap-2">
              <Button 
                onClick={() => window.location.href = '/api/login'}
                className="action-button-primary"
                data-testid="button-login"
              >
                Sign In
              </Button>
              <Button 
                onClick={() => window.location.href = '/register'}
                variant="outline"
                data-testid="button-register"
              >
                Sign Up
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Smart B2B Ordering &<br />
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              Billing Platform
            </span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Connect retailers, distributors, and manufacturers with WhatsApp integration, 
            auto invoicing, and complete workflow management built for India's market.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg"
              onClick={() => window.location.href = '/api/login'}
              className="action-button-primary text-lg px-8 py-3"
              data-testid="button-start-ordering"
            >
              Start Ordering
            </Button>
            <Button 
              size="lg"
              variant="outline"
              className="text-lg px-8 py-3"
              data-testid="button-learn-more"
            >
              Learn More
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Everything You Need for B2B Commerce
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              From order placement to invoice delivery, AuroMart handles your complete B2B workflow
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="text-center hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-xl" data-testid={`text-feature-title-${index}`}>
                    {feature.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600" data-testid={`text-feature-description-${index}`}>
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Roles Section */}
      <section className="py-20 bg-gray-50 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Built for Every Role in Your Supply Chain
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Whether you're a retailer, distributor, or manufacturer, AuroMart has tools designed for your needs
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {roles.map((role, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="w-12 h-12 bg-secondary/10 rounded-lg flex items-center justify-center mb-4">
                    <role.icon className="h-6 w-6 text-secondary" />
                  </div>
                  <CardTitle className="text-xl" data-testid={`text-role-title-${index}`}>
                    {role.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-600 mb-4" data-testid={`text-role-description-${index}`}>
                    {role.description}
                  </p>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-gray-700">Perfect for:</p>
                    <ul className="text-sm text-gray-600 space-y-1">
                      {role.examples.map((example, exampleIndex) => (
                        <li key={exampleIndex} className="flex items-center">
                          <div className="w-1.5 h-1.5 bg-secondary rounded-full mr-2"></div>
                          {example}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* WhatsApp Integration Highlight */}
      <section className="py-20 bg-white px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gradient-to-r from-secondary/10 to-primary/10 rounded-2xl p-8 md:p-12 text-center">
            <div className="w-16 h-16 bg-secondary rounded-2xl flex items-center justify-center mx-auto mb-6">
              <MessageCircle className="h-8 w-8 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              WhatsApp-First Experience
            </h2>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              Get order confirmations, delivery updates, and invoices directly on WhatsApp. 
              Built for how Indian businesses actually communicate.
            </p>
            <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-600">
              <div className="flex items-center">
                <div className="w-2 h-2 bg-secondary rounded-full mr-2"></div>
                Instant order alerts
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-secondary rounded-full mr-2"></div>
                PDF invoice delivery
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-secondary rounded-full mr-2"></div>
                Real-time status updates
              </div>
              <div className="flex items-center">
                <div className="w-2 h-2 bg-secondary rounded-full mr-2"></div>
                Monthly report summaries
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gray-900 text-white px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Transform Your B2B Operations?
          </h2>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Join thousands of businesses already using AuroMart to streamline their ordering and billing processes.
          </p>
          <Button 
            size="lg"
            onClick={() => window.location.href = '/api/login'}
            className="action-button-primary text-lg px-8 py-3"
            data-testid="button-get-started"
          >
            Get Started Today
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h3 className="text-2xl font-bold text-primary mb-4">AuroMart</h3>
          <p className="text-gray-600 mb-8">
            Smart B2B ordering and billing platform built for India's hyper-local market
          </p>
          <div className="text-sm text-gray-500">
            © 2024 AuroMart. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
