# 🌐 Auto-KG Render Deployment Branch

**Ready-to-deploy branch for hosting Auto-KG on Render (100% free)**

> ⚠️ **Important**: This is the deployment branch. For development and main project documentation, see the [main branch](https://github.com/vats98754/auto-kg/tree/main).

## 🚀 One-Click Deployment

This branch is optimized for Render deployment. Everything is pre-configured for you!

### Quick Deploy Steps:

1. **Fork this repository** to your GitHub account
2. **Switch to this branch** (`render-deploy`)
3. **Deploy to Render**:
   - Create account at [render.com](https://render.com)
   - Connect GitHub account
   - Create "New Blueprint"
   - Point to your forked repo, branch: `render-deploy`
   - Configure environment variables (see guide below)

4. **Or follow the detailed manual steps** in our [Complete Deployment Guide](./RENDER_DEPLOYMENT_GUIDE.md)

## 📋 What's Included

- ✅ **Pre-configured services**: Web app + Neo4j database  
- ✅ **Free tier optimized**: Runs entirely on Render's free plan
- ✅ **Sample data included**: Mathematical concepts knowledge graph
- ✅ **Auto-scaling**: Handles traffic spikes automatically
- ✅ **HTTPS enabled**: Secure by default
- ✅ **Persistent storage**: Database data survives restarts

## 🎯 Features

- **Interactive Knowledge Graph Visualization**: Explore mathematical concepts and their relationships
- **Document Upload**: Create custom knowledge graphs from your documents  
- **Wikipedia Integration**: Scrape and process Wikipedia articles
- **Multi-format Support**: TXT, PDF, DOC, DOCX files
- **Responsive Design**: Works on desktop and mobile
- **API Access**: Programmatic access to graph data

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [📖 RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md) | **Complete deployment guide** (start here) |
| [✅ DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) | **Step-by-step checklist** |
| [🔧 ENV_TEMPLATE.md](./ENV_TEMPLATE.md) | **Environment variables template** |
| [🚀 README_DEPLOY.md](./README_DEPLOY.md) | Technical deployment details |

## 💰 Cost Breakdown

**Total Monthly Cost: $0** (Free Tier)

| Service | Type | Cost | Limits |
|---------|------|------|--------|
| Web App | Free Tier | $0 | 750 hours/month |
| Neo4j Database | Free Tier | $0 | 1GB storage |
| Domain | Provided | $0 | .onrender.com subdomain |
| HTTPS | Included | $0 | Automatic SSL |

## 🆘 Need Help?

1. **Start here**: [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md)
2. **Check troubleshooting**: See guide for common issues
3. **Report issues**: [GitHub Issues](https://github.com/vats98754/auto-kg/issues)

## 🔧 Development

This is the deployment branch. For development, see the main branch:
- Main project: [main branch](https://github.com/vats98754/auto-kg/tree/main)
- Development setup: [Main README](https://github.com/vats98754/auto-kg/blob/main/README.md)

## 📊 Architecture

```
┌─────────────────┐    ┌─────────────────┐
│   Render Web    │    │   Render Neo4j  │
│   (Flask App)   │◄──►│   (Database)    │
│                 │    │                 │
│ • UI/API        │    │ • Graph Storage │
│ • File Upload   │    │ • Persistence   │  
│ • Processing    │    │ • Bolt Protocol │
└─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│     Users       │
│                 │
│ • Web Interface │
│ • API Access    │
│ • File Upload   │
└─────────────────┘
```

## 🎉 Success Stories

After deployment, you'll have:
- ✅ Live web application with custom domain
- ✅ Automatic HTTPS security
- ✅ Scalable knowledge graph database
- ✅ File upload and processing capabilities
- ✅ API endpoints for integration
- ✅ Interactive graph visualization

---

**Ready to deploy? Start with [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md)**

## 📄 License

This project is open source. See LICENSE file for details.

---

**Happy Knowledge Graphing! 🧠📊**