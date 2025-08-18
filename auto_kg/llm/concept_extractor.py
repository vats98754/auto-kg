"""
LLM integration for concept extraction and relationship inference.
"""

import os
import re
from typing import List, Dict, Tuple
from dotenv import load_dotenv

load_dotenv()


class ConceptExtractor:
    """Extract mathematical concepts and relationships using LLM or rule-based methods."""
    
    def __init__(self, model_type: str = "rule_based"):
        """
        Initialize the concept extractor.
        
        Args:
            model_type: Type of model to use ('openai', 'rule_based')
        """
        self.model_type = model_type
        
        if model_type == "openai":
            try:
                import openai
                self.openai_client = openai.OpenAI(
                    api_key=os.getenv('OPENAI_API_KEY')
                )
                self.model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
                print(f"Using OpenAI model: {self.model}")
            except ImportError:
                print("OpenAI not available, falling back to rule-based extraction")
                self.model_type = "rule_based"
            except Exception as e:
                print(f"OpenAI setup failed: {e}, falling back to rule-based extraction")
                self.model_type = "rule_based"
    
    def extract_concepts_rule_based(self, text: str) -> List[str]:
        """
        Extract mathematical concepts using rule-based approach.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted concepts
        """
        # Mathematical concept patterns
        patterns = [
            # Theorems, lemmas, etc.
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:theorem|lemma|corollary|proposition)\b',
            r'\b(?:theorem|lemma|corollary|proposition)\s+(?:of\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            
            # Mathematical objects and structures
            r'\b([A-Z][a-z]+(?:\s+[a-z]+)*)\s+(?:space|group|field|ring|algebra|manifold|function|operator)\b',
            r'\b(?:space|group|field|ring|algebra|manifold|function|operator)\s+(?:of\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            
            # Named mathematical entities
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:equation|formula|method|algorithm|series|sequence)\b',
            r'\b(?:equation|formula|method|algorithm|series|sequence)\s+(?:of\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            
            # General mathematical terms (capitalized)
            r'\b([A-Z][a-z]+(?:\s+[a-z]+)*(?:\s+[a-z]+)*)\b(?=\s+(?:is|are|was|were|can|may|will)\s+(?:a|an|the)?\s*(?:fundamental|important|basic|key|central|main|primary))',
        ]
        
        concepts = set()
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                concept = match.group(1).strip()
                if len(concept) > 2 and len(concept) < 50:  # Filter reasonable lengths
                    concepts.add(concept)
        
        # Also look for common mathematical terms
        math_terms = [
            "calculus", "algebra", "geometry", "topology", "analysis", "statistics",
            "probability", "number theory", "set theory", "graph theory", "logic",
            "optimization", "differential equations", "linear algebra", "abstract algebra",
            "real analysis", "complex analysis", "functional analysis", "measure theory",
            "combinatorics", "discrete mathematics", "numerical analysis"
        ]
        
        text_lower = text.lower()
        for term in math_terms:
            if term in text_lower:
                concepts.add(term.title())
        
        return list(concepts)
    
    def extract_relationships_rule_based(self, text: str, concepts: List[str]) -> List[Tuple[str, str, str]]:
        """
        Extract relationships between concepts using rule-based approach.
        
        Args:
            text: Input text
            concepts: List of known concepts
            
        Returns:
            List of (source, target, relationship_type) tuples
        """
        relationships = []
        text_lower = text.lower()
        
        # Relationship patterns
        relationship_patterns = {
            "generalizes": [r"(\w+)\s+(?:generalizes?|extends?|is\s+a\s+generalization\s+of)\s+(\w+)"],
            "specializes": [r"(\w+)\s+(?:specializes?|is\s+a\s+special\s+case\s+of|is\s+a\s+type\s+of)\s+(\w+)"],
            "uses": [r"(\w+)\s+(?:uses?|employs?|utilizes?|applies?|relies\s+on)\s+(\w+)"],
            "related_to": [r"(\w+)\s+(?:is\s+related\s+to|relates\s+to|connected\s+to|associated\s+with)\s+(\w+)"],
            "implies": [r"(\w+)\s+(?:implies?|leads\s+to|results\s+in|gives\s+rise\s+to)\s+(\w+)"],
            "proven_by": [r"(\w+)\s+(?:is\s+proven\s+by|is\s+demonstrated\s+by|follows\s+from)\s+(\w+)"]
        }
        
        for rel_type, patterns in relationship_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower)
                for match in matches:
                    source = match.group(1).strip()
                    target = match.group(2).strip()
                    
                    # Try to match with known concepts
                    source_concept = self._find_matching_concept(source, concepts)
                    target_concept = self._find_matching_concept(target, concepts)
                    
                    if source_concept and target_concept and source_concept != target_concept:
                        relationships.append((source_concept, target_concept, rel_type))
        
        return relationships
    
    def _find_matching_concept(self, text: str, concepts: List[str]) -> str:
        """Find the best matching concept for a given text."""
        text_lower = text.lower()
        
        # Exact match
        for concept in concepts:
            if concept.lower() == text_lower:
                return concept
        
        # Partial match
        for concept in concepts:
            if text_lower in concept.lower() or concept.lower() in text_lower:
                return concept
        
        return None
    
    def extract_concepts_openai(self, text: str) -> List[str]:
        """
        Extract mathematical concepts using OpenAI API.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted concepts
        """
        if self.model_type != "openai":
            return self.extract_concepts_rule_based(text)
        
        prompt = f"""
        Extract mathematical concepts from the following text. Return only the concept names, one per line.
        Focus on mathematical terms, theorems, methods, structures, and important mathematical objects.
        
        Text: {text[:2000]}  # Limit text length
        
        Mathematical concepts:
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a mathematics expert. Extract mathematical concepts from text."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            concepts_text = response.choices[0].message.content
            concepts = [line.strip() for line in concepts_text.split('\n') if line.strip()]
            return concepts
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self.extract_concepts_rule_based(text)
    
    def extract_relationships_openai(self, text: str, concepts: List[str]) -> List[Tuple[str, str, str]]:
        """
        Extract relationships using OpenAI API.
        
        Args:
            text: Input text
            concepts: List of known concepts
            
        Returns:
            List of (source, target, relationship_type) tuples
        """
        if self.model_type != "openai":
            return self.extract_relationships_rule_based(text, concepts)
        
        concepts_str = ", ".join(concepts[:20])  # Limit number of concepts
        
        prompt = f"""
        Given the following text and list of mathematical concepts, identify relationships between the concepts.
        Return relationships in the format: "source_concept -> target_concept (relationship_type)"
        
        Concepts: {concepts_str}
        
        Text: {text[:1500]}
        
        Relationships:
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a mathematics expert. Identify relationships between mathematical concepts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.1
            )
            
            relationships_text = response.choices[0].message.content
            relationships = []
            
            for line in relationships_text.split('\n'):
                if '->' in line and '(' in line:
                    try:
                        parts = line.split('->')
                        source = parts[0].strip()
                        target_and_type = parts[1].strip()
                        
                        if '(' in target_and_type:
                            target = target_and_type.split('(')[0].strip()
                            rel_type = target_and_type.split('(')[1].split(')')[0].strip()
                            relationships.append((source, target, rel_type))
                    except:
                        continue
            
            return relationships
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self.extract_relationships_rule_based(text, concepts)
    
    def process_wikipedia_page(self, page_data: Dict) -> Dict:
        """
        Process a Wikipedia page to extract concepts and relationships.
        
        Args:
            page_data: Wikipedia page data
            
        Returns:
            Dictionary with extracted concepts and relationships
        """
        title = page_data.get('title', '')
        content = page_data.get('content', '')
        summary = page_data.get('summary', '')
        
        # Combine summary and first part of content for processing
        text_to_process = f"{summary}\n\n{content[:3000]}"
        
        # Extract concepts
        if self.model_type == "openai":
            concepts = self.extract_concepts_openai(text_to_process)
        else:
            concepts = self.extract_concepts_rule_based(text_to_process)
        
        # Add the page title as a concept
        if title not in concepts:
            concepts.insert(0, title)
        
        # Extract relationships
        if self.model_type == "openai":
            relationships = self.extract_relationships_openai(text_to_process, concepts)
        else:
            relationships = self.extract_relationships_rule_based(text_to_process, concepts)
        
        return {
            'title': title,
            'concepts': concepts,
            'relationships': relationships,
            'original_data': page_data
        }


if __name__ == "__main__":
    # Example usage
    extractor = ConceptExtractor(model_type="rule_based")
    
    sample_text = """
    Linear algebra is the branch of mathematics concerning linear equations, linear maps,
    and their representations in vector spaces and through matrices. Linear algebra is central
    to almost all areas of mathematics. For instance, linear algebra is fundamental in modern
    presentations of geometry, including for defining basic objects such as lines, planes and rotations.
    Also, functional analysis, a branch of mathematical analysis, may be viewed as the application
    of linear algebra to spaces of functions.
    """
    
    concepts = extractor.extract_concepts_rule_based(sample_text)
    print(f"Extracted concepts: {concepts}")
    
    relationships = extractor.extract_relationships_rule_based(sample_text, concepts)
    print(f"Extracted relationships: {relationships}")