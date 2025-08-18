"""
Flask web application for knowledge graph visualization.
"""

from flask import Flask, render_template, jsonify, request, url_for
from flask_cors import CORS
import json
import os
from auto_kg.database.neo4j_manager import Neo4jKnowledgeGraph


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Initialize Neo4j connection
    kg = Neo4jKnowledgeGraph()
    
    @app.route('/')
    def index():
        """Main page with knowledge graph visualization."""
        return render_template('index.html')
    
    @app.route('/api/graph')
    def get_graph():
        """API endpoint to get the full knowledge graph data."""
        try:
            graph_data = kg.export_graph_data()
            return jsonify(graph_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/concept/<concept_name>')
    def get_concept(concept_name):
        """API endpoint to get details about a specific concept."""
        try:
            concept = kg.get_concept(concept_name)
            if concept:
                related = kg.get_related_concepts(concept_name)
                return jsonify({
                    'concept': concept,
                    'related': related
                })
            else:
                return jsonify({'error': 'Concept not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/search')
    def search_concepts():
        """API endpoint to search for concepts."""
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))
        
        try:
            results = kg.search_concepts(query, limit)
            return jsonify({'results': results})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/stats')
    def get_stats():
        """API endpoint to get graph statistics."""
        try:
            stats = kg.get_graph_stats()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/share/<graph_id>')
    def share_graph(graph_id):
        """Share a specific view of the knowledge graph."""
        # For now, just redirect to main page
        # In a full implementation, this would load a specific saved graph state
        return render_template('index.html', shared_graph_id=graph_id)
    
    @app.teardown_appcontext
    def close_db(error):
        """Close database connection when app context ends."""
        if hasattr(kg, 'close'):
            kg.close()
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"Starting Auto-KG web application on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)