import { Download } from "lucide-react";
import React from "react";
import { getDownloadUrl } from "../api/scraper";
import { ScrapingResult } from "../types/types";

interface ResultViewProps {
  result: ScrapingResult;
}

export function ResultView({ result }: ResultViewProps) {
  const handleDownload = () => {
    if (!result.taskId) {
      // Si le taskId n'est pas disponible, utiliser la méthode de téléchargement côté client
      const blob = new Blob([result.content], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `documentation-${new Date().toISOString().split("T")[0]}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } else {
      // Utiliser l'API pour télécharger le fichier
      const downloadUrl = getDownloadUrl(result.taskId);
      window.open(downloadUrl, "_blank");
    }
  };

  return (
    <div className="w-full max-w-3xl">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Contenu extrait</h3>
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            Télécharger Markdown
          </button>
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
