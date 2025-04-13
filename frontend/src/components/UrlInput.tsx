import { Download } from "lucide-react";
import React, { useEffect, useState } from "react";
import { ScrapingOptions } from "../types/types";

interface UrlInputProps {
  onSubmit: (url: string, options: ScrapingOptions) => void;
  isLoading: boolean;
}

export function UrlInput({ onSubmit, isLoading }: UrlInputProps) {
  const [url, setUrl] = useState("");
  const [filename, setFilename] = useState("");
  const [format, setFormat] =
    useState<ScrapingOptions["format"]>("single_file");

  // Extraction automatique du dernier segment de l'URL comme nom de fichier
  useEffect(() => {
    if (url) {
      try {
        const urlObj = new URL(url);
        const pathSegments = urlObj.pathname.split("/").filter(Boolean);
        const lastSegment =
          pathSegments[pathSegments.length - 1] || "documentation";
        setFilename(lastSegment);
      } catch (error) {
        // URL invalide, ne rien faire
      }
    }
  }, [url]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url.trim()) {
      onSubmit(url.trim(), {
        format,
        filename: filename.trim() || "documentation",
      });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl space-y-4">
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
          <Download className="w-5 h-5" />
        </button>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
        <div className="w-full sm:w-1/3">
          <label
            htmlFor="filename"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Nom du fichier
          </label>
          <input
            type="text"
            id="filename"
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
            placeholder="Nom du fichier à télécharger"
            className="w-full px-4 py-2 text-gray-900 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
        </div>

        <div className="w-full sm:w-2/3">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Format d'exportation
          </label>
          <div className="flex flex-col sm:flex-row flex-wrap gap-3">
            <div className="flex items-center">
              <input
                type="radio"
                id="single-file"
                name="format"
                value="single_file"
                checked={format === "single_file"}
                onChange={() => setFormat("single_file")}
                className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                disabled={isLoading}
              />
              <label
                htmlFor="single-file"
                className="ml-2 text-sm text-gray-700"
              >
                Fichier unique (.md)
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="radio"
                id="zip-files"
                name="format"
                value="zip_files"
                checked={format === "zip_files"}
                onChange={() => setFormat("zip_files")}
                className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                disabled={isLoading}
              />
              <label htmlFor="zip-files" className="ml-2 text-sm text-gray-700">
                Zip avec arborescence
              </label>
            </div>
            <div className="flex items-center">
              <input
                type="radio"
                id="zip-flat"
                name="format"
                value="zip_flat"
                checked={format === "zip_flat"}
                onChange={() => setFormat("zip_flat")}
                className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                disabled={isLoading}
              />
              <label htmlFor="zip-flat" className="ml-2 text-sm text-gray-700">
                Zip plat (sans dossiers)
              </label>
            </div>
          </div>
        </div>
      </div>
    </form>
  );
}
