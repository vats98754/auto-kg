"""
Neo4j database integration for knowledge graph storage and retrieval.
"""

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    GraphDatabase = None

from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()


class Neo4jKnowledgeGraph:
    """Neo4j database manager for the knowledge graph."""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j database URI
            user: Database username  
            password: Database password
        """
        if not NEO4J_AVAILABLE:
            print("Warning: Neo4j driver not available. Install with: pip install neo4j")
            self.driver = None
            return
            
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'password')
        
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            print(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            self.driver = None
    
    def close(self):
        """Close database connection."""
        if self.driver:
            self.driver.close()
    
    def clear_database(self):
        """Clear all nodes and relationships from the database."""
        if not self.driver:
            print("No database connection available")
            return
            
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared.")
    
    def create_concept_node(self, title: str, summary: str, url: str, 
                           categories: List[str] = None, properties: Dict = None):
        """
        Create a concept node in the knowledge graph.
        
        Args:
            title: Concept title
            summary: Concept summary
            url: Wikipedia URL
            categories: List of categories
            properties: Additional properties
        """
        if not self.driver:
            print(f"No database connection available. Would create concept: {title}")
            return
            
        categories = categories or []
        properties = properties or {}
        
        query = """
        MERGE (c:Concept {title: $title})
        SET c.summary = $summary,
            c.url = $url,
            c.categories = $categories,
            c.created_at = datetime()
        """
        
        # Add custom properties
        for key, value in properties.items():
            query += f", c.{key} = ${key}"
        
        parameters = {
            'title': title,
            'summary': summary,
            'url': url,
            'categories': categories,
            **properties
        }
        
        with self.driver.session() as session:
            session.run(query, parameters)
    
    def create_relationship(self, from_concept: str, to_concept: str, 
                          relationship_type: str = "RELATES_TO", 
                          properties: Dict = None):
        """
        Create a relationship between two concepts.
        
        Args:
            from_concept: Source concept title
            to_concept: Target concept title
            relationship_type: Type of relationship
            properties: Relationship properties
        """
        properties = properties or {}
        
        query = f"""
        MATCH (a:Concept {{title: $from_concept}})
        MATCH (b:Concept {{title: $to_concept}})
        MERGE (a)-[r:{relationship_type}]->(b)
        SET r.created_at = datetime()
        """
        
        # Add custom properties to relationship
        for key, value in properties.items():
            query += f", r.{key} = ${key}"
        
        parameters = {
            'from_concept': from_concept,
            'to_concept': to_concept,
            **properties
        }
        
        with self.driver.session() as session:
            session.run(query, parameters)
    
    def get_concept(self, title: str) -> Optional[Dict]:
        """
        Retrieve a concept by title.
        
        Args:
            title: Concept title
            
        Returns:
            Concept data or None if not found
        """
        query = "MATCH (c:Concept {title: $title}) RETURN c"
        
        with self.driver.session() as session:
            result = session.run(query, title=title)
            record = result.single()
            if record:
                return dict(record['c'])
            return None
    
    def get_related_concepts(self, title: str, limit: int = 10) -> List[Dict]:
        """
        Get concepts related to the given concept.
        
        Args:
            title: Concept title
            limit: Maximum number of related concepts to return
            
        Returns:
            List of related concepts
        """
        query = """
        MATCH (c:Concept {title: $title})-[r]-(related:Concept)
        RETURN related, type(r) as relationship_type, r as relationship_props
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            result = session.run(query, title=title, limit=limit)
            related = []
            for record in result:
                related.append({
                    'concept': dict(record['related']),
                    'relationship_type': record['relationship_type'],
                    'relationship_props': dict(record['relationship_props'])
                })
            return related
    
    def search_concepts(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for concepts by title or summary.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching concepts
        """
        cypher_query = """
        MATCH (c:Concept)
        WHERE toLower(c.title) CONTAINS toLower($query) 
           OR toLower(c.summary) CONTAINS toLower($query)
        RETURN c
        LIMIT $limit
        """
        
        with self.driver.session() as session:
            result = session.run(cypher_query, query=query, limit=limit)
            return [dict(record['c']) for record in result]
    
    def get_graph_stats(self) -> Dict:
        """
        Get statistics about the knowledge graph.
        
        Returns:
            Dictionary with graph statistics
        """
        stats = {}
        
        with self.driver.session() as session:
            # Count nodes
            result = session.run("MATCH (c:Concept) RETURN count(c) as concept_count")
            stats['concept_count'] = result.single()['concept_count']
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as relationship_count")
            stats['relationship_count'] = result.single()['relationship_count']
            
            # Get relationship types
            result = session.run("MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count")
            stats['relationship_types'] = {record['rel_type']: record['count'] for record in result}
            
            # Get most connected concepts
            result = session.run("""
                MATCH (c:Concept)-[r]-()
                RETURN c.title as concept, count(r) as connections
                ORDER BY connections DESC
                LIMIT 10
            """)
            stats['most_connected'] = [(record['concept'], record['connections']) for record in result]
        
        return stats
    
    def export_graph_data(self) -> Dict:
        """
        Export the entire graph for visualization.
        
        Returns:
            Dictionary with nodes and edges for visualization
        """
        nodes = []
        edges = []
        
        with self.driver.session() as session:
            # Get all nodes
            result = session.run("MATCH (c:Concept) RETURN c")
            for record in result:
                concept = dict(record['c'])
                nodes.append({
                    'id': concept['title'],
                    'label': concept['title'],
                    'summary': concept.get('summary', ''),
                    'url': concept.get('url', ''),
                    'categories': concept.get('categories', [])
                })
            
            # Get all relationships
            result = session.run("""
                MATCH (a:Concept)-[r]->(b:Concept)
                RETURN a.title as source, b.title as target, type(r) as relationship_type, r as props
            """)
            for record in result:
                edges.append({
                    'source': record['source'],
                    'target': record['target'],
                    'relationship_type': record['relationship_type'],
                    'properties': dict(record['props'])
                })
        
        return {'nodes': nodes, 'edges': edges}
    
    def load_wikipedia_data(self, wikipedia_data: Dict):
        """
        Load scraped Wikipedia data into the knowledge graph.
        
        Args:
            wikipedia_data: Dictionary of scraped Wikipedia pages
        """
        print(f"Loading {len(wikipedia_data)} concepts into Neo4j...")
        
        # First pass: Create all concept nodes
        for title, page_data in wikipedia_data.items():
            self.create_concept_node(
                title=title,
                summary=page_data.get('summary', ''),
                url=page_data.get('url', ''),
                categories=page_data.get('categories', [])
            )
        
        # Second pass: Create relationships based on links
        for title, page_data in wikipedia_data.items():
            links = page_data.get('links', [])
            for link in links:
                # Only create relationships if the linked concept exists in our data
                if link in wikipedia_data:
                    self.create_relationship(
                        from_concept=title,
                        to_concept=link,
                        relationship_type="LINKS_TO"
                    )
        
        print("Wikipedia data loaded successfully!")
        
        # Print stats
        stats = self.get_graph_stats()
        print(f"Graph stats: {stats}")


if __name__ == "__main__":
    # Example usage
    kg = Neo4jKnowledgeGraph()
    
    if kg.driver:
        # Test connection
        stats = kg.get_graph_stats()
        print(f"Current graph stats: {stats}")
        
        kg.close()