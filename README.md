# Sinterklaas Gedicht Generator

Een AI-powered Sinterklaas gedicht generator met real-time status updates via Server-Sent Events (SSE).

## Architectuur

- **Frontend**: HTML/CSS/JavaScript met SSE voor real-time updates
- **Backend**: Node.js/Express server voor SSE en status endpoints
- **n8n**: Automatisering workflows voor agent en gedicht generatie

## Setup

### Backend Server

1. Installeer dependencies:
```bash
npm install
```

2. Configureer environment variables (optioneel):
```bash
PORT=3000
HOST=0.0.0.0
```

3. Start de server:
```bash
npm start
# of voor development:
npm run dev
```

De server draait standaard op poort 3000.

### Frontend

De frontend is een statische HTML file. Configureer de backend URL door `window.BACKEND_URL` te setten vóór het laden van de pagina:

```html
<script>
    window.BACKEND_URL = 'https://your-backend-url.com';
    window.WEBHOOK_URL = 'https://your-n8n-webhook-url.com/webhook/receive_message';
</script>
<script src="index.html"></script>
```

Of pas de defaults aan in `index.html`:
```javascript
const CONFIG = {
    BACKEND_URL: window.BACKEND_URL || 'https://your-backend-url.com',
    WEBHOOK_URL: window.WEBHOOK_URL || 'https://your-n8n-webhook-url.com/webhook/receive_message'
};
```

## n8n Flow Setup

### Flow 1: Agent Flow (blijft hetzelfde)
- Ontvangt chat berichten via webhook
- Stelt vragen en verzamelt informatie
- Roept Flow 2 aan als tool wanneer klaar

### Flow 2: Gedicht Generator Flow

**Stap 1: When Executed by Another Workflow**
- Ontvangt session_id en verzamelde data

**Stap 2: HTTP Request - Status "generating"**
- URL: `POST https://your-backend-url.com/status/generating`
- Body:
```json
{
  "session_id": "{{ $json.session_id }}"
}
```

**Stap 3: LLM Node**
- Genereer het gedicht met alle verzamelde informatie

**Stap 4: HTTP Request - Status "completed"**
- URL: `POST https://your-backend-url.com/status/completed`
- Body:
```json
{
  "session_id": "{{ $json.session_id }}",
  "poem": "{{ $json.generated_poem }}"
}
```

### Flow 3: Word Document Generator Flow

**Stap 1: Webhook**
- Ontvangt `session_id` en `poem` van frontend

**Stap 2: LLM Node**
- Converteer gedicht naar JSON structuur met velden:
  - `voornaam`: Voornaam van de ontvanger
  - `session_id`: Session ID
  - `rijm`: Het gedicht met behoud van formatting (witregels en enters)

**Stap 3: HTTP Request - Generate Word**
- URL: `POST https://your-backend-url.com/generate-word`
- Body:
```json
{
  "voornaam": "{{ $json.voornaam }}",
  "session_id": "{{ $json.session_id }}",
  "rijm": "{{ $json.rijm }}"
}
```

**Stap 4: Respond to Webhook**
- Stuur het Word bestand terug naar de frontend
- Option 1: Direct file response (set Content-Type header)
- Option 2: Base64 encoded in JSON:
```json
{
  "file_data": "base64_encoded_file_content",
  "file_name": "sinterklaas_gedicht_{session_id}.docx"
}
```

## API Endpoints

### SSE Stream
```
GET /stream/:session_id
```
Frontend connecteert hier voor real-time updates.

### Status Updates (voor n8n)
```
POST /status/generating
Body: { "session_id": "..." }
```

```
POST /status/completed
Body: { "session_id": "...", "poem": "..." }
```

### Word Document Generation
```
POST /generate-word
Body: { 
  "voornaam": "...",
  "session_id": "...",
  "rijm": "..." 
}
Response: Word document (.docx file)
```

### Health Check
```
GET /health
```

## Deployment

### Backend op Render/Heroku/etc.

1. Maak een nieuwe web service
2. Set build command: `npm install`
3. Set start command: `npm start`
4. Set environment variables:
   - `PORT` (optioneel, defaults naar 3000)
   - `HOST` (optioneel, defaults naar 0.0.0.0)

### Frontend op Netlify

1. Upload `index.html` en andere statische bestanden
2. In de HTML, voeg script toe voor configuratie:
```html
<script>
    window.BACKEND_URL = 'https://your-backend-url.com';
</script>
```

Of gebruik Netlify's environment variables en inject via build script.

## Environment Variables

### Backend
- `PORT`: Server poort (default: 3000)
- `HOST`: Server host (default: 0.0.0.0)

### Frontend (via window object)
- `BACKEND_URL`: Backend API base URL
- `WEBHOOK_URL`: n8n webhook URL voor chat

## Flow Diagram

```
User → Frontend (SSE) → Backend Server
                          ↑
                          |
n8n Flow 2 → HTTP POST → Status Updates
```

## Troubleshooting

- **SSE connection fails**: Check CORS settings en backend URL
- **Status updates niet ontvangen**: Check of session_id correct wordt doorgegeven
- **Poem niet getoond**: Check backend logs en n8n flow logs
