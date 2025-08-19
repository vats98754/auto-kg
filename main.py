#!/usr/bin/env python3
"""
Main CLI application for Auto-KG: Automatic Knowledge Graph Builder
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from auto_kg.scrapers.wikipedia_scraper import WikipediaMathScraper
from auto_kg.database.neo4j_manager import Neo4jKnowledgeGraph
from auto_kg.llm.concept_extractor import ConceptExtractor
from auto_kg.web.app import create_app


def scrape_wikipedia(args):
    """Scrape Wikipedia for mathematical concepts."""
    print("Starting Wikipedia scraping...")
    
    scraper = WikipediaMathScraper(
        language=args.language,
        max_pages=args.max_pages,
        max_depth=getattr(args, 'max_depth', 3),
        seed_topics=getattr(args, 'seed_topics', None)
    )
    
    # Scrape data
    scraped_data = scraper.scrape_mathematics_knowledge_graph()
    
    # Save to file
    output_file = args.output or "wikipedia_math_data.json"
    scraper.save_scraped_data(scraped_data, output_file)
    
    print(f"Scraping completed. Data saved to {output_file}")
    return scraped_data


def process_with_llm(args):
    """Process scraped data with LLM to extract concepts and relationships."""
    print("Processing data with LLM...")
    
    # Load scraped data
    input_file = args.input or "wikipedia_math_data.json"
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found")
        return None
    
    with open(input_file, 'r', encoding='utf-8') as f:
        wikipedia_data = json.load(f)
    
    # Initialize concept extractor
    extractor = ConceptExtractor(model_type=args.model_type)
    
    # Process each page
    processed_data = {}
    for title, page_data in wikipedia_data.items():
        print(f"Processing: {title}")
        processed_page = extractor.process_wikipedia_page(page_data)
        processed_data[title] = processed_page
    
    # Save processed data
    output_file = args.output or "processed_concepts.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    print(f"LLM processing completed. Data saved to {output_file}")
    return processed_data


def load_to_neo4j(args):
    """Load data into Neo4j database."""
    print("Loading data into Neo4j...")
    
    # Initialize Neo4j connection
    kg = Neo4jKnowledgeGraph()
    
    if not kg.driver:
        print("Error: Could not connect to Neo4j. Please check your configuration.")
        return
    
    # Load data file
    input_file = args.input or "wikipedia_math_data.json"
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found")
        return
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Clear database if requested
    if args.clear:
        print("Clearing existing database...")
        kg.clear_database()
    
    # Load data
    kg.load_wikipedia_data(data)
    
    # Show statistics
    stats = kg.get_graph_stats()
    print(f"Data loaded successfully!")
    print(f"Graph statistics: {stats}")
    
    kg.close()


def load_processed_to_neo4j(args):
    """Load processed concepts with relationships into Neo4j."""
    print("Loading processed data into Neo4j...")
    kg = Neo4jKnowledgeGraph()
    if not kg.driver:
        print("Error: Could not connect to Neo4j. Please check your configuration.")
        return
    input_file = args.input or "processed_concepts.json"
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found")
        return
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if args.clear:
        print("Clearing existing database...")
        kg.clear_database()
    kg.load_processed_data(data)
    stats = kg.get_graph_stats()
    print(f"Data loaded successfully! Graph statistics: {stats}")
    kg.close()


def run_web_app(args):
    """Run the web application."""
    print("Starting web application...")
    
    app = create_app()
    
    port = args.port or int(os.getenv('FLASK_PORT', 5000))
    debug = args.debug or os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Web application starting on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug)


def full_pipeline(args):
    """Run the full pipeline: scrape -> process -> load -> serve."""
    print("Running full Auto-KG pipeline...")
    
    # Step 1: Scrape Wikipedia
    print("\n=== Step 1: Scraping Wikipedia ===")
    scrape_args = argparse.Namespace(
        language=args.language,
        max_pages=args.max_pages,
    max_depth=args.max_depth,
    seed_topics=None,
        output="wikipedia_math_data.json"
    )
    scraped_data = scrape_wikipedia(scrape_args)
    
    # Step 2: Process with LLM (optional)
    if args.skip_llm:
        print("\n=== Step 2: Skipping LLM processing ===")
        processed_data = scraped_data
    else:
        print("\n=== Step 2: Processing with LLM ===")
        llm_args = argparse.Namespace(
            input="wikipedia_math_data.json",
            output="processed_concepts.json",
            model_type=args.model_type
        )
        processed_data = process_with_llm(llm_args)
    
    # Step 3: Load to Neo4j
    print("\n=== Step 3: Loading to Neo4j ===")
    if args.skip_llm:
        load_args = argparse.Namespace(
            input="wikipedia_math_data.json",
            clear=args.clear_db
        )
        load_to_neo4j(load_args)
    else:
        loadp_args = argparse.Namespace(
            input="processed_concepts.json",
            clear=args.clear_db
        )
        load_processed_to_neo4j(loadp_args)
    
    # Step 4: Start web app
    if args.serve:
        print("\n=== Step 4: Starting web application ===")
        web_args = argparse.Namespace(
            port=args.port,
            debug=args.debug
        )
        run_web_app(web_args)


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Auto-KG: Automatic Knowledge Graph Builder for Mathematics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scrape --max-pages 50                    # Scrape 50 Wikipedia pages
  %(prog)s process --input data.json                # Process with LLM
  %(prog)s load --input data.json --clear           # Load to Neo4j
  %(prog)s web --port 5000                          # Start web app
  %(prog)s full --max-pages 30 --serve              # Run full pipeline
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape Wikipedia for mathematical concepts')
    scrape_parser.add_argument('--language', default='en', help='Wikipedia language code (default: en)')
    scrape_parser.add_argument('--max-pages', type=int, default=100, help='Maximum pages to scrape (default: 100)')
    scrape_parser.add_argument('--max-depth', type=int, default=3, help='Maximum BFS depth (default: 3)')
    scrape_parser.add_argument('--seed-topics', nargs='*', help='Custom seed topics (space separated)')
    scrape_parser.add_argument('--output', help='Output JSON file (default: wikipedia_math_data.json)')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process data with LLM')
    process_parser.add_argument('--input', help='Input JSON file (default: wikipedia_math_data.json)')
    process_parser.add_argument('--output', help='Output JSON file (default: processed_concepts.json)')
    process_parser.add_argument('--model-type', choices=['openai', 'rule_based'], default='rule_based',
                               help='LLM model type (default: rule_based)')
    
    # Load command
    load_parser = subparsers.add_parser('load', help='Load raw scraped data into Neo4j')
    load_parser.add_argument('--input', help='Input JSON file (default: wikipedia_math_data.json)')
    load_parser.add_argument('--clear', action='store_true', help='Clear existing database')

    # Load processed command
    loadp_parser = subparsers.add_parser('load-processed', help='Load processed concepts (with relationships) into Neo4j')
    loadp_parser.add_argument('--input', help='Input JSON file (default: processed_concepts.json)')
    loadp_parser.add_argument('--clear', action='store_true', help='Clear existing database')
    
    # Web command
    web_parser = subparsers.add_parser('web', help='Start web application')
    web_parser.add_argument('--port', type=int, help='Port number (default: 5000)')
    web_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    # Full pipeline command
    full_parser = subparsers.add_parser('full', help='Run full pipeline')
    full_parser.add_argument('--language', default='en', help='Wikipedia language code (default: en)')
    full_parser.add_argument('--max-pages', type=int, default=50, help='Maximum pages to scrape (default: 50)')
    full_parser.add_argument('--max-depth', type=int, default=3, help='Maximum BFS depth (default: 3)')
    full_parser.add_argument('--model-type', choices=['openai', 'rule_based'], default='rule_based',
                            help='LLM model type (default: rule_based)')
    full_parser.add_argument('--skip-llm', action='store_true', help='Skip LLM processing')
    full_parser.add_argument('--clear-db', action='store_true', help='Clear existing database')
    full_parser.add_argument('--serve', action='store_true', help='Start web app after loading')
    full_parser.add_argument('--port', type=int, help='Web app port (default: 5000)')
    full_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute the appropriate command
    try:
        if args.command == 'scrape':
            scrape_wikipedia(args)
        elif args.command == 'process':
            process_with_llm(args)
        elif args.command == 'load':
            load_to_neo4j(args)
        elif args.command == 'load-processed':
            load_processed_to_neo4j(args)
        elif args.command == 'web':
            run_web_app(args)
        elif args.command == 'full':
            full_pipeline(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        if args.debug if hasattr(args, 'debug') else False:
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    main()