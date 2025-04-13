import { Check } from "lucide-react";
import React from "react";
import { ScrapingResult } from "../types/types";

interface ResultViewProps {
  result: ScrapingResult;
}

export function ResultView({ result }: ResultViewProps) {
  return (
    <div className="w-full max-w-3xl">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Contenu extrait</h3>
          <div className="flex items-center text-green-600 bg-green-50 px-3 py-1 rounded-full text-sm">
            <Check className="w-4 h-4 mr-1" />
            Téléchargement automatique
          </div>
        </div>
        <div className="mt-4 bg-gray-50 rounded-lg p-4">
          <pre className="whitespace-pre-wrap text-sm text-gray-800 font-mono">
            {result.content.slice(0, 500)}...
          </pre>
        </div>
        <p className="text-sm text-gray-500 mt-4">
          Extrait de: {result.url}
          <br />
          Date: {new Date(result.timestamp).toLocaleString()}
        </p>
      </div>
    </div>
  );
}
