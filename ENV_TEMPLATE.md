# Environment Variables Template for Render Deployment

## Web Service Environment Variables (auto-kg-web)

Copy these environment variables to your Render web service:

```env
# Database Connection
NEO4J_URI=bolt://auto-kg-neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=YOUR_SECURE_PASSWORD_HERE

# Python Configuration  
PYTHON_VERSION=3.11

# Optional: LLM Configuration (if using OpenAI features)
# OPENAI_API_KEY=your_openai_api_key_here

# Optional: Application Settings
# FLASK_ENV=production
# LOG_LEVEL=INFO
```

## Neo4j Service Environment Variables (auto-kg-neo4j)

Copy these environment variables to your Render Neo4j service:

```env
# Authentication (MUST match NEO4J_PASSWORD above)
NEO4J_AUTH=neo4j/YOUR_SECURE_PASSWORD_HERE

# Memory Configuration (optimized for free tier)
NEO4J_dbms_memory_heap_initial__size=256m
NEO4J_dbms_memory_heap_max__size=512m
NEO4J_dbms_memory_pagecache_size=128m

# Optional: Additional Neo4j Configuration
# NEO4J_dbms_default__listen__address=0.0.0.0
# NEO4J_dbms_connector_bolt_listen__address=0.0.0.0:7687
```

## Security Notes

1. **Password Requirements**:
   - Use a strong, unique password
   - Same password must be used in both services
   - Format for Neo4j: `neo4j/your_password`
   - Format for Web app: `your_password`

2. **Environment Variable Security**:
   - Never commit passwords to Git
   - Use Render's secure environment variable storage
   - Passwords are encrypted at rest in Render

## Example Configuration

```bash
# Example strong password
NEO4J_PASSWORD=AutoKG2024SecurePass!
NEO4J_AUTH=neo4j/AutoKG2024SecurePass!
```

## Validation

After setting environment variables:

1. **Check web service logs** for database connection success
2. **Visit health endpoint**: `https://your-app.onrender.com/api/health`
3. **Expected response**:
   ```json
   {
     "status": "healthy",
     "database": "connected",
     "services": "running"
   }
   ```

## Troubleshooting

### Common Issues:

1. **Database connection failed**:
   - Verify passwords match exactly
   - Check `NEO4J_URI` format
   - Ensure both services are running

2. **Service won't start**:
   - Check environment variable names (case sensitive)
   - Verify Python version compatibility
   - Review service build logs

3. **Authentication errors**:
   - Confirm `NEO4J_AUTH` format: `neo4j/password`
   - Ensure no extra spaces in password
   - Check special characters are URL-safe

---

**For complete setup instructions, see [RENDER_DEPLOYMENT_GUIDE.md](./RENDER_DEPLOYMENT_GUIDE.md)**