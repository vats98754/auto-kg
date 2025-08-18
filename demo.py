#!/usr/bin/env python3
"""
Demo version of Auto-KG that works without Neo4j database.
Shows the web interface with sample data.
"""

import json
import os
from pathlib import Path
import sys

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from flask import Flask, render_template, jsonify, request
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from auto_kg.utils.sample_data import generate_sample_math_data


def create_demo_app():
    """Create a demo Flask application with sample data."""
    if not FLASK_AVAILABLE:
        print("Flask not available. Install with: pip install flask flask-cors")
        return None
    
    # Set template and static folder paths
    template_dir = project_root / 'auto_kg' / 'web' / 'templates'
    static_dir = project_root / 'auto_kg' / 'web' / 'static'
    
    app = Flask(__name__, 
                template_folder=str(template_dir),
                static_folder=str(static_dir))
    CORS(app)
    
    # Generate sample data
    sample_data = generate_sample_math_data()
    
    # Convert to graph format
    nodes = []
    edges = []
    
    for title, data in sample_data.items():
        nodes.append({
            'id': title,
            'label': title,
            'summary': data['summary'],
            'url': data['url'],
            'categories': data['categories']
        })
        
        # Create edges from links
        for link in data['links']:
            if link in sample_data:
                edges.append({
                    'source': title,
                    'target': link,
                    'relationship_type': 'RELATES_TO',
                    'properties': {}
                })
    
    graph_data = {'nodes': nodes, 'edges': edges}
    
    @app.route('/')
    def index():
        """Main page with knowledge graph visualization."""
        return render_template('index.html')
    
    @app.route('/api/graph')
    def get_graph():
        """API endpoint to get the full knowledge graph data."""
        return jsonify(graph_data)
    
    @app.route('/api/concept/<concept_name>')
    def get_concept(concept_name):
        """API endpoint to get details about a specific concept."""
        if concept_name in sample_data:
            concept_data = sample_data[concept_name]
            
            # Find related concepts
            related = []
            for link in concept_data['links']:
                if link in sample_data:
                    related.append({
                        'concept': {
                            'title': link,
                            'summary': sample_data[link]['summary']
                        },
                        'relationship_type': 'RELATES_TO',
                        'relationship_props': {}
                    })
            
            return jsonify({
                'concept': {
                    'title': concept_data['title'],
                    'summary': concept_data['summary'],
                    'url': concept_data['url'],
                    'categories': concept_data['categories']
                },
                'related': related
            })
        else:
            return jsonify({'error': 'Concept not found'}), 404
    
    @app.route('/api/search')
    def search_concepts():
        """API endpoint to search for concepts."""
        query = request.args.get('q', '').lower()
        limit = int(request.args.get('limit', 10))
        
        results = []
        for title, data in sample_data.items():
            if query in title.lower() or query in data['summary'].lower():
                results.append({
                    'title': title,
                    'summary': data['summary'],
                    'url': data['url']
                })
                if len(results) >= limit:
                    break
        
        return jsonify({'results': results})
    
    @app.route('/api/stats')
    def get_stats():
        """API endpoint to get graph statistics."""
        stats = {
            'concept_count': len(nodes),
            'relationship_count': len(edges),
            'relationship_types': {'RELATES_TO': len(edges)},
            'most_connected': [(node['label'], len([e for e in edges if e['source'] == node['id'] or e['target'] == node['id']])) for node in nodes[:5]]
        }
        return jsonify(stats)
    
    return app


def main():
    """Run the demo application."""
    if not FLASK_AVAILABLE:
        print("❌ Flask is required for the web demo")
        print("Install with: pip install flask flask-cors")
        return
    
    app = create_demo_app()
    if app:
        print("🚀 Starting Auto-KG Demo Application")
        print("📊 Using sample mathematical concepts data")
        print("🌐 Open http://localhost:5000 to view the knowledge graph")
        print("⚠️  This is a demo version - install Neo4j for full functionality")
        print()
        
        port = 5000
        app.run(host='0.0.0.0', port=port, debug=True)


if __name__ == '__main__':
    main()