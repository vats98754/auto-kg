"""
Wikipedia scraper for mathematical concepts and topics.
"""

import requests
import wikipediaapi
from bs4 import BeautifulSoup
from typing import List, Dict, Set, Tuple
import re
import time
from tqdm import tqdm


class WikipediaMathScraper:
    """Scraper for mathematical concepts from Wikipedia."""
    
    def __init__(self, language: str = 'en', max_pages: int = 100, max_depth: int = 3, seed_topics: List[str] = None):
        """
        Initialize the Wikipedia math scraper.
        
        Args:
            language: Wikipedia language code (default: 'en')
            max_pages: Maximum number of pages to scrape
            max_depth: Maximum BFS depth from seeds
            seed_topics: Optional custom seed topics list
        """
        self.language = language
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.wiki = wikipediaapi.Wikipedia(
            language=language,
            extract_format=wikipediaapi.ExtractFormat.WIKI,
            user_agent='auto-kg/1.0 (https://github.com/vats98754/auto-kg)'
        )
        
        # Core mathematical topics to start with
        self.seed_topics = seed_topics or [
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

        # Exclusion prefixes/namespaces
        self.excluded_prefixes = (
            "Help:", "File:", "Category:", "Template:", "Talk:", "Portal:", "Wikipedia:", "Special:",
            "Draft:", "Module:", "User:" 
        )
    
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
            if any(link.startswith(prefix) for prefix in self.excluded_prefixes):
                continue
            if ":" in link and not link.startswith("Category:"):
                # Skip other namespaces
                continue
            
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

    def score_link(self, link: str, page_summary: str, page_content: str) -> float:
        """Score a linked title for math relevance using simple heuristics."""
        score = 0.0
        title = link
        t = title.lower()
        # Title signals
        math_terms = [
            'theorem','lemma','corollary','proof','equation','formula','function','space','group','ring','field',
            'algebra','calculus','geometry','topology','analysis','matrix','vector','derivative','integral','limit',
            'sequence','series','probability','statistics','graph','set','logic','algorithm','optimization','operator',
            'distribution','process','transform','differential','manifold','tensor','measure','norm','topological'
        ]
        if any(k in t for k in math_terms):
            score += 2.0
        # Avoid disambiguation/list pages
        if t.startswith('list of') or 'disambiguation' in t:
            score -= 1.5
        # Frequency in text
        cnt = page_content.lower().count(t)
        if cnt >= 5:
            score += 2.0
        elif cnt >= 2:
            score += 1.0
        # Mention in summary
        if t in (page_summary or '').lower():
            score += 0.5
        # Prefer shorter, well-formed titles
        if 2 <= len(title) <= 60:
            score += 0.2
        return score
    
    def scrape_mathematics_knowledge_graph(self) -> Dict:
        """
        Scrape Wikipedia to build a mathematical knowledge graph.
        
        Returns:
            Dictionary containing scraped mathematical concepts and relationships
        """
        visited_pages: Set[str] = set()
        # Queue of (title, depth). Start at depth 0 seeds.
        to_visit: List[Tuple[str, int]] = [(t, 0) for t in self.seed_topics]
        scraped_data = {}
        
        print(f"Starting Wikipedia scrape for mathematical concepts...")
        print(f"Seed topics: {len(self.seed_topics)}")
        print(f"Maximum pages to scrape: {self.max_pages}")
        print(f"Maximum BFS depth: {self.max_depth}")
        
        with tqdm(total=self.max_pages, desc="Scraping pages") as pbar:
            while to_visit and len(visited_pages) < self.max_pages:
                current_topic, depth = to_visit.pop(0)
                if current_topic in visited_pages:
                    continue
                if depth > self.max_depth:
                    continue

                print(f"\nScraping (depth {depth}): {current_topic}")
                page_data = self.get_page_content(current_topic)

                if page_data:
                    visited_pages.add(current_topic)
                    scraped_data[current_topic] = page_data

                    # Extract mathematical links for further exploration and score them
                    math_links = self.extract_mathematical_links(
                        page_data.get('content', ''),
                        page_data.get('links', [])
                    )

                    # Score and sort links to prioritize likely math concepts
                    scored: List[Tuple[str, float]] = [
                        (link, self.score_link(link, page_data.get('summary', ''), page_data.get('content', '')))
                        for link in math_links
                    ]
                    # Keep top-N links per page to control branching factor
                    scored.sort(key=lambda x: x[1], reverse=True)
                    top_links = [t for t, s in scored[:30]]  # limit branching

                    # Add new topics to visit at next depth level (BFS)
                    for link in top_links:
                        if link not in visited_pages and all(link != t for (t, _) in to_visit):
                            to_visit.append((link, depth + 1))

                    pbar.update(1)

                # Rate limiting to be respectful to Wikipedia
                time.sleep(0.5)
        
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