import { CheckCircle, Clock, Package, Truck } from "lucide-react";

interface OrderStatusProps {
  status: string;
}

export default function OrderStatus({ status }: OrderStatusProps) {
  const statusSteps = [
    { key: 'pending', label: 'Order Placed', icon: Package },
    { key: 'confirmed', label: 'Confirmed', icon: CheckCircle },
    { key: 'packed', label: 'Packed', icon: Package },
    { key: 'out_for_delivery', label: 'Out for Delivery', icon: Truck },
    { key: 'delivered', label: 'Delivered', icon: CheckCircle },
  ];

  const currentStepIndex = statusSteps.findIndex(step => step.key === status);

  return (
    <div className="space-y-4">
      {statusSteps.map((step, index) => {
        const isCompleted = index <= currentStepIndex;
        const isCurrent = index === currentStepIndex;
        const isPending = index > currentStepIndex;

        return (
          <div key={step.key} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-medium ${
                isCompleted
                  ? isCurrent
                    ? "bg-accent"
                    : "bg-secondary"
                  : "bg-gray-300"
              }`}
            >
              {isCompleted ? (
                index < currentStepIndex ? (
                  <CheckCircle className="h-4 w-4" />
                ) : (
                  index + 1
                )
              ) : (
                <Clock className="h-4 w-4" />
              )}
            </div>
            <div className="ml-4 flex-1">
              <p
                className={`font-medium ${
                  isCompleted ? "text-gray-900" : "text-gray-500"
                }`}
                data-testid={`text-status-step-${step.key}`}
              >
                {step.label}
              </p>
              <p className="text-sm text-gray-600">
                {isCurrent ? "In Progress" : isCompleted ? "Completed" : "Pending"}
              </p>
            </div>
            {isCompleted ? (
              <CheckCircle className="h-5 w-5 text-secondary" />
            ) : isCurrent ? (
              <Clock className="h-5 w-5 text-accent" />
            ) : (
              <div className="w-5 h-5" />
            )}
          </div>
        );
      })}
    </div>
  );
}
