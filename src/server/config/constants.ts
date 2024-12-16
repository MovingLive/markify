export const PORT = process.env.PORT || 3000;

export const SELECTORS = [
  'main#article-contents',
  '.markdown-body',
  'main',
  'article',
  '.content',
  '.documentation',
  'body'
] as const;