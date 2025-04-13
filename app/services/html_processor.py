from bs4 import BeautifulSoup
import html2text
from typing import List
from urllib.parse import urljoin

class HtmlProcessor:
    def __init__(self):
        self.html2text = html2text.HTML2Text()
        self.html2text.ignore_links = False
        self.html2text.body_width = 0

    def extract_main_content(self, html: str) -> str:
        """Extract main content from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try different common content selectors
        selectors = [
            'main#article-contents',
            '.markdown-body',
            'main',
            'article',
            'body'
        ]
        
        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                return str(content)
                
        return str(soup.body or soup)

    def convert_to_markdown(self, html: str) -> str:
        """Convert HTML to Markdown."""
        return self.html2text.handle(html)

    def process_markdown(self, markdown: str) -> str:
        """Process markdown content."""
        lines = markdown.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('# '):
                return '\n'.join(lines[i:])
        return markdown

    def extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract links from HTML content."""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            try:
                absolute_url = urljoin(base_url, href)
                links.append(absolute_url)
            except:
                continue
                
        return links