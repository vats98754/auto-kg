// Knowledge Graph Visualization with D3.js

class KnowledgeGraph {
    constructor() {
        this.svg = d3.select("#knowledge-graph");
        this.width = window.innerWidth * 0.7;
        this.height = window.innerHeight - 200;
        
        this.svg.attr("width", this.width).attr("height", this.height);
        
        this.g = this.svg.append("g");
        
        // Add zoom behavior
        this.zoom = d3.zoom()
            .scaleExtent([0.1, 3])
            .on("zoom", (event) => {
                this.g.attr("transform", event.transform);
            });
            
        this.svg.call(this.zoom);
        
        // Force simulation
        this.simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(d => d.id).distance(80))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(this.width / 2, this.height / 2))
            .force("collision", d3.forceCollide().radius(30));
        
        this.nodes = [];
        this.links = [];
        
        this.init();
    }
    
    init() {
        // Load initial data
        this.loadGraphData();
        this.loadStats();
        this.setupEventListeners();
    }
    
    async loadGraphData() {
        try {
            const response = await fetch('/api/graph');
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.nodes = data.nodes || [];
            this.links = data.edges || [];
            
            this.updateVisualization();
            
            document.getElementById('loading').style.display = 'none';
            
        } catch (error) {
            console.error('Error loading graph data:', error);
            document.getElementById('loading').textContent = 'Error loading graph data: ' + error.message;
        }
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            this.displayStats(stats);
            
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    displayStats(stats) {
        const statsContent = document.getElementById('stats-content');
        
        let html = `
            <div class="stat-item">
                <span class="stat-label">Concepts:</span>
                <span>${stats.concept_count || 0}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Relationships:</span>
                <span>${stats.relationship_count || 0}</span>
            </div>
        `;
        
        if (stats.most_connected && stats.most_connected.length > 0) {
            html += '<h4>Most Connected:</h4>';
            stats.most_connected.slice(0, 5).forEach(([concept, connections]) => {
                html += `
                    <div class="stat-item">
                        <span>${concept}</span>
                        <span>${connections}</span>
                    </div>
                `;
            });
        }
        
        statsContent.innerHTML = html;
    }
    
    updateVisualization() {
        // Clear existing elements
        this.g.selectAll("*").remove();
        
        if (this.nodes.length === 0) {
            return;
        }
        
        // Create links
        const link = this.g.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(this.links)
            .enter().append("line")
            .attr("class", "link")
            .attr("stroke-width", d => Math.sqrt(1));
        
        // Create nodes
        const node = this.g.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(this.nodes)
            .enter().append("circle")
            .attr("class", "node")
            .attr("r", d => Math.max(8, Math.min(20, (d.categories?.length || 1) * 3 + 8)))
            .attr("fill", d => this.getNodeColor(d))
            .call(d3.drag()
                .on("start", (event, d) => this.dragstarted(event, d))
                .on("drag", (event, d) => this.dragged(event, d))
                .on("end", (event, d) => this.dragended(event, d)));
        
        // Add labels
        const label = this.g.append("g")
            .attr("class", "labels")
            .selectAll("text")
            .data(this.nodes)
            .enter().append("text")
            .attr("class", "node-label")
            .attr("dy", "0.35em")
            .text(d => d.label.length > 15 ? d.label.substring(0, 15) + "..." : d.label);
        
        // Add click events
        node.on("click", (event, d) => this.showConceptDetails(d));
        
        // Add hover effects
        node.on("mouseover", (event, d) => this.highlightNode(d))
            .on("mouseout", () => this.clearHighlight());
        
        // Update simulation
        this.simulation
            .nodes(this.nodes)
            .on("tick", () => {
                link
                    .attr("x1", d => d.source.x)
                    .attr("y1", d => d.source.y)
                    .attr("x2", d => d.target.x)
                    .attr("y2", d => d.target.y);
                
                node
                    .attr("cx", d => d.x)
                    .attr("cy", d => d.y);
                
                label
                    .attr("x", d => d.x)
                    .attr("y", d => d.y);
            });
        
        this.simulation.force("link").links(this.links);
        this.simulation.alpha(1).restart();
    }
    
    getNodeColor(node) {
        // Color nodes based on categories or other properties
        const colors = {
            'algebra': '#ff6b6b',
            'geometry': '#4ecdc4',
            'analysis': '#45b7d1',
            'topology': '#96ceb4',
            'statistics': '#ffeaa7',
            'probability': '#dda0dd',
            'calculus': '#98d8c8',
            'theory': '#a8e6cf'
        };
        
        if (node.categories && node.categories.length > 0) {
            const category = node.categories[0].toLowerCase();
            for (const [key, color] of Object.entries(colors)) {
                if (category.includes(key)) {
                    return color;
                }
            }
        }
        
        return '#667eea'; // Default color
    }
    
    async showConceptDetails(node) {
        const detailsPanel = document.getElementById('concept-details');
        
        try {
            const response = await fetch(`/api/concept/${encodeURIComponent(node.id)}`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            const concept = data.concept;
            const related = data.related;
            
            let html = `
                <div class="concept-info">
                    <div class="concept-title">${concept.title}</div>
                    <div class="concept-summary">${concept.summary || 'No summary available'}</div>
                    ${concept.url ? `<a href="${concept.url}" target="_blank" class="concept-url">View on Wikipedia</a>` : ''}
                </div>
            `;
            
            if (related && related.length > 0) {
                html += '<div class="related-concepts"><h4>Related Concepts:</h4>';
                related.forEach(rel => {
                    html += `
                        <div class="related-concept" onclick="graph.focusOnNode('${rel.concept.title}')">
                            ${rel.concept.title} (${rel.relationship_type})
                        </div>
                    `;
                });
                html += '</div>';
            }
            
            detailsPanel.innerHTML = `<h3>Concept Details</h3>${html}`;
            
        } catch (error) {
            detailsPanel.innerHTML = `<h3>Concept Details</h3><p>Error loading concept details: ${error.message}</p>`;
        }
    }
    
    focusOnNode(nodeId) {
        const node = this.nodes.find(n => n.id === nodeId);
        if (node) {
            // Center the view on the node
            const transform = d3.zoomIdentity
                .translate(this.width / 2 - node.x, this.height / 2 - node.y)
                .scale(1.5);
            
            this.svg.transition()
                .duration(750)
                .call(this.zoom.transform, transform);
            
            this.showConceptDetails(node);
        }
    }
    
    highlightNode(node) {
        // Highlight the node and its connections
        this.g.selectAll(".node")
            .classed("highlighted", d => d.id === node.id);
        
        this.g.selectAll(".link")
            .classed("highlighted", d => d.source.id === node.id || d.target.id === node.id);
    }
    
    clearHighlight() {
        this.g.selectAll(".node").classed("highlighted", false);
        this.g.selectAll(".link").classed("highlighted", false);
    }
    
    async search(query) {
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            this.displaySearchResults(data.results);
            
        } catch (error) {
            console.error('Error searching:', error);
        }
    }
    
    displaySearchResults(results) {
        const resultsPanel = document.getElementById('search-results');
        const resultsList = document.getElementById('results-list');
        
        if (results.length === 0) {
            resultsList.innerHTML = '<p>No results found</p>';
        } else {
            let html = '';
            results.forEach(result => {
                html += `
                    <div class="search-result" onclick="graph.focusOnNode('${result.title}')">
                        <strong>${result.title}</strong>
                        <p>${(result.summary || '').substring(0, 100)}...</p>
                    </div>
                `;
            });
            resultsList.innerHTML = html;
        }
        
        resultsPanel.style.display = 'block';
    }
    
    // Drag functions
    dragstarted(event, d) {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    dragended(event, d) {
        if (!event.active) this.simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
    
    resetView() {
        this.svg.transition()
            .duration(750)
            .call(this.zoom.transform, d3.zoomIdentity);
    }
}

// Initialize the application
let graph;

document.addEventListener('DOMContentLoaded', function() {
    graph = new KnowledgeGraph();
    
    // Setup event listeners
    document.getElementById('searchBtn').addEventListener('click', function() {
        const query = document.getElementById('searchInput').value;
        if (query.trim()) {
            graph.search(query);
        }
    });
    
    document.getElementById('searchInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const query = this.value;
            if (query.trim()) {
                graph.search(query);
            }
        }
    });
    
    document.getElementById('resetBtn').addEventListener('click', function() {
        graph.resetView();
    });
    
    document.getElementById('shareBtn').addEventListener('click', function() {
        // Generate a shareable URL
        const shareUrl = window.location.origin + '/share/' + Date.now();
        navigator.clipboard.writeText(shareUrl).then(() => {
            alert('Share URL copied to clipboard: ' + shareUrl);
        });
    });
    
    document.getElementById('statsBtn').addEventListener('click', function() {
        graph.loadStats();
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        graph.width = window.innerWidth * 0.7;
        graph.height = window.innerHeight - 200;
        graph.svg.attr("width", graph.width).attr("height", graph.height);
        graph.simulation.force("center", d3.forceCenter(graph.width / 2, graph.height / 2));
        graph.simulation.alpha(0.3).restart();
    });
});