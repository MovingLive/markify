import React, { useState } from 'react';
import { Search } from 'lucide-react';

interface UrlInputProps {
  onSubmit: (url: string, useCrawl4ai: boolean) => void;
  isLoading: boolean;
}

export function UrlInput({ onSubmit, isLoading }: UrlInputProps) {
  const [url, setUrl] = useState('');
  const [useCrawl4ai, setUseCrawl4ai] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onSubmit(url.trim(), useCrawl4ai);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl">
      <div className="relative flex flex-col gap-4">
        <div className="relative flex items-center">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter documentation URL (e.g., https://docs.example.com)"
            className="w-full px-4 py-3 pr-12 text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading}
            className="absolute right-2 p-2 text-gray-600 hover:text-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Search className="w-5 h-5" />
          </button>
        </div>
        
        <div className="flex items-center">
          <input
            type="checkbox"
            id="useCrawl4ai"
            checked={useCrawl4ai}
            onChange={(e) => setUseCrawl4ai(e.target.checked)}
            className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
            disabled={isLoading}
          />
          <label htmlFor="useCrawl4ai" className="ml-2 text-sm text-gray-700">
            Utiliser Crawl4AI (extraction avancée basée sur MCP)
          </label>
          {useCrawl4ai && (
            <span className="ml-2 px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded-full">
              Expérimental
            </span>
          )}
        </div>
      </div>
    </form>
  );
}