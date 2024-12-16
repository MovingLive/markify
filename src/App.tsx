import React from 'react';
import { FileSearch } from 'lucide-react';
import { UrlInput } from './components/UrlInput';
import { ProgressIndicator } from './components/ProgressIndicator';
import { ResultView } from './components/ResultView';
import { useScraper } from './hooks/useScraper';

function App() {
  const { scrape, status, result } = useScraper();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-12">
        <div className="flex flex-col items-center gap-8">
          <div className="text-center">
            <div className="flex justify-center mb-4">
              <FileSearch className="w-16 h-16 text-blue-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Documentation Scraper
            </h1>
            <p className="text-gray-600 max-w-xl">
              Enter a documentation URL to automatically scrape and convert it to Markdown format.
              Perfect for offline reading or AI context building.
            </p>
          </div>

          <UrlInput onSubmit={scrape} isLoading={status.isLoading} />

          {status.isLoading && <ProgressIndicator progress={status.progress} />}

          {status.error && (
            <div className="text-red-600 bg-red-50 px-4 py-2 rounded-lg">
              {status.error}
            </div>
          )}

          {result && <ResultView result={result} />}
        </div>
      </div>
    </div>
  );
}

export default App;