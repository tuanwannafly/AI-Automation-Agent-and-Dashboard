'use client';

interface TokenCounterProps {
  count: number;
  limit?: number;
}

export function TokenCounter({ count, limit }: TokenCounterProps) {
  const percentage = limit ? (count / limit) * 100 : 0;
  const isWarning = limit && percentage > 80;
  const isDanger = limit && percentage > 95;

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="text-gray-400">Tokens:</span>
      <span className={`font-medium ${
        isDanger ? 'text-red-400' : isWarning ? 'text-yellow-400' : 'text-gray-300'
      }`}>
        {count.toLocaleString()}
      </span>
      {limit && (
        <span className="text-gray-500">/ {limit.toLocaleString()}</span>
      )}
    </div>
  );
}