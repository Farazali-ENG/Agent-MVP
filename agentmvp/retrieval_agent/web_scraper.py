from typing import Set, List, Dict
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import logging

logger = logging.getLogger(__name__)

class WebsiteContentExtractor:
    def __init__(self, max_pages: int = 50, delay: float = 1.0):
        """Initialize the content extractor
        
        Args:
            max_pages: Maximum number of pages to scrape
            delay: Delay between requests in seconds
        """
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        
        # Initialize Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Initialize WebDriver
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(30)

    def __del__(self):
        """Cleanup WebDriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def is_valid_url(self, url: str, base_domain: str) -> bool:
        """Check if URL is valid and belongs to same domain"""
        try:
            parsed = urlparse(url)
            return parsed.netloc == base_domain
        except:
            return False

    def extract_text(self, url: str) -> str:
        """Extract readable text from a webpage"""
        try:
            self.driver.get(url)
            time.sleep(2)  # Wait for dynamic content to load
            
            # Get the rendered HTML
            html_content = self.driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(["script", "style", "nav", "footer"]):
                element.decompose()
                
            # Get text and clean it
            text = soup.get_text(separator=' ', strip=True)
            return ' '.join(text.split())
            
        except Exception as e:
            logger.error(f"Error extracting text from {url}: {str(e)}")
            return ""

    def get_links(self, url: str) -> List[str]:
        """Extract all valid links from a webpage"""
        links = set()
        base_domain = urlparse(url).netloc
        
        try:
            # Find all links
            elements = self.driver.find_elements(By.TAG_NAME, "a")
            
            for element in elements:
                try:
                    href = element.get_attribute('href')
                    if not href or href.startswith(('javascript:', '#', 'tel:', 'mailto:')):
                        continue
                        
                    # Clean the URL
                    parsed = urlparse(href)
                    cleaned_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    
                    if (self.is_valid_url(cleaned_url, base_domain) and 
                        cleaned_url not in self.visited_urls):
                        links.add(cleaned_url)
                        
                except Exception as e:
                    continue
                    
        except Exception as e:
            logger.error(f"Error finding links on {url}: {str(e)}")
            
        return list(links)

    def extract_all_content(self, start_url: str) -> List[Dict[str, str]]:
        """Extract content from all pages on the website
        
        Args:
            start_url: The starting URL to begin extraction
            
        Returns:
            List of dictionaries containing URL and content for each page
        """
        urls_to_visit = [start_url]
        extracted_content = []
        
        while urls_to_visit and len(self.visited_urls) < self.max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue
                
            logger.info(f"Processing page {len(self.visited_urls) + 1}/{self.max_pages}: {current_url}")
            
            # Extract content
            content = self.extract_text(current_url)
            if content:
                extracted_content.append({
                    "url": current_url,
                    "content": content,
                    "title": self.driver.title
                })
                
            self.visited_urls.add(current_url)
            
            # Get new links
            new_links = self.get_links(current_url)
            urls_to_visit.extend([url for url in new_links if url not in self.visited_urls])
            
            logger.info(f"Found {len(new_links)} new links")
            time.sleep(self.delay)
            
        logger.info(f"Extraction completed. Processed {len(self.visited_urls)} pages")
        return extracted_content

def extract_content(url: str) -> List[Dict[str, str]]:
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test the extractor
    extractor = WebsiteContentExtractor(max_pages=25, delay=2.0)
    website_url = "https://www.tri-townconstruction.com"
    
    content = []
    try:
        logger.info(f"Starting content extraction from {website_url}")
        content = extractor.extract_all_content(website_url)
        
        logger.info("\nContent Extracted Successfully")

    except KeyboardInterrupt:
        logger.info("Extraction interrupted by user")
    except Exception as e:
        logger.error(f"Error during extraction: {str(e)}")
    finally:
        extractor.driver.quit()
    
    return content


def get_content(url: str):

    content = extract_content(url)
    results = []

    for page in content:

        text = f"URL: {page['url']}\nTITLE: {page['title']}\nCONTENT: {page['content']}"
        results.append(text)

    return results
