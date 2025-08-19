"""
Flask web application for knowledge graph visualization.
Includes offline fallback when Neo4j is unavailable.
"""

from flask import Flask, render_template, jsonify, request, url_for
from flask_cors import CORS
import json
import os
from collections import deque, defaultdict
from typing import Dict, List, Set
from auto_kg.database.neo4j_manager import Neo4jKnowledgeGraph


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Initialize Neo4j connection
    kg = Neo4jKnowledgeGraph()

    # Optionally autoload data into Neo4j on first boot if DB is empty
    try:
        if getattr(kg, 'driver', None):
            with kg.driver.session() as session:
                count = session.run("MATCH (c:Concept) RETURN count(c) as n").single()["n"]
            autoload_flag = os.getenv('AUTO_KG_AUTOLOAD', 'true').lower() in ('1', 'true', 'yes')
            if autoload_flag and count == 0:
                processed_path = os.path.join(os.getcwd(), 'processed_concepts.json')
                raw_path = os.path.join(os.getcwd(), 'wikipedia_math_data.json')
                if os.path.exists(processed_path):
                    with open(processed_path, 'r', encoding='utf-8') as f:
                        pdata = json.load(f)
                    kg.load_processed_data(pdata)
                    print("Auto-loaded processed_concepts.json into Neo4j")
                elif os.path.exists(raw_path):
                    with open(raw_path, 'r', encoding='utf-8') as f:
                        wdata = json.load(f)
                    kg.load_wikipedia_data(wdata)
                    print("Auto-loaded wikipedia_math_data.json into Neo4j")
    except Exception as e:
        print(f"Autoload skipped due to error: {e}")

    # Offline data cache (populated if DB fails)
    app.config['OFFLINE_GRAPH'] = None
    app.config['OFFLINE_INDEX'] = None

    def build_offline_graph() -> Dict:
        """Build a graph from local JSON files when Neo4j is unavailable."""
        # Prefer processed concepts for richer relationships
        data = None
        processed_path = os.path.join(os.getcwd(), 'processed_concepts.json')
        raw_path = os.path.join(os.getcwd(), 'wikipedia_math_data.json')
        if os.path.exists(processed_path):
            with open(processed_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Build nodes and edges
            nodes = []
            edges = []
            node_map = {}
            adj = defaultdict(set)
            for title, item in data.items():
                orig = item.get('original_data', {})
                n = {
                    'id': str(title),
                    'label': str(title),
                    'summary': orig.get('summary', ''),
                    'url': orig.get('url', ''),
                    'categories': orig.get('categories', []),
                }
                nodes.append(n)
                node_map[str(title)] = n
            # relationships
            for title, item in data.items():
                title = str(title)
                for rel in item.get('relationships', []):
                    try:
                        src, tgt, rtype = rel
                    except Exception:
                        continue
                    src = str(src); tgt = str(tgt)
                    if src in node_map and tgt in node_map:
                        edges.append({'source': src, 'target': tgt, 'relationship_type': str(rtype).upper(), 'properties': {}})
                        adj[src].add(tgt); adj[tgt].add(src)
                # add LINKS_TO from original links if connectable
                for link in (item.get('original_data') or {}).get('links', []):
                    link = str(link)
                    if link in node_map:
                        edges.append({'source': title, 'target': link, 'relationship_type': 'LINKS_TO', 'properties': {}})
                        adj[title].add(link); adj[link].add(title)
            return {'nodes': nodes, 'edges': edges, 'adj': adj, 'map': node_map}
        elif os.path.exists(raw_path):
            with open(raw_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            nodes = []
            node_map = {}
            for title, page in data.items():
                n = {
                    'id': str(title),
                    'label': str(title),
                    'summary': page.get('summary', ''),
                    'url': page.get('url', ''),
                    'categories': page.get('categories', []),
                }
                nodes.append(n)
                node_map[str(title)] = n
            # Only keep edges where target exists (to avoid bloat)
            edges = []
            adj = defaultdict(set)
            for title, page in data.items():
                title = str(title)
                for link in page.get('links', []):
                    link = str(link)
                    if link in node_map and title in node_map:
                        edges.append({'source': title, 'target': link, 'relationship_type': 'LINKS_TO', 'properties': {}})
                        adj[title].add(link); adj[link].add(title)
            return {'nodes': nodes, 'edges': edges, 'adj': adj, 'map': node_map}
        else:
            return {'nodes': [], 'edges': [], 'adj': defaultdict(set), 'map': {}}

    def ensure_offline_graph():
        if app.config['OFFLINE_GRAPH'] is None:
            app.config['OFFLINE_GRAPH'] = build_offline_graph()
            # index for search
            idx = {}
            for n in app.config['OFFLINE_GRAPH']['nodes']:
                idx[n['id']] = n
            app.config['OFFLINE_INDEX'] = idx
        return app.config['OFFLINE_GRAPH']
    
    @app.route('/')
    def index():
        """Main page with knowledge graph visualization."""
        return render_template('index.html')
    
    @app.route('/api/graph')
    def get_graph():
        """API endpoint to get the full knowledge graph data."""
        try:
            graph_data = kg.export_graph_data()
            # Filter out edges that point to non-existent nodes
            nodes = graph_data.get('nodes', [])
            edges = graph_data.get('edges', [])
            node_ids = {n.get('id') for n in nodes}
            clean_edges = []
            for e in edges:
                s = e.get('source'); t = e.get('target')
                if isinstance(s, dict): s = s.get('id')
                if isinstance(t, dict): t = t.get('id')
                if s in node_ids and t in node_ids:
                    clean_edges.append(e)
            return jsonify({'nodes': nodes, 'edges': clean_edges})
        except Exception as e:
            # Fallback to offline data
            offline = ensure_offline_graph()
            return jsonify({'nodes': offline['nodes'], 'edges': offline['edges'], 'offline': True})
    
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
                # Fallback to offline
                offline = ensure_offline_graph()
                node = offline['map'].get(concept_name)
                if not node:
                    return jsonify({'error': 'Concept not found'}), 404
                # related via adjacency (undirected)
                related = []
                for neigh in offline['adj'].get(concept_name, []):
                    related.append({'concept': offline['map'].get(neigh, {'title': neigh}), 'relationship_type': 'RELATED', 'relationship_props': {}})
                return jsonify({'concept': {'title': node['id'], 'summary': node.get('summary',''), 'url': node.get('url',''), 'categories': node.get('categories',[])}, 'related': related})
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
            # Offline search
            offline = ensure_offline_graph()
            q = (query or '').lower().strip()
            hits = []
            for n in offline['nodes']:
                if q in n['id'].lower() or q in (n.get('summary','').lower()):
                    hits.append({'title': n['id'], 'summary': n.get('summary','')})
                    if len(hits) >= limit:
                        break
            return jsonify({'results': hits, 'offline': True})
    
    @app.route('/api/stats')
    def get_stats():
        """API endpoint to get graph statistics."""
        try:
            stats = kg.get_graph_stats()
            return jsonify(stats)
        except Exception as e:
            # Offline stats
            offline = ensure_offline_graph()
            concept_count = len(offline['nodes'])
            relationship_count = len(offline['edges'])
            # Basic degree
            deg = {n['id']: len(offline['adj'].get(n['id'], [])) for n in offline['nodes']}
            most_connected = sorted(deg.items(), key=lambda x: x[1], reverse=True)[:10]
            rel_types = defaultdict(int)
            for e in offline['edges']:
                rel_types[e.get('relationship_type','RELATES_TO')] += 1
            return jsonify({
                'concept_count': concept_count,
                'relationship_count': relationship_count,
                'relationship_types': rel_types,
                'most_connected': most_connected,
                'offline': True
            })

    @app.route('/api/subgraph')
    def get_subgraph():
        """API endpoint to get a subgraph around a root node."""
        root = request.args.get('root')
        depth = int(request.args.get('depth', 2))
        if not root:
            return jsonify({'error': 'Missing root parameter'}), 400
        try:
            data = kg.export_subgraph(root=root, depth=depth)
            # Sanitize edges
            node_ids = {n.get('id') for n in data.get('nodes', [])}
            clean_edges = []
            for e in data.get('edges', []):
                s = e.get('source'); t = e.get('target')
                if isinstance(s, dict): s = s.get('id')
                if isinstance(t, dict): t = t.get('id')
                if s in node_ids and t in node_ids:
                    clean_edges.append(e)
            return jsonify({'nodes': data.get('nodes', []), 'edges': clean_edges})
        except Exception as e:
            # Offline BFS subgraph (undirected)
            offline = ensure_offline_graph()
            adj = offline['adj']
            node_map = offline['map']
            if root not in node_map:
                # try case-insensitive match
                lower = root.lower()
                match = next((k for k in node_map if k.lower() == lower), None)
                if match is None:
                    return jsonify({'error': 'Root not found', 'suggestion': 'Check capitalization or search first'}), 404
                root = match
            max_depth = max(1, min(depth, 5))
            seen: Set[str] = set([root])
            q = deque([(root, 0)])
            nodes = []
            edges = []
            while q:
                cur, d = q.popleft()
                n = node_map[cur]
                nodes.append(n)
                if d == max_depth:
                    continue
                for nb in adj.get(cur, []):
                    if nb not in seen:
                        seen.add(nb)
                        q.append((nb, d+1))
                    # collect edges (undirected unique key)
                    edges.append({'source': cur, 'target': nb, 'relationship_type': 'RELATED', 'properties': {}})
            # Dedup edges
            uniq = {}
            for e in edges:
                a, b = e['source'], e['target']
                k = tuple(sorted([a, b]))
                if k not in uniq:
                    uniq[k] = e
            return jsonify({'nodes': nodes, 'edges': list(uniq.values()), 'offline': True})

    @app.route('/api/path')
    def get_path():
        """API endpoint to get shortest path between two concepts."""
        source = request.args.get('source')
        target = request.args.get('target')
        max_depth = int(request.args.get('max_depth', 6))
        if not source or not target:
            return jsonify({'error': 'Missing source or target parameter'}), 400
        try:
            data = kg.shortest_path(source=source, target=target, max_depth=max_depth)
            return jsonify(data)
        except Exception as e:
            # Offline BFS shortest path (undirected)
            offline = ensure_offline_graph()
            adj = offline['adj']
            node_map = offline['map']
            if source not in node_map or target not in node_map:
                return jsonify({'nodes': [], 'edges': [], 'offline': True})
            # BFS
            max_depth = max(1, min(max_depth, 10))
            prev = {source: None}
            q = deque([source])
            found = False
            depth_map = {source: 0}
            while q:
                cur = q.popleft()
                if depth_map[cur] >= max_depth:
                    continue
                for nb in adj.get(cur, []):
                    if nb not in prev:
                        prev[nb] = cur
                        depth_map[nb] = depth_map[cur] + 1
                        if nb == target:
                            found = True
                            q.clear()
                            break
                        q.append(nb)
            if not found:
                return jsonify({'nodes': [], 'edges': [], 'offline': True})
            # Reconstruct
            path = []
            cur = target
            while cur is not None:
                path.append(cur)
                cur = prev[cur]
            path.reverse()
            nodes = [node_map[n] for n in path]
            edges = []
            for i in range(len(path)-1):
                edges.append({'source': path[i], 'target': path[i+1], 'relationship_type': 'RELATED', 'properties': {}})
            return jsonify({'nodes': nodes, 'edges': edges, 'offline': True})

    @app.route('/api/health')
    def health():
        ok = bool(getattr(kg, 'driver', None))
        return jsonify({'neo4j': ok})
    
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