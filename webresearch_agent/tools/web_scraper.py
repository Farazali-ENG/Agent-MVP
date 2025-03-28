from typing import Dict, List, Optional, Set, Tuple, ClassVar
from bs4 import BeautifulSoup
from langchain_core.tools import BaseTool
import validators
import aiohttp
from urllib.parse import urljoin, urlparse
import asyncio
import re
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn

console = Console()

class WebScraperTool(BaseTool):
    name: str = "web_scraper"
    description: str = "Scrapes content from a given URL and its subpages"
    
    # Skip pages that match these patterns
    SKIP_PATTERNS: ClassVar[List[str]] = [
        r'/privacy-policy',
        r'/terms-of-service',
        r'/terms-and-conditions',
        r'/contact',
        r'/login',
        r'/signup',
        r'/cart',
        r'/checkout',
        r'/sitemap',
        r'.+\.(jpg|jpeg|png|gif|pdf|doc|docx|zip|rar)$'
    ]

    def _run(self, url: str) -> str:
        """Synchronous scrape content from the given URL"""
        return asyncio.run(self._arun(url))

    async def _extract_links(self, soup: BeautifulSoup, base_url: str, progress) -> Set[str]:
        """Extract and filter links from the page"""
        domain = urlparse(base_url).netloc
        links = set()
        
        task_id = progress.add_task(f"[cyan]Extracting links from {base_url}", total=None)
        try:
            all_links = soup.find_all('a', href=True)
            console.log(f"[cyan]Found {len(all_links)} raw links on {base_url}")
            
            for a in all_links:
                url = urljoin(base_url, a['href'])
                parsed_url = urlparse(url)
                
                # Skip if different domain or has anchor
                if parsed_url.netloc != domain or '#' in url:
                    continue
                    
                # Skip if matches skip patterns
                if any(re.search(pattern, url.lower()) for pattern in self.SKIP_PATTERNS):
                    continue
                
                # Clean the URL
                clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                if clean_url not in links:
                    links.add(clean_url)
            
            console.log(f"[green]Extracted {len(links)} valid links from {base_url}")
            return links
            
        except Exception as e:
            console.log(f"[red]Error extracting links from {base_url}: {str(e)}")
            return set()
        finally:
            progress.remove_task(task_id)

    async def _scrape_page(self, url: str, session: aiohttp.ClientSession, progress) -> Tuple[str, BeautifulSoup, Set[str]]:
        """Scrape a single page and extract its links concurrently"""
        task_id = progress.add_task(f"[cyan]Scraping {url}", total=None)
        start_time = time.time()
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            async with session.get(url, headers=headers, timeout=10) as response:
                response.raise_for_status()
                console.log(f"[green]Fetched {url} (Status: {response.status})")
                html = await response.text()
            
            soup = BeautifulSoup(html, 'html.parser')
            
            # Start link extraction concurrently with content processing
            links_task = asyncio.create_task(self._extract_links(soup, url, progress))
            
            # Process content
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text = '\n'.join(lines)
            
            # Wait for link extraction to complete
            links = await links_task
            
            content_length = len(text)
            elapsed_time = time.time() - start_time
            console.log(f"[green]Processed {url} ({content_length} chars) in {elapsed_time:.2f}s")
            
            return text, soup, links
            
        except Exception as e:
            console.log(f"[red]Error scraping {url}: {str(e)}")
            return "", None, set()
        finally:
            progress.remove_task(task_id)

    async def _crawl_site(self, start_url: str, max_pages: int = 10, max_concurrent: int = 5) -> str:
        """Crawl multiple pages of the site concurrently"""
        if not validators.url(start_url):
            console.log(f"[red]Invalid URL provided: {start_url}")
            return "Invalid URL provided"
            
        console.log(f"\n[cyan]Starting crawl of website: {start_url}")
        console.log(f"[cyan]Max pages: {max_pages}, Max concurrent: {max_concurrent}")
        
        visited = set()
        to_visit = {start_url}
        all_content = []
        start_time = time.time()
        
        try:
            connector = aiohttp.TCPConnector(limit=max_concurrent)
            async with aiohttp.ClientSession(connector=connector) as session:
                with Progress(
                    SpinnerColumn(),
                    *Progress.get_default_columns(),
                    TimeElapsedColumn(),
                    console=console,
                    transient=True
                ) as progress:
                    while to_visit and len(visited) < max_pages:
                        # Get next batch of URLs to process
                        batch_size = min(max_concurrent, max_pages - len(visited))
                        current_batch = list(to_visit)[:batch_size]
                        to_visit = to_visit - set(current_batch)
                        
                        console.log(f"[cyan]Processing batch of {len(current_batch)} URLs")
                        
                        # Create tasks for current batch
                        tasks = [self._scrape_page(url, session, progress) for url in current_batch]
                        results = await asyncio.gather(*tasks)
                        
                        # Process results
                        for url, (content, soup, new_links) in zip(current_batch, results):
                            visited.add(url)
                            
                            if content and soup:
                                all_content.append(f"\n=== Content from {url} ===\n{content}")
                                
                                # Add new links if we haven't hit the page limit
                                if len(visited) < max_pages:
                                    to_visit.update(new_links - visited)
                                    console.log(f"[cyan]Added {len(new_links)} new URLs to queue from {url}")
                
                total_chars = sum(len(content) for content in all_content)
                elapsed_time = time.time() - start_time
                console.log(f"\n[green]Crawl complete!")
                console.log(f"[green]Pages processed: {len(visited)}")
                console.log(f"[green]Total characters: {total_chars}")
                console.log(f"[green]Time elapsed: {elapsed_time:.2f}s")
                console.log(f"[green]Average time per page: {elapsed_time/len(visited):.2f}s")
                
                return '\n'.join(all_content)
                
        except Exception as e:
            console.log(f"[red]Error during crawl: {str(e)}")
            import traceback
            traceback.print_exc()
            return f"Error during crawl: {str(e)}"

    async def _arun(self, url: str) -> str:
        """Asynchronous scrape content from the given URL and its subpages"""
        return await self._crawl_site(url, max_pages=10, max_concurrent=5) 