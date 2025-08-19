# Deploy Auto-KG (Web + Neo4j)

This project can run fully in Render (API + Neo4j) and be visualized from a static site (e.g., GitHub Pages) pointing to the API.

## 1) Deploy to Render

- Repo contains `render.yaml` and `Procfile`.
- Render will create two services:
  - `auto-kg-web` (Python/Flask via Gunicorn)
  - `auto-kg-neo4j` (Neo4j 5 Docker)

Steps:
1. Push to GitHub.
2. In Render, create "New +" → "Blueprint". Point to this repo. It will read `render.yaml`.
3. Set environment variables on `auto-kg-web`:
   - `NEO4J_PASSWORD` (required)
   - `NEO4J_URI=bolt://auto-kg-neo4j:7687` (already in blueprint)
   - `NEO4J_USER=neo4j`
4. On the Neo4j service, ensure `NEO4J_AUTH=neo4j/<same password>`.
5. Render will provision a disk for `/data` to persist DB.

If you want to pre-load processed data:
- Commit `processed_concepts.json` (already present).
- After deploy, hit the API endpoint you expose for loading (or run a one-off job). For now the web app can operate with the fallback offline graph too.

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
