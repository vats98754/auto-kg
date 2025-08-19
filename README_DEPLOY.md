# Deploy Auto-KG (Web + Neo4j)

**🚀 For detailed deployment instructions, see [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md)**

This project can run fully in Render (API + Neo4j) and be visualized from a static site (e.g., GitHub Pages) pointing to the API.

## Quick Start

1. **Use the `render-deploy` branch** for production deployment
2. **Follow the complete guide**: [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md)
3. **Deploy with one-click** using Render Blueprint

## 1) Deploy to Render

- Repo contains `render.yaml` and `Procfile`.
- Render will create two services:
  - `auto-kg-web` (Python/Flask via Gunicorn)
  - `auto-kg-neo4j` (Neo4j 5 Docker)

### Quick Steps:
1. Fork this repository and switch to `render-deploy` branch
2. In Render, create "New +" → "Blueprint". Point to your fork.
3. Set environment variables on `auto-kg-web`:
   - `NEO4J_PASSWORD` (choose a secure password)
   - `NEO4J_URI=bolt://auto-kg-neo4j:7687` (already in blueprint)
   - `NEO4J_USER=neo4j`
4. On the Neo4j service, ensure `NEO4J_AUTH=neo4j/<same password>`.
5. Render will provision a disk for `/data` to persist DB.

### Pre-loaded Data:
- The app includes `processed_concepts.json` with sample mathematical concepts
- After deployment, the app can operate with fallback offline graph data
- Use the web interface to upload custom documents or scrape new Wikipedia data

## 2) Host frontend on GitHub Pages

- The Flask app serves the UI, but you can also host the static front-end on GitHub Pages.
- In `auto_kg/web/templates/index.html`, set:

```html
<script>
  window.API_BASE = 'https://<your-render-service>.onrender.com';
</script>
```

- Commit and push to a `gh-pages` branch with the built/static assets, or keep using the Flask-served UI on Render.

## 3) Local development

- Run: `python3 main.py full --max-pages 100 --serve`
- UI served at http://localhost:5000
- Ensure Neo4j is running locally or the app will use the offline fallback.

## Notes
- GitHub Pages cannot host Neo4j; a server is required (Render service here).
- The UI now tolerates missing DB by using a local JSON fallback and sanitizing edges.
