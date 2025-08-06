import { CheckCircle, Clock, Package, Truck, XCircle, AlertCircle } from "lucide-react";

interface OrderStatusProps {
  status: string;
}

type OrderStatus = 'pending' | 'confirmed' | 'accepted' | 'packed' | 'dispatched' | 'out_for_delivery' | 'delivered' | 'cancelled' | 'rejected';
type StepStatus = 'completed' | 'current' | 'failed' | 'pending';

export default function OrderStatus({ status }: OrderStatusProps) {
  const statusSteps = [
    { key: 'pending', label: 'Order Placed', icon: Clock },
    { key: 'confirmed', label: 'Confirmed', icon: CheckCircle },
    { key: 'accepted', label: 'Accepted', icon: CheckCircle },
    { key: 'packed', label: 'Packed', icon: Package },
    { key: 'dispatched', label: 'Dispatched', icon: Truck },
    { key: 'out_for_delivery', label: 'Out for Delivery', icon: Truck },
    { key: 'delivered', label: 'Delivered', icon: CheckCircle },
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
    activeSteps = statusSteps.slice(0, 2); // Only show pending and confirmed/accepted
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
      // For failed orders, we need to check if this is where the failure occurred
      if (index === 1) {
        // If order was confirmed/accepted before being cancelled/rejected
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

  return (
    <div className="space-y-4">
      {/* Special status indicator for failed orders */}
      {isFailed && (
        <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200">
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
      {activeSteps.map((step, index) => {
        const stepStatus = getStepStatus(index);

        return (
          <div key={step.key} className="flex items-center">
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

      {/* Progress for completed orders */}
      {isCompleted && (
        <div className="mt-4 p-3 rounded-lg bg-green-50 border border-green-200">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            <span className="font-medium text-green-800">Order Completed!</span>
          </div>
          <p className="text-sm text-green-600 mt-1">
            Your order has been successfully delivered. Thank you for your business!
          </p>
        </div>
      )}
    </div>
  );
}
