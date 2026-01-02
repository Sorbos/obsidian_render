# Deploy to Render

This guide shows how to deploy your Obsidian MCP Server to Render for public access.

## 🚀 Quick Deploy

### Option 1: GitHub + Render Dashboard

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/obsidian-mcp-server.git
   git push -u origin main
   ```

2. **Deploy on Render**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Render will auto-detect Python and use the settings below

### Option 2: Render Blueprint (render.yaml)

1. **Push to GitHub** (same as above)
2. **Deploy with Blueprint**:
   - Go to [render.com](https://render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repo
   - Render will use the `render.yaml` configuration

## ⚙️ Manual Configuration

If auto-detection doesn't work, use these settings:

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python mcp-server.py --http`
- **Environment**: `Python 3`
- **Health Check Path**: `/health`

## 🔐 Environment Variables

Set these in Render's dashboard:

| Variable | Value | Notes |
|----------|-------|-------|
| `sb_url` | `https://your-project.supabase.co` | Your Supabase URL |
| `sb_api` | `your_supabase_secret_key` | Your Supabase secret key |
| `secret_api_key` | `any_random_string` | For FastAPI security |

## 🌐 After Deployment

1. **Get your URL**: Render will give you a URL like:
   ```
   https://obsidian-mcp-server.onrender.com
   ```

2. **Test the deployment**:
   ```bash
   curl https://your-app.onrender.com/health
   ```

3. **Update Le Chat configuration**:
   ```json
   {
     "mcpServers": {
       "obsidian-notes": {
         "url": "https://your-app.onrender.com/mcp/message",
         "disabled": false
       }
     }
   }
   ```

## 💡 Benefits of Render Deployment

- ✅ **Public Access**: Le Chat can reach your server from anywhere
- ✅ **Always On**: No need to keep your local machine running
- ✅ **Free Tier**: Render offers generous free hosting
- ✅ **Auto-Deploy**: Updates when you push to GitHub
- ✅ **HTTPS**: Secure connection out of the box

## 🔧 Troubleshooting

### Server Won't Start
- Check environment variables are set correctly
- Verify Supabase credentials
- Check Render logs for errors

### Can't Connect to Database
- Ensure `sb_url` and `sb_api` are correct
- Test Supabase connection locally first
- Check Supabase project is active

### MCP Requests Fail
- Verify the URL ends with `/mcp/message`
- Check server logs in Render dashboard
- Test with curl or Postman first

## 📊 Monitoring

- **Render Dashboard**: View logs, metrics, and deployments
- **Health Check**: Visit `/health` endpoint
- **Supabase Dashboard**: Monitor database usage

Your MCP server will be publicly accessible and ready for Le Chat!