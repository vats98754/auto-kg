"""
LLM integration for concept extraction and relationship inference.
"""

import os
import re
from typing import List, Dict, Tuple
from dotenv import load_dotenv

load_dotenv()


class ConceptExtractor:
    """Extract important concepts and relationships from any domain using LLM or rule-based methods.
    
    Supports multiple extraction methods:
    - rule_based: Pattern-based extraction for any domain
    - huggingface: Free local LLM inference using transformers
    - openai: OpenAI API (requires API key)
    """
    
    def __init__(self, model_type: str = "rule_based"):
        """
        Initialize the concept extractor.
        
        Args:
            model_type: Type of model to use ('openai', 'rule_based', 'huggingface')
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
        
        elif model_type == "huggingface":
            try:
                from transformers import pipeline
                # Use a lightweight model for concept extraction
                self.hf_pipeline = pipeline(
                    "text2text-generation", 
                    model="google/flan-t5-small",
                    max_length=512,
                    device_map="auto" if hasattr(__import__('torch'), 'cuda') and __import__('torch').cuda.is_available() else "cpu"
                )
                print("Using Hugging Face model: google/flan-t5-small")
            except ImportError:
                print("Transformers not available, falling back to rule-based extraction")
                self.model_type = "rule_based"
            except Exception as e:
                print(f"Hugging Face setup failed: {e}, falling back to rule-based extraction")
                self.model_type = "rule_based"
    
    def extract_concepts_rule_based(self, text: str) -> List[str]:
        """
        Extract important concepts using rule-based approach.
        Generalized for any domain, not just mathematics.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted concepts
        """
        concepts = set()
        
        # Domain-specific compound concepts (high priority)
        domain_indicators = [
            # Technology
            r'\b(artificial intelligence|machine learning|deep learning|data analytics|cloud computing|digital transformation|cyber security)\b',
            # Business
            r'\b(business process|customer experience|market requirements|infrastructure costs|value delivery|supply chain)\b',
            # Science/Environment
            r'\b(climate change|environmental science|renewable energy|solar power|wind energy|greenhouse gas|carbon dioxide|fossil fuels|biodiversity conservation|ecosystem dynamics)\b',
            # Healthcare
            r'\b(public health|medical research|drug development|clinical trials|health care|patient care)\b',
            # Education
            r'\b(higher education|educational technology|distance learning|curriculum development)\b',
        ]
        
        text_lower = text.lower()
        for pattern in domain_indicators:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                concept = match.group(1).strip()
                concepts.add(concept.title())
        
        # Key technical terms and proper nouns
        patterns = [
            # Clean multi-word proper nouns (2-3 words max)
            r'\b([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',
            
            # Named methods, techniques, systems (cleaner patterns)
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(technology|method|system|analysis|management|development|research|strategy)\b',
            
            # Important scientific/technical terms
            r'\b([A-Z][a-z]+(?:\s+[a-z]+)?)\s+(science|energy|power|emissions|conservation|adaptation|efficiency)\b',
            
            # Single important technical words (if they appear frequently)
            r'\b([A-Z][a-z]{4,})\b',  # Capitalized words of 5+ letters
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                if len(match.groups()) >= 2:
                    # For two-group patterns, combine them meaningfully
                    concept1 = match.group(1).strip()
                    concept2 = match.group(2).strip()
                    
                    # Create compound concept if it makes sense
                    compound = f"{concept1} {concept2}".strip()
                    if 5 < len(compound) < 40 and not any(word in compound.lower() for word in ['the', 'this', 'that', 'these', 'those', 'while', 'since']):
                        concepts.add(compound.title())
                else:
                    concept = match.group(1).strip()
                    if 3 < len(concept) < 30:
                        concepts.add(concept)
        
        # Filter by frequency and importance
        text_lower = text.lower()
        concept_scores = {}
        
        for concept in list(concepts):
            score = text_lower.count(concept.lower())
            
            # Boost important characteristics
            if concept.lower() in text[:300].lower():  # Appears early
                score += 2
            if len(concept.split()) > 1:  # Multi-word concepts
                score += 1
            if any(keyword in concept.lower() for keyword in ['technology', 'system', 'science', 'management', 'development', 'research']):
                score += 1
                
            concept_scores[concept] = score
        
        # Filter out low-quality concepts
        filtered_concepts = []
        for concept in concepts:
            score = concept_scores.get(concept, 0)
            concept_lower = concept.lower()
            
            # Skip if too generic or low quality
            if any(bad_word in concept_lower for bad_word in ['while', 'since', 'then', 'also', 'such', 'more', 'most', 'some', 'many', 'other', 'into', 'from']):
                continue
            if score < 1:  # Must appear at least once
                continue
            if len(concept) < 4 or len(concept) > 40:  # Reasonable length
                continue
                
            filtered_concepts.append((concept, score))
        
        # Sort by score (desc) then alphabetically, limit results
        filtered_concepts.sort(key=lambda x: (-x[1], x[0].lower()))
        return [concept for concept, score in filtered_concepts[:20]]
    
    def extract_relationships_rule_based(self, text: str, concepts: List[str]) -> List[Tuple[str, str, str]]:
        """
        Extract relationships between concepts using rule-based approach.
        Generalized for any domain.
        
        Args:
            text: Input text
            concepts: List of known concepts
            
        Returns:
            List of (source, target, relationship_type) tuples
        """
        relationships = []
        text_lower = text.lower()
        
        # Generalized relationship patterns
        relationship_patterns = {
            "is_type_of": [
                r"(\w+(?:\s+\w+)*)\s+(?:is\s+a\s+type\s+of|is\s+a\s+kind\s+of|is\s+a\s+form\s+of)\s+(\w+(?:\s+\w+)*)",
                r"(\w+(?:\s+\w+)*)\s+(?:includes?|contains?|encompasses?)\s+(\w+(?:\s+\w+)*)",
            ],
            "uses": [
                r"(\w+(?:\s+\w+)*)\s+(?:uses?|employs?|utilizes?|applies?|relies\s+on|depends\s+on)\s+(\w+(?:\s+\w+)*)",
                r"(\w+(?:\s+\w+)*)\s+(?:is\s+based\s+on|builds\s+on|leverages?)\s+(\w+(?:\s+\w+)*)",
            ],
            "related_to": [
                r"(\w+(?:\s+\w+)*)\s+(?:is\s+related\s+to|relates\s+to|connected\s+to|associated\s+with|linked\s+to)\s+(\w+(?:\s+\w+)*)",
                r"(\w+(?:\s+\w+)*)\s+(?:and|&)\s+(\w+(?:\s+\w+)*)\s+(?:are\s+related|work\s+together|interact)",
            ],
            "causes": [
                r"(\w+(?:\s+\w+)*)\s+(?:causes?|leads\s+to|results\s+in|gives\s+rise\s+to|produces?)\s+(\w+(?:\s+\w+)*)",
                r"(\w+(?:\s+\w+)*)\s+(?:is\s+caused\s+by|results\s+from|stems\s+from)\s+(\w+(?:\s+\w+)*)",
            ],
            "influences": [
                r"(\w+(?:\s+\w+)*)\s+(?:influences?|affects?|impacts?|modifies?)\s+(\w+(?:\s+\w+)*)",
                r"(\w+(?:\s+\w+)*)\s+(?:is\s+influenced\s+by|is\s+affected\s+by)\s+(\w+(?:\s+\w+)*)",
            ],
            "implements": [
                r"(\w+(?:\s+\w+)*)\s+(?:implements?|realizes?|executes?|performs?)\s+(\w+(?:\s+\w+)*)",
                r"(\w+(?:\s+\w+)*)\s+(?:is\s+implemented\s+by|is\s+realized\s+by)\s+(\w+(?:\s+\w+)*)",
            ],
            "part_of": [
                r"(\w+(?:\s+\w+)*)\s+(?:is\s+part\s+of|belongs\s+to|is\s+a\s+component\s+of)\s+(\w+(?:\s+\w+)*)",
                r"(\w+(?:\s+\w+)*)\s+(?:consists\s+of|comprises?|is\s+made\s+up\s+of)\s+(\w+(?:\s+\w+)*)",
            ]
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
    
    def extract_concepts_huggingface(self, text: str) -> List[str]:
        """
        Extract concepts using Hugging Face transformers (free local inference).
        
        Args:
            text: Input text
            
        Returns:
            List of extracted concepts
        """
        if self.model_type != "huggingface":
            return self.extract_concepts_rule_based(text)
        
        # Limit text length for processing
        text_chunk = text[:1500] if len(text) > 1500 else text
        
        prompt = f"""Extract the most important concepts and key terms from the following text. 
List them as comma-separated values, focusing on:
- Main topics and subjects
- Important technical terms
- Key entities and proper nouns
- Significant processes or methods

Text: {text_chunk}

Important concepts:"""
        
        try:
            result = self.hf_pipeline(prompt, max_length=200, do_sample=False)
            concepts_text = result[0]['generated_text'] if result else ""
            
            # Parse the concepts from the response
            concepts = []
            if concepts_text:
                # Split by commas and clean up
                raw_concepts = concepts_text.split(',')
                for concept in raw_concepts:
                    clean_concept = concept.strip().strip('.,;:')
                    if clean_concept and 2 < len(clean_concept) < 50:
                        # Capitalize first letter for consistency
                        clean_concept = clean_concept[0].upper() + clean_concept[1:] if len(clean_concept) > 1 else clean_concept.upper()
                        concepts.append(clean_concept)
            
            # If HF extraction failed or returned few results, fall back to rule-based
            if len(concepts) < 3:
                print("HF extraction yielded few results, combining with rule-based")
                rule_based_concepts = self.extract_concepts_rule_based(text)
                concepts.extend(rule_based_concepts)
                # Remove duplicates while preserving order
                seen = set()
                concepts = [x for x in concepts if not (x.lower() in seen or seen.add(x.lower()))]
            
            return concepts[:20]  # Limit to top 20 concepts
            
        except Exception as e:
            print(f"Hugging Face extraction error: {e}, falling back to rule-based")
            return self.extract_concepts_rule_based(text)
    
    def extract_relationships_huggingface(self, text: str, concepts: List[str]) -> List[Tuple[str, str, str]]:
        """
        Extract relationships using Hugging Face transformers.
        
        Args:
            text: Input text
            concepts: List of known concepts
            
        Returns:
            List of (source, target, relationship_type) tuples
        """
        if self.model_type != "huggingface":
            return self.extract_relationships_rule_based(text, concepts)
        
        # Limit concepts for processing
        concepts_subset = concepts[:15]
        concepts_str = ", ".join(concepts_subset)
        text_chunk = text[:1000] if len(text) > 1000 else text
        
        prompt = f"""Given these concepts: {concepts_str}

Analyze the following text and identify relationships between the concepts.
List relationships in the format: "concept1 -> concept2 (relationship_type)"

Use relationship types like: related_to, causes, uses, part_of, influences, implements

Text: {text_chunk}

Relationships:"""
        
        try:
            result = self.hf_pipeline(prompt, max_length=150, do_sample=False)
            relationships_text = result[0]['generated_text'] if result else ""
            
            relationships = []
            if relationships_text:
                lines = relationships_text.split('\n')
                for line in lines:
                    if '->' in line and '(' in line:
                        try:
                            parts = line.split('->')
                            source = parts[0].strip()
                            target_and_type = parts[1].strip()
                            
                            if '(' in target_and_type:
                                target = target_and_type.split('(')[0].strip()
                                rel_type = target_and_type.split('(')[1].split(')')[0].strip()
                                
                                # Validate that concepts exist in our list
                                source_concept = self._find_matching_concept(source, concepts)
                                target_concept = self._find_matching_concept(target, concepts)
                                
                                if source_concept and target_concept and source_concept != target_concept:
                                    relationships.append((source_concept, target_concept, rel_type))
                        except:
                            continue
            
            # If HF didn't find many relationships, supplement with rule-based
            if len(relationships) < 2:
                rule_based_rels = self.extract_relationships_rule_based(text, concepts)
                relationships.extend(rule_based_rels)
                # Remove duplicates
                relationships = list(set(relationships))
            
            return relationships
            
        except Exception as e:
            print(f"Hugging Face relationship extraction error: {e}, falling back to rule-based")
            return self.extract_relationships_rule_based(text, concepts)
    
    def extract_concepts_openai(self, text: str) -> List[str]:
        """
        Extract important concepts using OpenAI API.
        Generalized for any domain.
        
        Args:
            text: Input text
            
        Returns:
            List of extracted concepts
        """
        if self.model_type != "openai":
            return self.extract_concepts_rule_based(text)
        
        prompt = f"""
        Extract the most important concepts and key terms from the following text. 
        Focus on identifying:
        - Main topics and subjects
        - Important technical terms and terminology
        - Key entities, people, organizations, or proper nouns
        - Significant processes, methods, or procedures
        - Core ideas and themes
        
        Return only the concept names, one per line, without explanations.
        
        Text: {text[:2000]}  # Limit text length
        
        Important concepts:
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying important concepts and key terms from any text. Extract the most significant concepts without explanations."},
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
        Generalized for any domain.
        
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
        Given the following text and list of concepts, identify relationships between the concepts.
        Focus on relationships like:
        - is_type_of, part_of, contains
        - uses, implements, applies
        - causes, influences, affects
        - related_to, associated_with
        - depends_on, builds_on
        
        Return relationships in the format: "source_concept -> target_concept (relationship_type)"
        
        Concepts: {concepts_str}
        
        Text: {text[:1500]}
        
        Relationships:
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at identifying relationships between concepts in any domain. Focus on clear, meaningful relationships."},
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
        Process a page (Wikipedia or uploaded document) to extract concepts and relationships.
        Generalized for any domain.
        
        Args:
            page_data: Page data with title, content, summary
            
        Returns:
            Dictionary with extracted concepts and relationships
        """
        title = page_data.get('title', '')
        content = page_data.get('content', '')
        summary = page_data.get('summary', '')
        
        # Combine summary and first part of content for processing
        text_to_process = f"{summary}\n\n{content[:3000]}"
        
        # Extract concepts based on model type
        if self.model_type == "openai":
            concepts = self.extract_concepts_openai(text_to_process)
        elif self.model_type == "huggingface":
            concepts = self.extract_concepts_huggingface(text_to_process)
        else:
            concepts = self.extract_concepts_rule_based(text_to_process)
        
        # Add the page title as a concept if not already present
        title_in_concepts = any(title.lower() == concept.lower() for concept in concepts)
        if title and not title_in_concepts:
            concepts.insert(0, title)
        
        # Extract relationships based on model type
        if self.model_type == "openai":
            relationships = self.extract_relationships_openai(text_to_process, concepts)
        elif self.model_type == "huggingface":
            relationships = self.extract_relationships_huggingface(text_to_process, concepts)
        else:
            relationships = self.extract_relationships_rule_based(text_to_process, concepts)
        
        return {
            'title': title,
            'concepts': concepts,
            'relationships': relationships,
            'original_data': page_data
        }


if __name__ == "__main__":
    # Example usage with generalized concept extraction
    extractor = ConceptExtractor(model_type="rule_based")
    
    # Example 1: Technical/Scientific text
    sample_text_science = """
    Artificial intelligence (AI) is intelligence demonstrated by machines, in contrast to 
    natural intelligence displayed by humans and animals. Leading AI textbooks define the 
    field as the study of "intelligent agents": any device that perceives its environment 
    and takes actions that maximize its chance of successfully achieving its goals. Machine 
    learning is a subset of AI that uses statistical techniques to give computers the ability 
    to learn from data without being explicitly programmed. Deep learning is a subset of 
    machine learning that uses neural networks with multiple layers.
    """
    
    # Example 2: Business text
    sample_text_business = """
    Digital transformation is the process of using digital technologies to create new or 
    modify existing business processes, culture, and customer experiences to meet changing 
    business and market requirements. This involves the integration of digital technology 
    into all areas of a business, fundamentally changing how you operate and deliver value 
    to customers. Cloud computing enables businesses to access computing resources on-demand, 
    reducing infrastructure costs and improving scalability.
    """
    
    print("=== Science/Tech Text Analysis ===")
    concepts1 = extractor.extract_concepts_rule_based(sample_text_science)
    print(f"Extracted concepts: {concepts1}")
    relationships1 = extractor.extract_relationships_rule_based(sample_text_science, concepts1)
    print(f"Extracted relationships: {relationships1}")
    
    print("\n=== Business Text Analysis ===")
    concepts2 = extractor.extract_concepts_rule_based(sample_text_business)
    print(f"Extracted concepts: {concepts2}")
    relationships2 = extractor.extract_relationships_rule_based(sample_text_business, concepts2)
    print(f"Extracted relationships: {relationships2}")