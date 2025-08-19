# 📋 Render Deployment Checklist

Use this checklist to ensure successful deployment of Auto-KG on Render.

## Pre-Deployment

- [ ] GitHub account set up
- [ ] Render account created (free tier available)
- [ ] Repository forked (if using your own copy)
- [ ] On `render-deploy` branch

## Render Setup

- [ ] Connected GitHub account to Render
- [ ] Created new Blueprint in Render
- [ ] Selected correct repository and `render-deploy` branch
- [ ] Blueprint deployment initiated

## Environment Configuration

### Web Service (`auto-kg-web`)
- [ ] `NEO4J_PASSWORD` set (strong password)
- [ ] `NEO4J_USER` set to `neo4j`
- [ ] `NEO4J_URI` set to `bolt://auto-kg-neo4j:7687`
- [ ] `PYTHON_VERSION` set to `3.11`

### Neo4j Service (`auto-kg-neo4j`)
- [ ] `NEO4J_AUTH` set to `neo4j/same-password-as-above`
- [ ] Memory settings configured
- [ ] Persistent disk attached

## Verification

- [ ] Both services show "Live" status
- [ ] Web service accessible via provided URL
- [ ] Health check endpoint responds: `/api/health`
- [ ] Main interface loads without errors
- [ ] Sample data visible in the graph
- [ ] Can upload and process documents

## Optional Enhancements

- [ ] Custom domain configured
- [ ] GitHub Pages frontend set up
- [ ] API endpoints tested
- [ ] Database backup strategy planned

## Troubleshooting Completed

- [ ] Checked service logs for errors
- [ ] Verified environment variables
- [ ] Confirmed both services are running
- [ ] Tested database connectivity

## Success Indicators

✅ Application loads successfully
✅ Knowledge graph displays
✅ File upload works
✅ API endpoints respond
✅ No critical errors in logs

---

**Need help?** Check [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md) for detailed instructions.