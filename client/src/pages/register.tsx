import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Link } from "wouter";
import { Building2, User, Package, Factory, ArrowLeft } from "lucide-react";

export default function Register() {
  const { register, isRegisterLoading, registerError } = useAuth();
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    password: "",
    confirmPassword: "",
    role: "" as 'retailer' | 'distributor' | 'manufacturer' | '',
    businessName: "",
    address: "",
    phoneNumber: "",
    whatsappNumber: "",
  });

  const handleInputChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Basic validation
    if (!formData.firstName || !formData.lastName || !formData.email || !formData.password || !formData.role) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields.",
        variant: "destructive",
      });
      return;
    }

    // Validate role is a valid option
    if (!['retailer', 'distributor', 'manufacturer'].includes(formData.role)) {
      toast({
        title: "Validation Error",
        description: "Please select a valid business type.",
        variant: "destructive",
      });
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      toast({
        title: "Validation Error",
        description: "Passwords do not match.",
        variant: "destructive",
      });
      return;
    }

    if (formData.password.length < 6) {
      toast({
        title: "Validation Error",
        description: "Password must be at least 6 characters long.",
        variant: "destructive",
      });
      return;
    }

    // Prepare registration data
    const { confirmPassword, ...registrationData } = formData;
    
    // Ensure role is properly typed
    const finalRegistrationData = {
      ...registrationData,
      role: registrationData.role as 'retailer' | 'distributor' | 'manufacturer'
    };
    
    console.log('Attempting registration with data:', finalRegistrationData);
    
    // Register user
    register(finalRegistrationData, {
      onSuccess: () => {
        console.log('Registration successful');
        toast({
          title: "Registration Successful",
          description: "Your account has been created successfully! Redirecting to login...",
        });
        // Redirect to login after a short delay
        setTimeout(() => {
          window.location.href = "/";
        }, 2000);
      },
      onError: (error: Error) => {
        console.error('Registration error:', error);
        let errorMessage = error.message;
        
        // Provide more specific error messages
        if (error.message.includes('Failed to fetch')) {
          errorMessage = "Unable to connect to server. Please check your internet connection and try again.";
        } else if (error.message.includes('409')) {
          errorMessage = "An account with this email already exists. Please use a different email or try logging in.";
        } else if (error.message.includes('400')) {
          errorMessage = "Please check your information and try again. Make sure all required fields are filled correctly.";
        } else if (error.message.includes('500')) {
          errorMessage = "Server error occurred. Please try again later.";
        }
        
        toast({
          title: "Registration Failed",
          description: errorMessage,
          variant: "destructive",
        });
      },
    });
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "retailer":
        return <User className="h-5 w-5" />;
      case "distributor":
        return <Package className="h-5 w-5" />;
      case "manufacturer":
        return <Factory className="h-5 w-5" />;
      default:
        return <Building2 className="h-5 w-5" />;
    }
  };

  const getRoleDescription = (role: string) => {
    switch (role) {
      case "retailer":
        return "Perfect for shops, stores, and businesses that buy products to sell to customers.";
      case "distributor":
        return "Ideal for wholesalers and distributors who supply products to retailers.";
      case "manufacturer":
        return "Best for companies that produce and supply products to the market.";
      default:
        return "Select your business type to get started.";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        {/* Back Button */}
        <div className="mb-6">
          <Link href="/">
            <Button variant="ghost" size="sm" className="flex items-center gap-2 text-gray-600 hover:text-gray-900">
              <ArrowLeft className="h-4 w-4" />
              Back to Login
            </Button>
          </Link>
        </div>

        <Card className="login-card">
          <CardHeader className="text-center">
            <div className="login-icon">
              <Building2 className="h-8 w-8 text-white" />
            </div>
            <CardTitle className="text-2xl font-bold text-gray-900">Create Your Account</CardTitle>
            <CardDescription className="text-gray-600">
              Join AuroMart to streamline your B2B operations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Personal Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Personal Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="firstName">First Name *</Label>
                    <Input
                      id="firstName"
                      value={formData.firstName}
                      onChange={(e) => handleInputChange("firstName", e.target.value)}
                      placeholder="Enter your first name"
                      data-testid="input-firstName"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName">Last Name *</Label>
                    <Input
                      id="lastName"
                      value={formData.lastName}
                      onChange={(e) => handleInputChange("lastName", e.target.value)}
                      placeholder="Enter your last name"
                      data-testid="input-lastName"
                      required
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email Address *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => handleInputChange("email", e.target.value)}
                    placeholder="Enter your email address"
                    data-testid="input-email"
                    required
                  />
                </div>
              </div>

              {/* Password Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Security</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="password">Password *</Label>
                    <Input
                      id="password"
                      type="password"
                      value={formData.password}
                      onChange={(e) => handleInputChange("password", e.target.value)}
                      placeholder="Enter password (min 6 characters)"
                      data-testid="input-password"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">Confirm Password *</Label>
                    <Input
                      id="confirmPassword"
                      type="password"
                      value={formData.confirmPassword}
                      onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                      placeholder="Confirm your password"
                      data-testid="input-confirmPassword"
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Business Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Business Information</h3>
                <div className="space-y-2">
                  <Label htmlFor="role">Business Type *</Label>
                  <Select value={formData.role} onValueChange={(value) => handleInputChange("role", value)}>
                    <SelectTrigger data-testid="select-role" className="bg-white border-2 border-gray-300 focus:border-primary">
                      <SelectValue placeholder="Select your business type" />
                    </SelectTrigger>
                    <SelectContent className="bg-white border-2 border-gray-200 shadow-lg">
                      <SelectItem value="retailer" className="hover:bg-gray-50">
                        <div className="flex items-center gap-3 p-2">
                          {getRoleIcon("retailer")}
                          <div>
                            <div className="font-semibold text-gray-900">Retailer</div>
                            <div className="text-sm text-gray-600">Buy products to sell to customers</div>
                          </div>
                        </div>
                      </SelectItem>
                      <SelectItem value="distributor" className="hover:bg-gray-50">
                        <div className="flex items-center gap-3 p-2">
                          {getRoleIcon("distributor")}
                          <div>
                            <div className="font-semibold text-gray-900">Distributor</div>
                            <div className="text-sm text-gray-600">Supply products to retailers</div>
                          </div>
                        </div>
                      </SelectItem>
                      <SelectItem value="manufacturer" className="hover:bg-gray-50">
                        <div className="flex items-center gap-3 p-2">
                          {getRoleIcon("manufacturer")}
                          <div>
                            <div className="font-semibold text-gray-900">Manufacturer</div>
                            <div className="text-sm text-gray-600">Produce and supply products</div>
                          </div>
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  {formData.role && (
                    <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-sm text-blue-800 font-medium">
                        {getRoleDescription(formData.role)}
                      </p>
                    </div>
                  )}
                </div>
                <div className="space-y-2">
                  <Label htmlFor="businessName">Business Name</Label>
                  <Input
                    id="businessName"
                    value={formData.businessName}
                    onChange={(e) => handleInputChange("businessName", e.target.value)}
                    placeholder="Enter your business/company name"
                    data-testid="input-businessName"
                  />
                </div>
              </div>

              {/* Contact Information */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Contact Information</h3>
                <div className="space-y-2">
                  <Label htmlFor="address">Business Address</Label>
                  <Textarea
                    id="address"
                    value={formData.address}
                    onChange={(e) => handleInputChange("address", e.target.value)}
                    placeholder="Enter your business address"
                    data-testid="input-address"
                    rows={3}
                  />
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="phoneNumber">Phone Number</Label>
                    <Input
                      id="phoneNumber"
                      value={formData.phoneNumber}
                      onChange={(e) => handleInputChange("phoneNumber", e.target.value)}
                      placeholder="Enter your phone number"
                      data-testid="input-phoneNumber"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="whatsappNumber">WhatsApp Number</Label>
                    <Input
                      id="whatsappNumber"
                      value={formData.whatsappNumber}
                      onChange={(e) => handleInputChange("whatsappNumber", e.target.value)}
                      placeholder="Enter your WhatsApp number"
                      data-testid="input-whatsappNumber"
                    />
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <div className="space-y-4">
                <Button
                  type="submit"
                  className="w-full action-button-primary text-lg py-4 font-semibold shadow-lg hover:shadow-xl transition-all duration-300"
                  disabled={isRegisterLoading}
                  data-testid="button-register"
                >
                  {isRegisterLoading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      Creating Account...
                    </>
                  ) : (
                    "Create Account"
                  )}
                </Button>
                
                <div className="text-center">
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Already have an account?{" "}
                    <Link href="/" className="text-primary hover:underline font-medium">
                      Sign in here
                    </Link>
                  </p>
                </div>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}