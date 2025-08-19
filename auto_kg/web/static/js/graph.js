// Knowledge Graph Visualization with Cytoscape.js

class KnowledgeGraph {
    constructor() {
    this.container = document.getElementById('knowledge-graph');
    this.width = Math.max(600, window.innerWidth * 0.7);
    this.height = Math.max(400, window.innerHeight - 180);

        this.nodes = [];
        this.links = [];
    this.cy = null;
        
        this.init();
    }
    
    init() {
        // Load initial data
        this.loadGraphData();
        this.loadStats();
    }
    
    async loadGraphData() {
        try {
            const base = window.API_BASE || '';
            const response = await fetch(`${base}/api/graph`);
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
            const base = window.API_BASE || '';
            const response = await fetch(`${base}/api/stats`);
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
        if (!this.nodes || this.nodes.length === 0) return;
        
        // Check if Cytoscape is available
        if (typeof cytoscape === 'undefined') {
            console.warn('Cytoscape.js not available, using D3.js fallback');
            this.updateVisualizationD3();
            return;
        }
        
        const elements = [];
        const nodeSet = new Set();
        this.nodes.forEach(n => {
            const size = Math.max(10, Math.min(25, ((n.categories || []).length + 1) * 4 + 8));
            const color = this.getNodeColor(n);
            elements.push({ data: { id: n.id, label: n.label, url: n.url, summary: n.summary, categories: n.categories, size, color }, classes: 'concept' });
            nodeSet.add(n.id);
        });
        this.links.forEach(e => {
            const sid = e.source?.id || e.source;
            const tid = e.target?.id || e.target;
            if (sid && tid && nodeSet.has(sid) && nodeSet.has(tid)) {
                const type = e.relationship_type || 'RELATES_TO';
                elements.push({ data: { id: `${sid}->${tid}-${type}`, source: sid, target: tid, type }, classes: 'rel' });
            }
        });
        if (this.cy) { this.cy.destroy(); }
        this.cy = cytoscape({
            container: this.container,
            elements,
            style: [
                { selector: 'node', style: {
                    'background-color': 'data(color)',
                    'label': 'data(label)',
                    'color': '#e5e7ef',
                    'font-size': '10px',
                    'text-outline-color': '#0b0e1a',
                    'text-outline-width': 2,
                    'width': 'data(size)',
                    'height': 'data(size)',
                    'text-valign': 'center',
                    'text-halign': 'center'
                }},
                { selector: 'edge', style: {
                    'width': 1.5,
                    'line-color': '#39406a',
                    'target-arrow-color': '#39406a',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier'
                }},
                { selector: '.highlighted', style: {
                    'line-color': '#4fd1c5',
                    'target-arrow-color': '#4fd1c5'
                }}
            ],
            layout: { 
                name: 'cose', 
                padding: 50, 
                nodeRepulsion: 12000, 
                idealEdgeLength: 100, 
                edgeElasticity: 0.15, 
                gravity: 1.2, 
                numIter: 600, 
                initialTemp: 150,
                coolingFactor: 0.95,
                minTemp: 1.0
            }
        });

        this.cy.on('tap', 'node', evt => {
            const d = evt.target.data();
            this.showConceptDetails(d);
        });
    }

    updateVisualizationD3() {
        // D3.js fallback visualization
        const container = d3.select("#knowledge-graph");
        container.selectAll("*").remove();
        
        const width = this.width;
        const height = this.height;
        
        const svg = container.append("svg")
            .attr("width", width)
            .attr("height", height)
            .style("background", "transparent");
        
        const g = svg.append("g");
        
        // Add zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 3])
            .on("zoom", (event) => {
                g.attr("transform", event.transform);
            });
        svg.call(zoom);
        
        // Create force simulation
        const simulation = d3.forceSimulation(this.nodes)
            .force("link", d3.forceLink(this.links).id(d => d.id).distance(80))
            .force("charge", d3.forceManyBody().strength(-200))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(20));
        
        // Create links
        const link = g.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(this.links)
            .enter().append("line")
            .attr("stroke", "#39406a")
            .attr("stroke-opacity", 0.7)
            .attr("stroke-width", 1.2);
        
        // Create nodes
        const node = g.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(this.nodes)
            .enter().append("circle")
            .attr("r", d => Math.max(10, Math.min(25, ((d.categories || []).length + 1) * 4 + 8)))
            .attr("fill", d => this.getNodeColor(d))
            .attr("stroke", "#0b0e1a")
            .attr("stroke-width", 2)
            .style("filter", "drop-shadow(0 2px 4px rgba(0,0,0,0.35))")
            .style("cursor", "pointer")
            .call(d3.drag()
                .on("start", (event, d) => this.dragstarted(event, d))
                .on("drag", (event, d) => this.dragged(event, d))
                .on("end", (event, d) => this.dragended(event, d)));
        
        // Add labels
        const label = g.append("g")
            .attr("class", "labels")
            .selectAll("text")
            .data(this.nodes)
            .enter().append("text")
            .text(d => d.label.length > 12 ? d.label.substring(0, 12) + "..." : d.label)
            .attr("font-size", "10px")
            .attr("fill", "#e5e7ef")
            .attr("text-anchor", "middle")
            .attr("dy", "0.35em")
            .style("text-shadow", "0 0 3px #0b0e1a, 0 0 3px #0b0e1a")
            .style("pointer-events", "none");
        
        // Add click events
        node.on("click", (event, d) => this.showConceptDetails(d));
        
        // Add hover effects
        node.on("mouseover", (event, d) => this.highlightNodeD3(d))
            .on("mouseout", () => this.clearHighlightD3());
        
        // Update positions on simulation tick
        simulation.on("tick", () => {
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
        
        // Store references for later use
        this.d3Svg = svg;
        this.d3Simulation = simulation;
        this.d3Nodes = node;
        this.d3Links = link;
        this.d3Labels = label;
        
        document.getElementById('loading').style.display = 'none';
    }
    
    highlightNodeD3(node) {
        if (!this.d3Nodes) return;
        this.d3Nodes.style("opacity", d => d.id === node.id ? 1 : 0.3);
        this.d3Links.style("opacity", d => d.source.id === node.id || d.target.id === node.id ? 1 : 0.1);
        this.d3Labels.style("opacity", d => d.id === node.id ? 1 : 0.3);
    }
    
    clearHighlightD3() {
        if (!this.d3Nodes) return;
        this.d3Nodes.style("opacity", 1);
        this.d3Links.style("opacity", 0.7);
        this.d3Labels.style("opacity", 1);
    }
    
    // Drag functions for D3
    dragstarted(event, d) {
        if (!event.active && this.d3Simulation) this.d3Simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    
    dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    
    dragended(event, d) {
        if (!event.active && this.d3Simulation) this.d3Simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    mergeGraphData(data, replace = true) {
        // Optionally replace current data or merge new data into existing graph
        if (replace) {
            this.nodes = data.nodes || [];
            this.links = data.edges || [];
            return;
        }
        const nodeIndex = new Map(this.nodes.map(n => [n.id, n]));
        (data.nodes || []).forEach(n => { if (!nodeIndex.has(n.id)) { this.nodes.push(n); nodeIndex.set(n.id, n); } });
        const linkKey = (e) => `${e.source}-${e.target}-${e.relationship_type}`;
        const existing = new Set(this.links.map(e => linkKey({source: e.source?.id || e.source, target: e.target?.id || e.target, relationship_type: e.relationship_type})));
        (data.edges || []).forEach(e => {
            const k = linkKey(e);
            if (!existing.has(k)) this.links.push(e);
        });
    }

    async loadSubgraph(root, depth = 2) {
        const base = window.API_BASE || '';
        const res = await fetch(`${base}/api/subgraph?root=${encodeURIComponent(root)}&depth=${depth}`);
        const data = await res.json();
        if (data.error) throw new Error(data.error);
    // Sanitize edges relative to nodes
    const nodeIds = new Set((data.nodes || []).map(n => n.id));
    data.edges = (data.edges || []).filter(e => nodeIds.has(e.source?.id || e.source) && nodeIds.has(e.target?.id || e.target));
    this.mergeGraphData(data, true);
        this.updateVisualization();
        const details = document.getElementById('concept-details');
        details.innerHTML = `<h3>Concept Details</h3><p>Loaded subgraph rooted at <strong>${root}</strong> (depth ${depth}). Nodes: ${this.nodes.length}, Edges: ${this.links.length}.</p>`;
    }

    async loadShortestPath(source, target, maxDepth = 6) {
        const base = window.API_BASE || '';
        const res = await fetch(`${base}/api/path?source=${encodeURIComponent(source)}&target=${encodeURIComponent(target)}&max_depth=${maxDepth}`);
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        this.mergeGraphData(data, true);
        this.updateVisualization();
        const ps = document.getElementById('pathSummary');
        const pathLen = (data.edges || []).length;
        ps.innerHTML = pathLen > 0 ? `Found path with ${pathLen} steps.` : 'No path found.';
    }
    
    getNodeColor(node) {
        // Color nodes based on categories or other properties
        const colors = {
            'algebra': '#ff9f7a',
            'geometry': '#4fd1c5',
            'analysis': '#7aa2f7',
            'topology': '#a77bf3',
            'statistics': '#f6d365',
            'probability': '#f78fb3',
            'calculus': '#9ceab3',
            'theory': '#c3aed6'
        };
        
        if (node.categories && node.categories.length > 0) {
            const category = node.categories[0].toLowerCase();
            for (const [key, color] of Object.entries(colors)) {
                if (category.includes(key)) {
                    return color;
                }
            }
        }
        
    return '#7aa2f7'; // Default color
    }
    
    async showConceptDetails(node) {
        const detailsPanel = document.getElementById('concept-details');
        
        try {
            const base = window.API_BASE || '';
            const response = await fetch(`${base}/api/concept/${encodeURIComponent(node.id)}`);
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
    
    async focusOnNode(nodeId) {
        if (!this.nodes.find(n => n.id === nodeId)) {
            try { await this.loadSubgraph(nodeId, 2); } catch(e) { /* ignore */ }
        }
        
        if (this.cy) {
            const ele = this.cy.getElementById(nodeId);
            if (ele && ele.length > 0) {
                this.cy.animate({ center: { eles: ele }, zoom: 1.2 }, { duration: 450 });
                this.showConceptDetails(ele.data());
                this.highlightNode(nodeId);
            }
        } else if (this.d3Simulation) {
            // D3 focus implementation
            const node = this.nodes.find(n => n.id === nodeId);
            if (node) {
                this.showConceptDetails(node);
                this.highlightNodeD3(node);
            }
        }
    }
    
    highlightNode(nodeId) {
        if (this.cy) {
            this.cy.elements().removeClass('highlighted');
            const n = this.cy.getElementById(nodeId);
            n.addClass('highlighted');
            n.connectedEdges().addClass('highlighted');
        } else {
            // D3 highlighting handled in highlightNodeD3
            const node = this.nodes.find(n => n.id === nodeId);
            if (node) this.highlightNodeD3(node);
        }
    }
    
    clearHighlight() {
        if (this.cy) {
            this.cy.elements().removeClass('highlighted');
        } else {
            this.clearHighlightD3();
        }
    }
    
    async search(query) {
        try {
            const base = window.API_BASE || '';
            const response = await fetch(`${base}/api/search?q=${encodeURIComponent(query)}`);
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
    
    // Drag is built-in for Cytoscape
    
    resetView() {
        if (this.cy) {
            this.cy.fit(undefined, 40);
        } else if (this.d3Svg) {
            // Reset D3 zoom
            this.d3Svg.transition()
                .duration(750)
                .call(d3.zoom().transform, d3.zoomIdentity);
        }
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

    // Analysis inputs
    const subBtn = document.getElementById('subgraphBtn');
    if (subBtn) {
        subBtn.addEventListener('click', () => {
            document.getElementById('subgraphRoot').focus();
        });
    }
    const runSubgraph = document.getElementById('runSubgraph');
    if (runSubgraph) {
        runSubgraph.addEventListener('click', async () => {
            const root = document.getElementById('subgraphRoot').value.trim();
            const depth = parseInt(document.getElementById('subgraphDepth').value || '2', 10);
            if (!root) return;
            try { await graph.loadSubgraph(root, depth); } catch (e) { alert(e.message); }
        });
    }

    const pathBtn = document.getElementById('pathBtn');
    if (pathBtn) {
        pathBtn.addEventListener('click', () => {
            document.getElementById('pathSource').focus();
        });
    }
    const runPath = document.getElementById('runPath');
    if (runPath) {
        runPath.addEventListener('click', async () => {
            const src = document.getElementById('pathSource').value.trim();
            const tgt = document.getElementById('pathTarget').value.trim();
            if (!src || !tgt) return;
            try { await graph.loadShortestPath(src, tgt); } catch (e) { alert(e.message); }
        });
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (graph && graph.cy) {
            graph.cy.resize();
        } else if (graph && graph.d3Svg) {
            // Update D3 dimensions
            const newWidth = Math.max(600, window.innerWidth * 0.7);
            const newHeight = Math.max(400, window.innerHeight - 180);
            graph.d3Svg.attr("width", newWidth).attr("height", newHeight);
            if (graph.d3Simulation) {
                graph.d3Simulation.force("center", d3.forceCenter(newWidth / 2, newHeight / 2));
                graph.d3Simulation.alpha(0.3).restart();
            }
        }
    });

    // File upload functionality
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadStatus = document.getElementById('uploadStatus');
    let selectedFile = null;

    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // Drag and drop functionality
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#171c36';
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.style.background = '#12162b';
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.style.background = '#12162b';
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            selectedFile = files[0];
            updateUploadUI();
        }
    });

    // File selection
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            selectedFile = e.target.files[0];
            updateUploadUI();
        }
    });

    function updateUploadUI() {
        if (selectedFile) {
            uploadArea.querySelector('.upload-text').innerHTML = `
                <span>Selected: ${selectedFile.name}</span>
                <br>
                <small>Size: ${(selectedFile.size / 1024).toFixed(1)} KB</small>
            `;
            uploadBtn.disabled = false;
        }
    }

    // Upload button click
    uploadBtn.addEventListener('click', async () => {
        if (!selectedFile) return;

        uploadBtn.disabled = true;
        uploadStatus.innerHTML = '<span style="color: var(--primary);">Processing document...</span>';

        const formData = new FormData();
        formData.append('file', selectedFile);

        try {
            const base = window.API_BASE || '';
            const response = await fetch(`${base}/api/upload`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.error) {
                throw new Error(result.error);
            }

            uploadStatus.innerHTML = `<span style="color: var(--accent);">✓ Processed! Found ${result.concept_count} concepts and ${result.relationship_count} relationships</span>`;
            
            // Load the newly generated graph
            graph.mergeGraphData(result, true);
            graph.updateVisualization();

        } catch (error) {
            uploadStatus.innerHTML = `<span style="color: #ff6b6b;">Error: ${error.message}</span>`;
        } finally {
            uploadBtn.disabled = false;
        }
    });
});