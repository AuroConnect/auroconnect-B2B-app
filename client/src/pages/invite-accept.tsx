import { useState, useEffect } from "react";
import { useParams, useLocation } from "wouter";
import { useToast } from "@/hooks/use-toast";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Check, X, Building2, Package, Users, ArrowLeft } from "lucide-react";

interface InviteDetails {
  id: string;
  token: string;
  inviter: {
    id: string;
    businessName: string;
    email: string;
    role: string;
  };
  inviteeEmail: string;
  inviteeRole: string;
  message?: string;
  status: string;
  expiresAt: string;
}

export default function InviteAccept() {
  const { token } = useParams();
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const [inviteDetails, setInviteDetails] = useState<InviteDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [accepting, setAccepting] = useState(false);
  const [declining, setDeclining] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      fetchInviteDetails();
    }
  }, [token]);

  const fetchInviteDetails = async () => {
    try {
      const response = await fetch(`http://localhost:5000/api/partnerships/invite/${token}`);
      
      if (response.ok) {
        const data = await response.json();
        setInviteDetails(data);
      } else {
        const errorData = await response.json();
        setError(errorData.message || "Invalid or expired invitation");
      }
    } catch (err) {
      setError("Failed to load invitation details");
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async () => {
    if (!token) return;
    
    setAccepting(true);
    try {
      const response = await fetch(`http://localhost:5000/api/partnerships/invite/${token}/accept`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const result = await response.json();
        toast({
          title: "Partnership Accepted!",
          description: "You are now connected with " + inviteDetails?.inviter.businessName,
        });
        
        // Redirect to partners page after a short delay
        setTimeout(() => {
          setLocation("/partners");
        }, 2000);
      } else {
        const errorData = await response.json();
        toast({
          title: "Error",
          description: errorData.message || "Failed to accept invitation",
          variant: "destructive",
        });
      }
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to accept invitation",
        variant: "destructive",
      });
    } finally {
      setAccepting(false);
    }
  };

  const handleDecline = async () => {
    if (!token) return;
    
    setDeclining(true);
    try {
      const response = await fetch(`http://localhost:5000/api/partnerships/invite/${token}/decline`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        toast({
          title: "Invitation Declined",
          description: "The invitation has been declined",
        });
        
        // Redirect to home page after a short delay
        setTimeout(() => {
          setLocation("/");
        }, 2000);
      } else {
        const errorData = await response.json();
        toast({
          title: "Error",
          description: errorData.message || "Failed to decline invitation",
          variant: "destructive",
        });
      }
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to decline invitation",
        variant: "destructive",
      });
    } finally {
      setDeclining(false);
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "manufacturer":
        return <Building2 className="h-5 w-5 text-purple-600" />;
      case "distributor":
        return <Package className="h-5 w-5 text-green-600" />;
      case "retailer":
        return <Users className="h-5 w-5 text-blue-600" />;
      default:
        return <Users className="h-5 w-5 text-gray-600" />;
    }
  };

  const getRoleDescription = (role: string) => {
    switch (role) {
      case "manufacturer":
        return "Product manufacturer that creates and supplies goods";
      case "distributor":
        return "Wholesale supplier that connects manufacturers and retailers";
      case "retailer":
        return "Local business that sells products to customers";
      default:
        return "Business partner";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-green-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-purple-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading invitation details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-green-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <X className="h-8 w-8 text-red-600" />
            </div>
            <CardTitle className="text-red-600">Invalid Invitation</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
          <CardContent className="text-center">
            <Button onClick={() => setLocation("/")} className="w-full">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Go to Home
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!inviteDetails) {
    return null;
  }

  const isExpired = new Date(inviteDetails.expiresAt) < new Date();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-green-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center">
          <div className="w-20 h-20 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
            <Users className="h-10 w-10 text-white" />
          </div>
          <CardTitle className="text-2xl">Partnership Invitation</CardTitle>
          <CardDescription>
            You've been invited to establish a business partnership
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Partner Details */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3 flex items-center">
              {getRoleIcon(inviteDetails.inviter.role)}
              <span className="ml-2">Partner Details</span>
            </h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Business:</span>
                <span className="font-medium">{inviteDetails.inviter.businessName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Role:</span>
                <Badge variant="outline" className="flex items-center">
                  {getRoleIcon(inviteDetails.inviter.role)}
                  <span className="ml-1 capitalize">{inviteDetails.inviter.role}</span>
                </Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Email:</span>
                <span className="font-medium">{inviteDetails.inviter.email}</span>
              </div>
            </div>
            <p className="text-sm text-gray-500 mt-3">
              {getRoleDescription(inviteDetails.inviter.role)}
            </p>
          </div>

          {/* Message */}
          {inviteDetails.message && (
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">Message</h3>
              <p className="text-gray-700 italic">"{inviteDetails.message}"</p>
            </div>
          )}

          {/* Expiry Warning */}
          {isExpired && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="flex items-center">
                <X className="h-5 w-5 text-red-600 mr-2" />
                <span className="text-red-800 font-medium">This invitation has expired</span>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4 pt-4">
            <Button
              onClick={handleAccept}
              disabled={accepting || declining || isExpired}
              className="flex-1 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
            >
              {accepting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                  Accepting...
                </>
              ) : (
                <>
                  <Check className="h-4 w-4 mr-2" />
                  Accept Partnership
                </>
              )}
            </Button>
            
            <Button
              onClick={handleDecline}
              disabled={accepting || declining || isExpired}
              variant="outline"
              className="flex-1"
            >
              {declining ? (
                <>
                  <div className="w-4 h-4 border-2 border-gray-600 border-t-transparent rounded-full animate-spin mr-2" />
                  Declining...
                </>
              ) : (
                <>
                  <X className="h-4 w-4 mr-2" />
                  Decline
                </>
              )}
            </Button>
          </div>

          {/* What happens next */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-2">What happens next?</h3>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>• You'll be able to see each other's products and services</li>
              <li>• Start doing business together on the platform</li>
              <li>• Access to exclusive partner pricing and features</li>
            </ul>
          </div>

          {/* Back to home */}
          <div className="text-center">
                      <Button variant="ghost" onClick={() => setLocation("/")}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Home
          </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
