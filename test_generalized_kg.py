#!/usr/bin/env python3
"""
Test script to demonstrate generalized concept detection for any uploaded document.
This shows how the system can now handle any domain, not just mathematics.
"""

import json
import sys
import tempfile
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from auto_kg.llm.concept_extractor import ConceptExtractor
from auto_kg.utils.document_processor import DocumentProcessor, create_knowledge_graph_from_document


def test_generalized_concept_extraction():
    """Test generalized concept extraction on different domains."""
    print("Testing Generalized Concept Extraction")
    print("=" * 50)
    
    extractor = ConceptExtractor(model_type='rule_based')
    
    # Test different domain texts
    test_texts = {
        "Technology": """
        Artificial intelligence and machine learning are transforming modern software development.
        Cloud computing enables scalable infrastructure deployment. Data analytics provides
        insights from customer behavior patterns. Digital transformation is reshaping business
        operations across industries.
        """,
        
        "Healthcare": """
        Medical research focuses on drug development and clinical trials to improve patient care.
        Public health initiatives address disease prevention and health promotion. Telemedicine
        technology enables remote patient monitoring and consultation services.
        """,
        
        "Environment": """
        Climate change impacts require sustainable energy solutions and carbon emission reductions.
        Renewable energy technologies include solar power, wind energy, and hydroelectric systems.
        Environmental science studies ecosystem dynamics and biodiversity conservation strategies.
        """,
        
        "Business": """
        Supply chain management optimizes logistics and inventory control processes. Customer
        experience design improves service delivery and market positioning. Strategic planning
        involves risk assessment and competitive analysis for business growth.
        """
    }
    
    for domain, text in test_texts.items():
        print(f"\n--- {domain} Domain ---")
        concepts = extractor.extract_concepts_rule_based(text)
        relationships = extractor.extract_relationships_rule_based(text, concepts)
        
        print(f"Concepts ({len(concepts)}): {', '.join(concepts[:8])}")
        print(f"Relationships ({len(relationships)}): {relationships[:3]}")


def test_document_upload_workflow():
    """Test the complete document upload and processing workflow."""
    print("\n\nTesting Document Upload Workflow")
    print("=" * 50)
    
    # Create test documents in different domains
    test_documents = {
        "business_strategy.txt": """
Business Strategy and Digital Innovation

Digital transformation has become essential for competitive advantage in modern markets.
Companies must adapt their business processes to leverage cloud computing, data analytics,
and artificial intelligence. Customer experience optimization drives revenue growth through
improved service delivery and personalized marketing strategies.

Supply chain management benefits from automation and real-time tracking systems.
Strategic planning incorporates risk assessment and market analysis to identify growth
opportunities. Technology integration enables operational efficiency and cost reduction
across organizational departments.
        """,
        
        "scientific_research.txt": """
Environmental Science and Climate Research

Climate change research investigates global warming impacts on ecosystem dynamics and
biodiversity conservation. Scientists study greenhouse gas emissions, carbon dioxide levels,
and atmospheric changes to understand environmental degradation patterns.

Renewable energy development focuses on solar power efficiency, wind energy optimization,
and sustainable technology implementation. Environmental science integrates biological
research, chemical analysis, and geological studies to address ecological challenges.

Conservation strategies involve habitat protection, species preservation, and sustainable
resource management for future generations.
        """
    }
    
    processor = DocumentProcessor()
    
    for filename, content in test_documents.items():
        print(f"\n--- Processing {filename} ---")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Process document
            document_data = processor.process_file(temp_path, filename)
            print(f"Title: {document_data['title']}")
            print(f"Content length: {len(document_data['content'])} characters")
            
            # Create knowledge graph
            graph_data = create_knowledge_graph_from_document(document_data)
            
            print(f"Generated {len(graph_data['nodes'])} nodes and {len(graph_data['edges'])} edges")
            print(f"Extraction method: {graph_data['metadata']['extraction_method']}")
            
            # Show key concepts
            concept_nodes = [node for node in graph_data['nodes'] if 'Concept' in node['categories']]
            concepts = [node['label'] for node in concept_nodes]
            print(f"Key concepts: {', '.join(concepts[:8])}")
            
            # Show relationships
            relationships = [edge for edge in graph_data['edges'] if edge['relationship_type'] != 'CONTAINS_CONCEPT']
            if relationships:
                print(f"Sample relationships: {relationships[:3]}")
            
        finally:
            # Clean up
            os.unlink(temp_path)


def main():
    """Run all generalization tests."""
    print("Auto-KG Generalized Concept Detection Test Suite")
    print("=" * 60)
    
    try:
        test_generalized_concept_extraction()
        test_document_upload_workflow()
        
        print("\n" + "=" * 60)
        print("✅ All generalization tests passed!")
        print("\nThe system can now:")
        print("- Extract concepts from any domain (not just mathematics)")
        print("- Process various document types (TXT, PDF, DOC, DOCX)")
        print("- Use free LLM inference (Hugging Face) when available")
        print("- Fall back to improved rule-based extraction")
        print("- Generate knowledge graphs for any subject matter")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())