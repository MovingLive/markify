import { Request, Response, NextFunction } from 'express';

export const validateUrl = (req: Request, res: Response, next: NextFunction) => {
  const { url } = req.body;

  if (!url) {
    return res.status(400).json({ error: 'URL is required' });
  }

  try {
    new URL(url);
    next();
  } catch (error) {
    res.status(400).json({ error: 'Invalid URL format' });
  }
};