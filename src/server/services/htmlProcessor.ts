import * as cheerio from 'cheerio';
import { NodeHtmlMarkdown } from 'node-html-markdown';

export class HtmlProcessor {
  private nhm: NodeHtmlMarkdown;

  constructor() {
    this.nhm = new NodeHtmlMarkdown();
  }

  extractMainContent(html: string): string {
    const $ = cheerio.load(html);
    
    // Try different common content selectors
    let mainContent = $('main#article-contents');
    if (!mainContent.length) {
      mainContent = $('.markdown-body');
    }
    if (!mainContent.length) {
      mainContent = $('main');
    }
    if (!mainContent.length) {
      mainContent = $('article');
    }
    if (!mainContent.length) {
      mainContent = $('body');
    }

    return mainContent.html() || '';
  }

  convertToMarkdown(html: string): string {
    return this.nhm.translate(html);
  }

  processMarkdown(markdown: string): string {
    const lines = markdown.split('\n');
    const titleIndex = lines.findIndex(line => line.trim().startsWith('# '));
    
    if (titleIndex === -1) {
      return markdown;
    }
    
    return lines.slice(titleIndex).join('\n');
  }

  extractLinks($: cheerio.CheerioAPI, baseUrl: string): string[] {
    const links: string[] = [];
    $('a[href]').each((_, element) => {
      const href = $(element).attr('href');
      if (href) {
        try {
          const absoluteUrl = new URL(href, baseUrl).toString();
          links.push(absoluteUrl);
        } catch (error) {
          // Skip invalid URLs
        }
      }
    });
    return links;
  }
}