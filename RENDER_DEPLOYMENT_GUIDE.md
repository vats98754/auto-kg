# 🚀 Complete Render Deployment Guide for Auto-KG

This guide provides step-by-step instructions to deploy the Auto-KG (Automatic Knowledge Graph Builder) application on Render for **completely free**.

## 📋 Prerequisites

- GitHub account
- Render account (free tier available at [render.com](https://render.com))
- Basic understanding of environment variables

## 🎯 What You'll Deploy

Auto-KG consists of two main components:
1. **Flask Web Application** - The main app with API and web interface
2. **Neo4j Database** - Graph database for storing knowledge relationships

Both will run on Render's free tier with automatic HTTPS and persistent storage.

## 📦 Deployment Options

### Option 1: Quick Deploy (Recommended)
Use this branch directly for instant deployment.

### Option 2: Fork and Deploy
Fork this repository to your GitHub account for customization.

## 🚀 Step-by-Step Deployment Instructions

### Step 1: Prepare Your Repository

1. **Fork this repository** (if you haven't already):
   - Go to https://github.com/vats98754/auto-kg
   - Click "Fork" in the top right
   - Select your GitHub account

2. **Switch to the deployment branch**:
   ```bash
   git checkout render-deploy
   ```

### Step 2: Deploy to Render

1. **Sign up/Login to Render**:
   - Go to [render.com](https://render.com)
   - Sign up with GitHub (recommended for easy repo access)

2. **Create New Blueprint**:
   - Click "New +" → "Blueprint"
   - Connect your GitHub account if not already connected
   - Select your forked `auto-kg` repository
   - Make sure to select the `render-deploy` branch
   - Click "Connect"

3. **Render will automatically detect the `render.yaml` file and create**:
   - `auto-kg-web` - Your main web application
   - `auto-kg-neo4j` - Neo4j database service

### Step 3: Configure Environment Variables

1. **Set up the Web Service**:
   - Go to your `auto-kg-web` service in Render dashboard
   - Click "Environment" tab
   - Add these environment variables:

   ```env
   NEO4J_PASSWORD=your-secure-password-here
   NEO4J_USER=neo4j
   NEO4J_URI=bolt://auto-kg-neo4j:7687
   PYTHON_VERSION=3.11
   ```

   > 🔒 **Security Note**: Choose a strong password for `NEO4J_PASSWORD`

2. **Set up the Neo4j Service**:
   - Go to your `auto-kg-neo4j` service
   - Click "Environment" tab
   - Add this environment variable:

   ```env
   NEO4J_AUTH=neo4j/your-secure-password-here
   ```

   > ⚠️ **Important**: Use the SAME password in both services!

### Step 4: Deploy and Verify

1. **Trigger Deployment**:
   - Both services should start building automatically
   - Web service build time: ~3-5 minutes
   - Neo4j service build time: ~2-3 minutes

2. **Check Service Status**:
   - Both services should show "Live" status when ready
   - Web service will have a public URL like: `https://auto-kg-web-xxxx.onrender.com`

3. **Test Your Deployment**:
   - Click on the web service URL
   - You should see the Auto-KG interface
   - The app will work with fallback data initially

## 🔧 Post-Deployment Configuration

### Load Initial Data

Your app starts with sample data, but you can load fresh Wikipedia data:

1. **Using the Web Interface**:
   - Go to your deployed app URL
   - Use the "Upload Document" feature to add custom content
   - Or use the existing mathematical concepts data

2. **Using API Endpoints** (Optional):
   - `POST /api/scrape` - Trigger Wikipedia scraping
   - `GET /api/health` - Check service health
   - `GET /api/concepts` - View loaded concepts

### Enable GitHub Pages (Optional)

For a static frontend experience:

1. **Configure API Base**:
   - Edit `docs/index.html`
   - Replace `REPLACE_WITH_RENDER_URL` with your Render service URL

2. **Enable GitHub Pages**:
   - Go to your GitHub repo settings
   - Navigate to "Pages" section
   - Select source: "Deploy from a branch"
   - Choose branch: `render-deploy`
   - Choose folder: `/docs`

## 💰 Free Tier Limitations

Render's free tier includes:
- ✅ 750 hours/month of runtime
- ✅ Automatic HTTPS
- ✅ Custom domains
- ✅ 1GB persistent disk for Neo4j
- ⚠️ Services sleep after 15 minutes of inactivity
- ⚠️ Cold start delay (~30 seconds) when waking up

## 🔍 Troubleshooting

### Common Issues

1. **Service Won't Start**:
   - Check environment variables are set correctly
   - Ensure passwords match between services
   - Check build logs for errors

2. **Database Connection Failed**:
   - Verify `NEO4J_URI` points to `bolt://auto-kg-neo4j:7687`
   - Confirm `NEO4J_AUTH` format: `neo4j/password`
   - Check both services are running

3. **Slow First Load**:
   - This is normal on free tier (cold start)
   - Subsequent requests will be faster
   - Consider upgrading to paid tier for instant response

### Getting Help

1. **Check Service Logs**:
   - Go to Render dashboard
   - Click on the problematic service
   - Check "Logs" tab for error messages

2. **Health Check**:
   - Visit: `https://your-service-url.onrender.com/api/health`
   - Should return JSON with service status

3. **GitHub Issues**:
   - Report problems at: https://github.com/vats98754/auto-kg/issues

## 🎉 Success!

Your Auto-KG application is now live and accessible worldwide! You can:

- ✅ Build knowledge graphs from Wikipedia data
- ✅ Upload custom documents for analysis
- ✅ Visualize concept relationships
- ✅ Share your graphs with others
- ✅ Scale up to paid tier when needed

## 📚 Next Steps

1. **Customize the Data**: Upload your own documents
2. **Explore the API**: Build custom integrations
3. **Monitor Usage**: Keep track of your free tier limits
4. **Upgrade When Ready**: Move to paid tier for production use

---

## 🤝 Contributing

Found an issue with deployment? Help improve this guide:
1. Fork the repository
2. Make your improvements
3. Submit a pull request

## 📄 License

This project is open source. See LICENSE file for details.

---

**Happy Knowledge Graphing! 🧠📊**