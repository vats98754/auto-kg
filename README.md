# Auto-KG: Automatic Knowledge Graph Builder

This app automatically builds (via free locally-hosted LLM calls) and displays (via Neo4j) an interactive knowledge graph of all (inferred) relevant concepts from a set of documents. It's designed as a cool and efficient visualization and presentation tool for course notes, research, and educational purposes.

The initial implementation focuses on creating a comprehensive knowledge graph of mathematics by scraping data and relationships between mathematical topics from Wikipedia. Users can share links to their created knowledge graphs with others.

## Features

- **Wikipedia Scraping**: Automatically scrapes mathematical concepts from Wikipedia
- **LLM-Powered Concept Extraction**: Uses rule-based methods or OpenAI API to extract relationships
- **Neo4j Knowledge Graph**: Stores and queries the knowledge graph in Neo4j database
- **Interactive Web Visualization**: D3.js-powered interactive graph visualization
- **Sharing Capabilities**: Generate shareable links for knowledge graphs
- **Search Functionality**: Search and explore mathematical concepts
- **Real-time Statistics**: View graph statistics and most connected concepts

## Quick Start

### Prerequisites

- Python 3.8+
- Neo4j Database (or Docker)
- Optional: OpenAI API key for enhanced LLM processing

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd auto-kg
   ```

2. **Run the setup script:**
   ```bash
   ./setup.sh
   ```

3. **Configure your environment:**
   - Edit `.env` file with your Neo4j credentials
   - Optionally add OpenAI API key for enhanced processing

4. **Start Neo4j database:**
   ```bash
   # Using Docker (recommended)
   docker run -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest
   
   # Or start your local Neo4j installation
   neo4j start
   ```

5. **Run the full pipeline:**
   ```bash
   python main.py full --max-pages 20 --serve
   ```

6. **Open your browser** to `http://localhost:5000` to view the knowledge graph!

## Usage

### Command Line Interface

The application provides a comprehensive CLI for different operations:

```bash
# Scrape Wikipedia for mathematical concepts
python main.py scrape --max-pages 50 --language en

# Process scraped data with LLM
python main.py process --input wikipedia_math_data.json --model-type rule_based

# Load data into Neo4j
python main.py load --input wikipedia_math_data.json --clear

# Start the web application
python main.py web --port 5000

# Run the complete pipeline
python main.py full --max-pages 30 --serve --clear-db
```

### Web Interface

The web interface provides:

- **Interactive Graph Visualization**: Zoom, pan, and drag nodes
- **Concept Details**: Click on nodes to view detailed information
- **Search**: Find specific mathematical concepts
- **Graph Statistics**: View connection counts and graph metrics
- **Sharing**: Generate shareable URLs for specific graph views

## Configuration

Edit the `.env` file to configure:

```env
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# LLM Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-3.5-turbo

# Application Configuration
FLASK_PORT=5000
FLASK_DEBUG=True
MAX_WIKIPEDIA_PAGES=100
```

## Architecture

```
auto_kg/
├── scrapers/           # Wikipedia scraping functionality
├── llm/               # LLM integration for concept extraction
├── database/          # Neo4j database management
├── web/               # Flask web application
│   ├── templates/     # HTML templates
│   └── static/        # CSS/JS assets
└── utils/             # Utility functions
```

## Features in Detail

### Wikipedia Scraping
- Starts with seed mathematical topics
- Intelligently follows links to related mathematical concepts
- Extracts page content, categories, and relationships
- Rate-limited to be respectful to Wikipedia

### Concept Extraction
- **Rule-based**: Uses regex patterns to identify mathematical concepts and relationships
- **LLM-powered**: Optional OpenAI integration for enhanced concept extraction
- Identifies theorems, mathematical structures, and relationships

### Knowledge Graph Storage
- Neo4j database for efficient graph storage and querying
- Concept nodes with properties (title, summary, categories, URL)
- Relationship edges with types (relates_to, generalizes, etc.)
- Graph statistics and analytics

### Web Visualization
- D3.js force-directed graph layout
- Interactive nodes with hover and click behaviors
- Color-coded nodes by mathematical category
- Responsive design for different screen sizes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. See LICENSE file for details.

## Roadmap

- [ ] Support for additional data sources beyond Wikipedia
- [ ] Enhanced LLM integration with local models
- [ ] Graph analytics and insights
- [ ] Export functionality (PDF, images)
- [ ] Collaborative editing and sharing
- [ ] Plugin system for custom data processors

## Troubleshooting

### Common Issues

1. **Neo4j Connection Error**: Ensure Neo4j is running and credentials are correct in `.env`
2. **Wikipedia Rate Limiting**: Reduce `--max-pages` if encountering rate limits
3. **Memory Issues**: For large graphs, consider increasing available memory
4. **OpenAI API Errors**: Check API key and rate limits if using OpenAI integration

For more help, see the [documentation](docs/) or open an issue.
