# Deployment Guide

## Stap 1: GitHub Repository Aanmaken

1. Ga naar https://github.com/PGEnvironment
2. Klik op "New repository"
3. Naam: `sinterklaas-gedicht-generator`
4. Maak repository aan (public of private)
5. Kopieer de repository URL

## Stap 2: Code naar GitHub Pushen

```bash
git remote add origin https://github.com/PGEnvironment/sinterklaas-gedicht-generator.git
git branch -M main
git push -u origin main
```

## Stap 3: Backend Deployen op Render

De backend wordt automatisch gedeployed zodra de GitHub repo is gekoppeld.

**Render Web Service Configuratie:**
- Name: `sinterklaas-poem-backend`
- Runtime: Node
- Build Command: `npm install`
- Start Command: `node server.js`
- Environment: Production
- Plan: Starter (gratis)

**Na deployment krijg je een URL zoals:**
`https://sinterklaas-poem-backend.onrender.com`

## Stap 4: Frontend Deployen op Netlify

**Optie A: Via Git (aanbevolen)**
1. Netlify → New site from Git
2. Kies GitHub → `sinterklaas-gedicht-generator`
3. Build settings:
   - Build command: (leeg - geen build nodig)
   - Publish directory: `/` (root)
4. Environment variables:
   - `BACKEND_URL`: De Render backend URL
   - `WEBHOOK_URL`: `https://dev.promptgorillas.com/webhook/receive_message`

**Optie B: Manual Deploy**
1. Netlify → New site → Deploy manually
2. Upload de `index.html` file
3. Voeg environment variables toe zoals hierboven

## Stap 5: Frontend Configuratie Aanpassen

Na deployment, update `index.html` met de juiste URLs of gebruik Netlify's environment variables injection.

Voor Netlify, voeg dit toe aan het begin van `index.html` (vóór de script tag):

```html
<script>
    window.BACKEND_URL = 'https://sinterklaas-poem-backend.onrender.com';
    window.WEBHOOK_URL = 'https://dev.promptgorillas.com/webhook/receive_message';
</script>
```

## n8n Flow 2 URLs

Update je n8n Flow 2 met deze URLs:

**Stap 2 - Status "generating":**
```
POST https://sinterklaas-poem-backend.onrender.com/status/generating
```

**Stap 4 - Status "completed":**
```
POST https://sinterklaas-poem-backend.onrender.com/status/completed
```

