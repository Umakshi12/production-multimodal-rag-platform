"""Web scraper for Oceanic website with sitemap support"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from logger import get_logger
from config import WEBSITE_URLS
import time

logger = get_logger(__name__)

class WebsiteScraper:
    """Scrapes website content with intelligent crawling"""
    
    def __init__(self, base_url="https://www.oceanic6solutionz.com"):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.visited_urls = set()
        self.max_pages = 50  # Safety limit
        
    def get_sitemap_urls(self):
        """Try to extract URLs from sitemap if available"""
        sitemap_urls = []
        try:
            sitemap_url = urljoin(self.base_url, "/sitemap.xml")
            response = requests.get(sitemap_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                locs = soup.find_all('loc')
                sitemap_urls = [loc.text for loc in locs]
                logger.info(f"Found {len(sitemap_urls)} URLs in sitemap")
                
        except Exception as e:
            logger.warning(f"Could not fetch sitemap: {e}")
            
        return sitemap_urls
    
    def crawl_website(self, start_urls=None):
        """Crawl website recursively to find all pages"""
        if start_urls is None:
            start_urls = WEBSITE_URLS
            
        # Try to get sitemap URLs first
        sitemap_urls = self.get_sitemap_urls()
        if sitemap_urls:
            start_urls = sitemap_urls[:self.max_pages]
        
        all_documents = []
        
        logger.info(f"Starting web scrape with {len(start_urls)} URLs")
        
        for url in start_urls[:self.max_pages]:
            if url in self.visited_urls:
                continue
                
            try:
                logger.info(f"Scraping: {url}")
                
                # Use WebBaseLoader
                loader = WebBaseLoader(url)
                docs = loader.load()
                
                # Enhance metadata
                for doc in docs:
                    doc.metadata['source_type'] = 'website'
                    doc.metadata['url'] = url
                    # Clean up content
                    doc.page_content = doc.page_content.strip()
                    
                all_documents.extend(docs)
                self.visited_urls.add(url)
                time.sleep(0.5)  # Be respectful to server
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                
        logger.info(f"Scraped {len(all_documents)} documents from {len(self.visited_urls)} URLs")
        return all_documents


def load_website_data():
    """Load data from company website"""
    scraper = WebsiteScraper()
    return scraper.crawl_website()
