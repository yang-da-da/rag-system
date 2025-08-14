import React from 'react';
import { AlertCircle, X } from 'lucide-react';

const ErrorMessage = ({ 
  message, 
  onClose, 
  type = 'error',
  showIcon = true,
  className = ''
}) => {
  const typeClasses = {
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
    success: 'bg-green-50 border-green-200 text-green-800'
  };

  const iconClasses = {
    error: 'text-red-400',
    warning: 'text-yellow-400',
    info: 'text-blue-400',
    success: 'text-green-400'
  };

  if (!message) return null;

  return (
    <div className={`border rounded-lg p-4 ${typeClasses[type]} ${className}`}>
      <div className="flex items-start">
        {showIcon && (
          <AlertCircle className={`h-5 w-5 mt-0.5 mr-3 flex-shrink-0 ${iconClasses[type]}`} />
        )}
        <div className="flex-1">
          <p className="text-sm font-medium">{message}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-3 flex-shrink-0 text-gray-400 hover:text-gray-600"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;
