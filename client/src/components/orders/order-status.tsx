import { CheckCircle, Clock, Package, Truck, XCircle, AlertCircle, MapPin, UserCheck, FileText } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface OrderStatusProps {
  status: string;
  statusHistory?: Array<{
    status: string;
    timestamp: string;
    notes?: string;
    updatedBy?: string;
  }>;
  showHistory?: boolean;
}

type OrderStatus = 'pending' | 'confirmed' | 'accepted' | 'processing' | 'packed' | 'shipped' | 'out_for_delivery' | 'delivered' | 'cancelled' | 'rejected';
type StepStatus = 'completed' | 'current' | 'failed' | 'pending';

export default function OrderStatus({ status, statusHistory = [], showHistory = false }: OrderStatusProps) {
  const statusSteps = [
    { key: 'pending', label: 'Order Placed', icon: Clock, description: 'Order has been submitted' },
    { key: 'confirmed', label: 'Order Confirmed', icon: UserCheck, description: 'Order has been confirmed' },
    { key: 'accepted', label: 'Order Accepted', icon: CheckCircle, description: 'Order has been accepted' },
    { key: 'processing', label: 'Processing', icon: AlertCircle, description: 'Order is being processed' },
    { key: 'packed', label: 'Packed', icon: Package, description: 'Items have been packed' },
    { key: 'shipped', label: 'Shipped', icon: Truck, description: 'Order has been shipped' },
    { key: 'out_for_delivery', label: 'Out for Delivery', icon: MapPin, description: 'Order is out for delivery' },
    { key: 'delivered', label: 'Delivered', icon: CheckCircle, description: 'Order has been delivered' },
  ];

  // Handle special statuses
  const orderStatus = status as OrderStatus;
  const isRejected = orderStatus === 'rejected';
  const isCancelled = orderStatus === 'cancelled';
  const isCompleted = orderStatus === 'delivered';
  const isFailed = isRejected || isCancelled;

  // Filter steps based on current status and flow
  let activeSteps = statusSteps;
  
  // For cancelled/rejected orders, only show initial steps
  if (isFailed) {
    activeSteps = statusSteps.slice(0, 3); // Show pending, confirmed, and accepted
  }

  const currentStepIndex = activeSteps.findIndex(step => step.key === orderStatus);
  const normalizedStatus = orderStatus === 'accepted' ? 'confirmed' : orderStatus;
  const normalizedCurrentIndex = activeSteps.findIndex(step => 
    step.key === normalizedStatus || (orderStatus === 'accepted' && step.key === 'confirmed')
  );

  const getStepStatus = (index: number): StepStatus => {
    // Handle failed orders differently
    if (isFailed) {
      if (index === 0) return 'completed'; // Pending always completed
      if (index === 1) return 'completed'; // Confirmed always completed for failed orders
      if (index === 2) {
        // If order was accepted before being cancelled/rejected
        if (orderStatus === 'cancelled' || orderStatus === 'rejected') {
          return 'failed';
        }
      }
      return 'failed';
    }

    // Normal flow logic
    if (index < normalizedCurrentIndex) return 'completed';
    if (index === normalizedCurrentIndex) return 'current';
    return 'pending';
  };

  const getStepColor = (stepStatus: StepStatus) => {
    switch (stepStatus) {
      case 'completed':
        return 'bg-green-500 text-white';
      case 'current':
        return isFailed ? 'bg-red-500 text-white' : 'bg-blue-500 text-white';
      case 'failed':
        return 'bg-red-200 text-red-600';
      case 'pending':
      default:
        return 'bg-gray-300 text-gray-600';
    }
  };

  const getStepIcon = (step: any, stepStatus: StepStatus) => {
    if (stepStatus === 'failed' || (isFailed && stepStatus === 'current')) {
      return <XCircle className="h-4 w-4" />;
    }
    if (stepStatus === 'completed') {
      return <CheckCircle className="h-4 w-4" />;
    }
    if (stepStatus === 'current') {
      return <step.icon className="h-4 w-4" />;
    }
    return <Clock className="h-4 w-4" />;
  };

  const getStepDescription = (step: any, stepStatus: StepStatus) => {
    if (isFailed && stepStatus === 'current') {
      return isRejected ? 'Order Rejected' : 'Order Cancelled';
    }
    if (stepStatus === 'current') return 'In Progress';
    if (stepStatus === 'completed') return 'Completed';
    if (stepStatus === 'failed') return 'Not Completed';
    return 'Pending';
  };

  const isStepFailed = (stepStatus: StepStatus) => {
    return stepStatus === 'failed' || (isFailed && stepStatus === 'current');
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'confirmed': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'accepted': return 'bg-green-100 text-green-800 border-green-200';
      case 'processing': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'packed': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'shipped': return 'bg-indigo-100 text-indigo-800 border-indigo-200';
      case 'out_for_delivery': return 'bg-pink-100 text-pink-800 border-pink-200';
      case 'delivered': return 'bg-emerald-100 text-emerald-800 border-emerald-200';
      case 'cancelled': return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'rejected': return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      return new Date(timestamp).toLocaleString('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return timestamp;
    }
  };

  return (
    <div className="space-y-6">
      {/* Current Status Badge */}
      <div className="flex items-center gap-3">
        <Badge className={`${getStatusBadgeColor(orderStatus)} font-medium`}>
          {orderStatus.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
        </Badge>
        <span className="text-sm text-gray-500">
          Last updated: {statusHistory.length > 0 ? formatTimestamp(statusHistory[statusHistory.length - 1].timestamp) : 'N/A'}
        </span>
      </div>

      {/* Special status indicator for failed orders */}
      {isFailed && (
        <div className="mb-4 p-4 rounded-lg bg-red-50 border border-red-200">
          <div className="flex items-center gap-2">
            <XCircle className="h-5 w-5 text-red-500" />
            <span className="font-medium text-red-800">
              {isRejected ? 'Order Rejected' : 'Order Cancelled'}
            </span>
          </div>
          <p className="text-sm text-red-600 mt-1">
            {isRejected ? 'This order was rejected by the distributor.' : 'This order has been cancelled.'}
          </p>
        </div>
      )}

      {/* Status steps */}
      <div className="space-y-4">
        {activeSteps.map((step, index) => {
          const stepStatus = getStepStatus(index);

          return (
            <div key={step.key} className="flex items-start">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-colors ${getStepColor(stepStatus)}`}
              >
                {getStepIcon(step, stepStatus)}
              </div>
              <div className="ml-4 flex-1">
                <p
                  className={`font-medium transition-colors ${
                    stepStatus === 'completed' || stepStatus === 'current'
                      ? isStepFailed(stepStatus)
                        ? "text-red-700"
                        : "text-gray-900"
                      : "text-gray-500"
                  }`}
                  data-testid={`text-status-step-${step.key}`}
                >
                  {isFailed && stepStatus === 'current' 
                    ? (isRejected ? 'Order Rejected' : 'Order Cancelled')
                    : step.label
                  }
                </p>
                <p className={`text-sm transition-colors ${
                  isStepFailed(stepStatus)
                    ? "text-red-600"
                    : "text-gray-600"
                }`}>
                  {step.description}
                </p>
                <p className={`text-xs transition-colors ${
                  isStepFailed(stepStatus)
                    ? "text-red-500"
                    : "text-gray-500"
                }`}>
                  {getStepDescription(step, stepStatus)}
                </p>
              </div>
              <div className="flex items-center">
                {stepStatus === 'completed' ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : stepStatus === 'current' ? (
                  isFailed ? (
                    <XCircle className="h-5 w-5 text-red-500" />
                  ) : (
                    <Clock className="h-5 w-5 text-blue-500" />
                  )
                ) : stepStatus === 'failed' ? (
                  <XCircle className="h-5 w-5 text-red-400" />
                ) : (
                  <div className="w-5 h-5" />
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Progress for completed orders */}
      {isCompleted && (
        <div className="mt-4 p-4 rounded-lg bg-green-50 border border-green-200">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="font-medium text-green-800">Order Completed!</span>
          </div>
          <p className="text-sm text-green-600 mt-1">
            Your order has been successfully delivered. Thank you for your business!
          </p>
        </div>
      )}

      {/* Status History */}
      {showHistory && statusHistory.length > 0 && (
        <div className="mt-6">
          <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Status History
          </h4>
          <div className="space-y-3">
            {statusHistory.map((history, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge className={`${getStatusBadgeColor(history.status)} text-xs`}>
                      {history.status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Badge>
                    <span className="text-xs text-gray-500">
                      {formatTimestamp(history.timestamp)}
                    </span>
                  </div>
                  {history.notes && (
                    <p className="text-sm text-gray-600 mt-1">{history.notes}</p>
                  )}
                  {history.updatedBy && (
                    <p className="text-xs text-gray-500 mt-1">
                      Updated by: {history.updatedBy}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
