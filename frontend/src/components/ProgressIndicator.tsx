import React from 'react';

interface ProgressIndicatorProps {
  progress: number;
}

export function ProgressIndicator({ progress }: ProgressIndicatorProps) {
  return (
    <div className="w-full max-w-3xl">
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="text-sm text-gray-600 mt-2 text-center">
        Processing... {Math.round(progress)}%
      </p>
    </div>
  );
}