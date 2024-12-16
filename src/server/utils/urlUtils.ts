import { URL } from 'url';

export function normalizeUrl(url: string): string {
  try {
    const parsedUrl = new URL(url);
    // Remove hash fragment and trailing slash
    let normalized = `${parsedUrl.origin}${parsedUrl.pathname}${parsedUrl.search}`;
    if (normalized.endsWith('/')) {
      normalized = normalized.slice(0, -1);
    }
    return normalized;
  } catch (error) {
    throw new Error(`Invalid URL: ${url}`);
  }
}

export function getBaseInfo(url: string) {
  const parsedUrl = new URL(url);
  return {
    baseUrl: parsedUrl.hostname,
    basePath: parsedUrl.pathname.split('/')[1] || '',
  };
}

export function isValidNextUrl(nextUrl: string, baseUrl: string, basePath: string): boolean {
  try {
    const parsed = new URL(nextUrl);
    return parsed.hostname === baseUrl && parsed.pathname.startsWith(`/${basePath}`);
  } catch {
    return false;
  }
}