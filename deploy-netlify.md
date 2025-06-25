# 🎯 Netlify + Supabase Edge Functions (100% Free)

## ✅ Completely Free - No Credit Card!

This approach uses Netlify for frontend and Supabase Edge Functions for backend API.

## 🚀 Architecture
```
Frontend: Netlify (React app)
Backend:  Supabase Edge Functions (TypeScript/JavaScript)
Database: Supabase PostgreSQL (free tier)
```

## 📋 Setup Steps

### 1. Frontend on Netlify
```bash
# Connect GitHub repo to Netlify
# Build settings:
# - Build command: npm run build
# - Publish directory: dist
# - Base directory: react-app
```

### 2. Backend Migration to Supabase Edge Functions

Since Supabase Edge Functions run Deno (TypeScript/JavaScript), we need to create API endpoints:

#### Create `supabase/functions/chat/index.ts`:
```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const { message } = await req.json()
    
    // Your AI logic here using Groq API
    const groqResponse = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${Deno.env.get('GROQ_API_KEY')}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: 'mixtral-8x7b-32768',
        messages: [{ role: 'user', content: message }],
      }),
    })

    const data = await groqResponse.json()
    
    return new Response(
      JSON.stringify(data),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      },
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      { 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      },
    )
  }
})
```

### 3. Deploy Edge Functions
```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Deploy functions
supabase functions deploy chat
```

## 🌍 Environment Variables

### Netlify (Frontend):
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

### Supabase Edge Functions (Backend):
- `GROQ_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

## ✨ Advantages

### ✅ Cost
- **100% Free** - No credit card required
- **Generous limits** for both services

### ✅ Performance  
- **Global CDN** (Netlify)
- **Edge computing** (Supabase)
- **Fast cold starts**

### ✅ Scalability
- **Automatic scaling**
- **Pay-per-use** (but free tier covers most usage)

### ✅ Developer Experience
- **Git-based deployments**
- **Preview deployments**
- **Real-time logs**

## 🚀 Quick Start
1. Push code to GitHub
2. Connect Netlify to your repo
3. Set up Supabase project
4. Deploy Edge Functions
5. Configure environment variables

**Total setup time: ~15 minutes** 