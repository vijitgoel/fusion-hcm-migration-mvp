'use client';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export default function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const getStatusConfig = (status: string) => {
    switch (status.toUpperCase()) {
      case 'SUCCESS':
        return { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-200' };
      case 'RUNNING':
        return { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-200' };
      case 'FAILED':
        return { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-200' };
      case 'PENDING':
        return { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-200' };
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-200' };
    }
  };

  const config = getStatusConfig(status);

  return (
    <span
      className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full border ${config.bg} ${config.text} ${config.border} ${className}`}
    >
      {status}
    </span>
  );
}