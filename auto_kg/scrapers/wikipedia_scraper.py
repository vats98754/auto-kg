"""
Wikipedia scraper for mathematical concepts and topics.
"""

import requests
import wikipediaapi
from bs4 import BeautifulSoup
from typing import List, Dict, Set
import re
import time
from tqdm import tqdm


class WikipediaMathScraper:
    """Scraper for mathematical concepts from Wikipedia."""
    
    def __init__(self, language: str = 'en', max_pages: int = 100):
        """
        Initialize the Wikipedia math scraper.
        
        Args:
            language: Wikipedia language code (default: 'en')
            max_pages: Maximum number of pages to scrape
        """
        self.language = language
        self.max_pages = max_pages
        self.wiki = wikipediaapi.Wikipedia(
            language=language,
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='auto-kg/1.0 (https://github.com/vats98754/auto-kg)'
        )
        
        # Core mathematical topics to start with
        self.seed_topics = [
            "Mathematics",
            "Algebra",
            "Calculus", 
            "Geometry",
            "Topology",
            "Number theory",
            "Analysis",
            "Statistics",
            "Probability theory",
            "Linear algebra",
            "Abstract algebra",
            "Differential equations",
            "Complex analysis",
            "Real analysis",
            "Set theory",
            "Logic",
            "Graph theory",
            "Combinatorics",
            "Mathematical optimization",
            "Numerical analysis"
        ]
    
    def get_page_content(self, title: str) -> Dict:
        """
        Get content and metadata for a Wikipedia page.
        
        Args:
            title: Wikipedia page title
            
        Returns:
            Dictionary containing page content and metadata
        """
        try:
            page = self.wiki.page(title)
            
            if not page.exists():
                print(f"Page not found: {title}")
                return None
            
            # Get page content
            content = {
                'title': page.title,
                'url': page.fullurl,
                'summary': page.summary[:1000] if page.summary else '',  # Limit summary length
                'content': page.text[:5000] if page.text else '',  # Limit content length
                'links': list(page.links.keys())[:50],  # Limit links to avoid overwhelming
                'categories': list(page.categories.keys())[:10]  # Limit categories
            }
            
            return content
            
        except Exception as e:
            print(f"Error scraping {title}: {e}")
            return None
    
    def extract_mathematical_links(self, content: str, links: List[str]) -> List[str]:
        """
        Filter links to find mathematical concepts.
        
        Args:
            content: Page content
            links: List of linked page titles
            
        Returns:
            List of mathematical concept links
        """
        # Keywords that indicate mathematical content
        math_keywords = [
            'theorem', 'lemma', 'proof', 'equation', 'formula', 'function',
            'algebra', 'calculus', 'geometry', 'topology', 'analysis',
            'number', 'theory', 'space', 'group', 'field', 'ring',
            'matrix', 'vector', 'derivative', 'integral', 'limit',
            'sequence', 'series', 'probability', 'statistics', 'graph',
            'set', 'logic', 'algorithm', 'optimization', 'mathematical'
        ]
        
        mathematical_links = []
        
        for link in links:
            link_lower = link.lower()
            
            # Check if link contains mathematical keywords
            if any(keyword in link_lower for keyword in math_keywords):
                mathematical_links.append(link)
            
            # Check if link is mentioned in mathematical context in content
            elif link in content:
                # Find context around the link mention
                content_lower = content.lower()
                link_index = content_lower.find(link.lower())
                if link_index != -1:
                    context = content_lower[max(0, link_index-100):link_index+100]
                    if any(keyword in context for keyword in math_keywords):
                        mathematical_links.append(link)
        
        return mathematical_links
    
    def scrape_mathematics_knowledge_graph(self) -> Dict:
        """
        Scrape Wikipedia to build a mathematical knowledge graph.
        
        Returns:
            Dictionary containing scraped mathematical concepts and relationships
        """
        visited_pages = set()
        to_visit = self.seed_topics.copy()
        scraped_data = {}
        
        print(f"Starting Wikipedia scrape for mathematical concepts...")
        print(f"Seed topics: {len(self.seed_topics)}")
        print(f"Maximum pages to scrape: {self.max_pages}")
        
        with tqdm(total=min(self.max_pages, len(to_visit)), desc="Scraping pages") as pbar:
            while to_visit and len(visited_pages) < self.max_pages:
                current_topic = to_visit.pop(0)
                
                if current_topic in visited_pages:
                    continue
                
                print(f"\nScraping: {current_topic}")
                page_data = self.get_page_content(current_topic)
                
                if page_data:
                    visited_pages.add(current_topic)
                    scraped_data[current_topic] = page_data
                    
                    # Extract mathematical links for further exploration
                    math_links = self.extract_mathematical_links(
                        page_data['content'], 
                        page_data['links']
                    )
                    
                    # Add new mathematical topics to visit
                    for link in math_links:
                        if link not in visited_pages and link not in to_visit:
                            to_visit.append(link)
                    
                    pbar.update(1)
                
                # Rate limiting to be respectful to Wikipedia
                time.sleep(1)
        
        print(f"\nScraping completed!")
        print(f"Total pages scraped: {len(scraped_data)}")
        print(f"Topics discovered: {list(scraped_data.keys())[:10]}...")
        
        return scraped_data
    
    def save_scraped_data(self, data: Dict, filename: str = "wikipedia_math_data.json"):
        """
        Save scraped data to a JSON file.
        
        Args:
            data: Scraped data dictionary
            filename: Output filename
        """
        import json
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Scraped data saved to {filename}")
        except Exception as e:
            print(f"Error saving data: {e}")


if __name__ == "__main__":
    # Example usage
    scraper = WikipediaMathScraper(max_pages=20)  # Small test run
    data = scraper.scrape_mathematics_knowledge_graph()
    scraper.save_scraped_data(data)