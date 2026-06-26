'use client';

import { CheckCircle, XCircle } from 'lucide-react';

interface StatusBarProps {
  status: 'connected' | 'disconnected' | 'connecting';
  message?: string;
}

export function StatusBar({ status, message }: StatusBarProps) {
  return (
    <div className="flex items-center justify-between px-4 py-2 border-b border-gray-700 bg-gray-800">
      <div className="flex items-center gap-2">
        {status === 'connected' && <CheckCircle className="w-4 h-4 text-green-400" />}
        {status === 'disconnected' && <XCircle className="w-4 h-4 text-red-400" />}
        {status === 'connecting' && (
          <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
        )}
        <span className={`text-sm ${
          status === 'connected' ? 'text-green-400' :
          status === 'disconnected' ? 'text-red-400' :
          'text-blue-400'
        }`}>
          {status === 'connected' ? 'Connected' :
           status === 'disconnected' ? 'Disconnected' :
           'Connecting...'}
        </span>
      </div>
      {message && <span className="text-xs text-gray-500">{message}</span>}
    </div>
  );
}