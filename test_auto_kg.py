#!/usr/bin/env python3
"""
Test script for Auto-KG functionality without external dependencies.
"""

import json
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from auto_kg.llm.concept_extractor import ConceptExtractor
from auto_kg.utils.sample_data import generate_sample_math_data


def test_concept_extraction():
    """Test the concept extraction functionality."""
    print("Testing concept extraction...")
    
    # Generate sample data
    sample_data = generate_sample_math_data()
    
    # Initialize concept extractor
    extractor = ConceptExtractor(model_type='rule_based')
    
    # Test with Linear Algebra page
    page_data = sample_data['Linear Algebra']
    result = extractor.process_wikipedia_page(page_data)
    
    print(f"✓ Processed page: {result['title']}")
    print(f"✓ Extracted {len(result['concepts'])} concepts")
    print(f"✓ Found {len(result['relationships'])} relationships")
    print(f"  Sample concepts: {result['concepts'][:3]}")
    
    return result


def test_sample_data_generation():
    """Test sample data generation."""
    print("Testing sample data generation...")
    
    data = generate_sample_math_data()
    
    print(f"✓ Generated {len(data)} mathematical concepts")
    print(f"✓ Topics: {list(data.keys())[:3]}...")
    
    # Save to file
    with open("test_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("✓ Saved test data to test_data.json")
    
    return data


def main():
    """Run all tests."""
    print("Auto-KG Test Suite")
    print("==================")
    
    try:
        # Test 1: Sample data generation
        test_sample_data_generation()
        print()
        
        # Test 2: Concept extraction
        test_concept_extraction()
        print()
        
        print("✅ All tests passed!")
        print("\nNext steps:")
        print("1. Install Neo4j database")
        print("2. Configure .env file with Neo4j credentials")
        print("3. Run: python main.py load --input test_data.json")
        print("4. Run: python main.py web")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()