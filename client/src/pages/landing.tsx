import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Building2, ShoppingCart, Factory, Shield, MessageCircle, FileText, BarChart3, Users, Sparkles, Zap, TrendingUp, Bell, Truck } from "lucide-react";
import LoginForm from "@/components/auth/login-form";
import { Play } from "lucide-react";

export default function Landing() {
  const [showLogin, setShowLogin] = useState(false);

  const features = [
    {
      icon: ShoppingCart,
      title: "Smart Ordering",
      description: "Place orders instantly from nearby distributors with real-time inventory",
      gradient: "from-purple-500 to-pink-500"
    },
    {
      icon: MessageCircle,
      title: "WhatsApp Integration",
      description: "Get instant notifications and invoices directly on WhatsApp",
      gradient: "from-green-500 to-emerald-500"
    },
    {
      icon: FileText,
      title: "Auto Invoicing",
      description: "PDF invoices generated and delivered automatically",
      gradient: "from-blue-500 to-cyan-500"
    },
    {
      icon: BarChart3,
      title: "Analytics & Reports",
      description: "Comprehensive reporting for all user roles",
      gradient: "from-orange-500 to-red-500"
    },
    {
      icon: Users,
      title: "Multi-Role Platform",
      description: "Designed for retailers, distributors, manufacturers, and admins",
      gradient: "from-indigo-500 to-purple-500"
    },
    {
      icon: Shield,
      title: "Secure & Reliable",
      description: "Built with security and reliability at its core",
      gradient: "from-teal-500 to-green-500"
    }
  ];

  const roles = [
    {
      icon: Building2,
      title: "Retailers",
      description: "Browse products, place orders, track deliveries, and download reports",
      examples: ["Mattress stores", "Clothing shops", "Electronics retailers", "Grocery stores"],
      gradient: "from-purple-500 to-pink-500"
    },
    {
      icon: Factory,
      title: "Distributors",
      description: "Manage inventory, process orders, and connect with retailers",
      examples: ["Wholesale suppliers", "Regional distributors", "Local stockists"],
      gradient: "from-green-500 to-emerald-500"
    },
    {
      icon: Shield,
      title: "Manufacturers",
      description: "Upload products, track distribution, and analyze market performance",
      examples: ["Brand owners", "Factory owners", "Product manufacturers"],
      gradient: "from-blue-500 to-cyan-500"
    }
  ];

  if (showLogin) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-green-50 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <LoginForm />
          <div className="text-center mt-6">
            <Button 
              variant="link" 
              onClick={() => setShowLogin(false)}
              className="text-gray-700 hover:text-gray-900 font-medium"
            >
              ← Back to Home
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-green-50">
      {/* Header */}
      <header className="glass-card sticky top-0 z-50 border-b border-gray-200/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="w-8 h-8 auromart-gradient-primary rounded-lg flex items-center justify-center mr-3">
                <Sparkles className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gray-900">AuroMart</span>
            </div>
            <div className="flex gap-3">
              <Button 
                onClick={() => setShowLogin(true)}
                className="glass-button text-gray-700 border-gray-300 hover:bg-white/80"
                data-testid="button-login"
              >
                Sign In
              </Button>
              <Button 
                onClick={() => window.location.href = '/register'}
                className="auromart-gradient-primary text-white hover:scale-105 transition-transform"
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
          <div className="float-animation mb-8">
            <div className="w-20 h-20 auromart-gradient-primary rounded-3xl flex items-center justify-center mx-auto mb-6">
              <Zap className="h-10 w-10 text-white" />
            </div>
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            Smart B2B Ordering &<br />
            <span className="bg-gradient-to-r from-purple-600 to-green-600 bg-clip-text text-transparent">
              Billing Platform
            </span>
          </h1>
          <p className="text-xl text-gray-700 mb-8 max-w-3xl mx-auto">
            Connect retailers, distributors, and manufacturers with WhatsApp integration, 
            auto invoicing, and complete workflow management built for India's market.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              onClick={() => window.location.href = '/register'}
              className="auromart-gradient-primary text-white text-lg px-8 py-4 hover:scale-105 transition-transform"
              data-testid="button-get-started"
            >
              <Sparkles className="h-5 w-5 mr-2" />
              Get Started
            </Button>
            <Button 
              size="lg" 
              className="glass-button text-gray-700 text-lg px-8 py-4 border-gray-300 hover:bg-white/80"
              onClick={() => setShowLogin(true)}
              data-testid="button-demo"
            >
              Try Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Roles Section - Professional Design */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-slate-50 to-blue-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Users className="h-8 w-8 text-white" />
            </div>
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Built for Every Role in Your Supply Chain
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Whether you're a retailer, distributor, or manufacturer, AuroMart has tools designed for your needs
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {roles.map((role, index) => (
              <div key={index} className="group relative">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl blur-xl opacity-20 group-hover:opacity-30 transition-opacity"></div>
                <Card className="relative bg-white border-0 shadow-xl hover:shadow-2xl transition-all duration-300 hover:-translate-y-2">
                  <CardHeader className="text-center pb-6">
                    <div className={`w-20 h-20 bg-gradient-to-r ${role.gradient} rounded-2xl flex items-center justify-center mx-auto mb-6 group-hover:scale-110 transition-transform shadow-lg`}>
                      <role.icon className="h-10 w-10 text-white" />
                    </div>
                    <CardTitle className="text-2xl font-bold text-gray-900 mb-2" data-testid={`text-role-title-${index}`}>
                      {role.title}
                    </CardTitle>
                    <p className="text-gray-600 text-lg leading-relaxed" data-testid={`text-role-description-${index}`}>
                      {role.description}
                    </p>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="space-y-3">
                      <p className="text-sm font-semibold text-gray-800 uppercase tracking-wide">Perfect for:</p>
                      <ul className="space-y-2">
                        {role.examples.map((example, exampleIndex) => (
                          <li key={exampleIndex} className="flex items-center text-gray-700">
                            <div className="w-2 h-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full mr-3"></div>
                            <span className="font-medium">{example}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section - Professional Design */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <div className="w-16 h-16 bg-gradient-to-r from-green-600 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <Sparkles className="h-8 w-8 text-white" />
            </div>
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything You Need for B2B Commerce
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From order placement to invoice delivery, AuroMart handles your complete B2B workflow
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="group relative">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl blur-lg opacity-10 group-hover:opacity-20 transition-opacity"></div>
                <Card className="relative bg-white border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                  <CardHeader className="text-center pb-4">
                    <div className={`w-16 h-16 bg-gradient-to-r ${feature.gradient} rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform shadow-md`}>
                      <feature.icon className="h-8 w-8 text-white" />
                    </div>
                    <CardTitle className="text-xl font-bold text-gray-900" data-testid={`text-feature-title-${index}`}>
                      {feature.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 text-center leading-relaxed" data-testid={`text-feature-description-${index}`}>
                      {feature.description}
                    </p>
                  </CardContent>
                </Card>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* WhatsApp Integration Highlight - Professional Design */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="max-w-7xl mx-auto text-center">
          <div className="float-animation mb-8">
            <div className="w-20 h-20 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl">
              <MessageCircle className="h-10 w-10 text-white" />
            </div>
          </div>
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            WhatsApp-First Experience
          </h2>
          <p className="text-xl text-gray-600 mb-10 max-w-3xl mx-auto leading-relaxed">
            Get order confirmations, delivery updates, and invoices directly on WhatsApp.
            Built for how Indian businesses actually communicate.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mx-auto">
            <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
              <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Bell className="h-6 w-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Instant Alerts</h3>
              <p className="text-sm text-gray-600">Real-time order notifications</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
              <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-green-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <FileText className="h-6 w-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">PDF Invoices</h3>
              <p className="text-sm text-gray-600">Digital invoice delivery</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Truck className="h-6 w-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Live Tracking</h3>
              <p className="text-sm text-gray-600">Real-time delivery updates</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
              <div className="w-12 h-12 bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Monthly Reports</h3>
              <p className="text-sm text-gray-600">Performance summaries</p>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action - Professional Design */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-gray-900 to-slate-800">
        <div className="max-w-4xl mx-auto text-center">
          <div className="float-animation mb-8">
            <div className="w-20 h-20 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-xl">
              <TrendingUp className="h-10 w-10 text-white" />
            </div>
          </div>
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Transform Your B2B Operations?
          </h2>
          <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto leading-relaxed">
            Join thousands of businesses already using AuroMart to streamline their ordering and billing processes.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button 
              size="lg" 
              className="action-button-primary text-lg px-8 py-4 h-auto"
              onClick={() => window.location.href = '/register'}
            >
              <Sparkles className="h-5 w-5 mr-2" />
              Get Started Today
            </Button>
            <Button 
              variant="outline" 
              size="lg" 
              className="text-lg px-8 py-4 h-auto border-white/20 text-white hover:bg-white/10"
              onClick={() => window.location.href = '/'}
            >
              <Play className="h-5 w-5 mr-2" />
              Watch Demo
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="glass-card border-t border-gray-200/50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <div className="w-16 h-16 auromart-gradient-primary rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Sparkles className="h-8 w-8 text-white" />
          </div>
          <h3 className="text-2xl font-bold text-gray-900 mb-4">AuroMart</h3>
          <p className="text-gray-700 mb-8">
            Smart B2B ordering and billing platform built for India's hyper-local market
          </p>
          <div className="text-sm text-gray-600">
            © 2024 AuroMart. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  );
}
