import React from 'react';
import { CheckCircle, X } from 'lucide-react';

const SuccessMessage = ({ 
  message, 
  onClose, 
  showIcon = true,
  className = ''
}) => {
  if (!message) return null;

  return (
    <div className={`bg-green-50 border border-green-200 text-green-800 rounded-lg p-4 ${className}`}>
      <div className="flex items-start">
        {showIcon && (
          <CheckCircle className="h-5 w-5 mt-0.5 mr-3 flex-shrink-0 text-green-400" />
        )}
        <div className="flex-1">
          <p className="text-sm font-medium">{message}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="ml-3 flex-shrink-0 text-green-400 hover:text-green-600"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
};

export default SuccessMessage;
