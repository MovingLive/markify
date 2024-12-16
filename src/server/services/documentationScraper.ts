import axios from 'axios';
import * as cheerio from 'cheerio';
import { HtmlProcessor } from './htmlProcessor';
import { normalizeUrl, isValidNextUrl } from '../utils/urlUtils';
import { QueueItem, ScrapingProgress } from '../types/types';

export class DocumentationScraper {
  private visited: Set<string>;
  private queue: QueueItem[];
  private markdownContents: string[];
  private htmlProcessor: HtmlProcessor;
  private progress: ScrapingProgress;

  constructor() {
    this.visited = new Set();
    this.queue = [];
    this.markdownContents = [];
    this.htmlProcessor = new HtmlProcessor();
    this.progress = {
      totalPages: 0,
      processedPages: 0,
      currentUrl: '',
    };
  }

  async scrape(startUrl: string): Promise<string> {
    const normalizedStartUrl = normalizeUrl(startUrl);
    const { hostname: baseUrl, pathname } = new URL(normalizedStartUrl);
    const basePath = pathname.split('/')[1] || '';

    this.queue.push({ url: normalizedStartUrl, baseUrl, basePath });
    this.progress.totalPages = 1;

    while (this.queue.length > 0) {
      const { url, baseUrl, basePath } = this.queue.shift()!;
      const normalizedUrl = normalizeUrl(url);

      if (this.visited.has(normalizedUrl)) {
        continue;
      }

      this.visited.add(normalizedUrl);
      this.progress.currentUrl = normalizedUrl;
      this.progress.processedPages++;

      try {
        const response = await axios.get(normalizedUrl);
        const html = response.data;
        const $ = cheerio.load(html);

        // Process the page
        const mainContent = this.htmlProcessor.extractMainContent(html);
        const markdown = this.htmlProcessor.convertToMarkdown(mainContent);
        const processedMarkdown = this.htmlProcessor.processMarkdown(markdown);
        
        if (processedMarkdown.trim()) {
          this.markdownContents.push(processedMarkdown);
        }

        // Extract and queue new links
        const links = this.htmlProcessor.extractLinks($, normalizedUrl);
        for (const link of links) {
          if (!this.visited.has(link) && isValidNextUrl(link, baseUrl, basePath)) {
            this.queue.push({ url: link, baseUrl, basePath });
            this.progress.totalPages++;
          }
        }
      } catch (error) {
        console.error(`Error processing ${normalizedUrl}:`, error);
      }
    }

    return this.markdownContents.join('\n\n---\n\n');
  }

  getProgress(): ScrapingProgress {
    return this.progress;
  }
}