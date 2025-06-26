# 🐙 GitHub Pages + Free Serverless Backend

## ✅ 100% Free - No Credit Card Ever!

Use GitHub Pages for frontend and free serverless platforms for backend.

## 🏗️ Architecture Options

### Option A: GitHub Pages + Vercel Functions
```
Frontend: GitHub Pages (React static site)
Backend:  Vercel Functions (Python/Node.js)
Database: Supabase (free PostgreSQL)
```

### Option B: GitHub Pages + Netlify Functions  
```
Frontend: GitHub Pages (React static site)
Backend:  Netlify Functions (Node.js)
Database: Supabase (free PostgreSQL)
```

### Option C: GitHub Pages + Deno Deploy
```
Frontend: GitHub Pages (React static site) 
Backend:  Deno Deploy (TypeScript)
Database: Supabase (free PostgreSQL)
```

## 🚀 Setup Guide

### 1. Frontend on GitHub Pages

#### Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy React App to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
      
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: |
        cd react-app
        npm install
        
    - name: Build
      run: |
        cd react-app
        npm run build
        
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./react-app/dist
```

### 2. Backend Options

#### Option A: Vercel Functions (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy backend only
cd backend
vercel

# Vercel auto-detects Python and creates serverless functions
```

#### Option B: Netlify Functions
```javascript
// netlify/functions/chat.js
exports.handler = async (event, context) => {
  const { message } = JSON.parse(event.body);
  
  // Call Groq API
  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.GROQ_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'mixtral-8x7b-32768',
      messages: [{ role: 'user', content: message }],
    }),
  });

  return {
    statusCode: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(await response.json()),
  };
};
```

#### Option C: Deno Deploy
```typescript
// main.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

serve(async (req) => {
  const { message } = await req.json();
  
  const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${Deno.env.get('GROQ_API_KEY')}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'mixtral-8x7b-32768',
      messages: [{ role: 'user', content: message }],
    }),
  });

  return new Response(await response.text(), {
    headers: { 'Content-Type': 'application/json' },
  });
});
```

## 🌍 Environment Variables

### GitHub Pages (Frontend):
- Set in repository secrets
- Access via build process

### Backend Platforms:
- **Vercel**: Set in dashboard
- **Netlify**: Set in dashboard  
- **Deno Deploy**: Set in dashboard

## ✨ Advantages

### ✅ Cost
- **GitHub Pages**: 100% free
- **Vercel Functions**: Generous free tier
- **Netlify Functions**: 125k requests/month free
- **Deno Deploy**: 100k requests/month free

### ✅ Reliability
- **GitHub's infrastructure**
- **Global CDN** for all platforms
- **99.9% uptime** guarantees

### ✅ No Vendor Lock-in
- **Standard web technologies**
- **Easy to migrate** between platforms
- **Full control** over code

## 🚀 Quick Start Commands

```bash
# 1. Enable GitHub Pages
# Go to Settings > Pages > Source: GitHub Actions

# 2. Push the workflow file
git add .github/workflows/deploy.yml
git commit -m "Add GitHub Pages deployment"
git push

# 3. Deploy backend to chosen platform
vercel  # or netlify deploy, or deno deploy
```

**Total cost: $0/month forever! 🎉** 