# 🤖 Chat Integratie Documentatie

## Overzicht
De Sinterklaas Gedichten Generator is nu volledig geïntegreerd met je n8n workflow via webhooks!

## 📋 Functionaliteit

### 1. **Chat Sessie Starten**
- Gebruiker klikt op "Start Chat Sessie" knop
- Er wordt automatisch een unieke `session_id` aangemaakt
- Format: `session_TIMESTAMP_RANDOM` (bijv. `session_1729756800000_abc123def`)
- De chat interface wordt geactiveerd

### 2. **Berichten Versturen**
Wanneer een gebruiker een bericht verstuurt:
- Het bericht wordt direct in de chat getoond
- Er wordt een POST request gestuurd naar je webhook

**Webhook URL**: `https://dev.promptgorillas.com/webhook-test/receive_message`

**Request Body**:
```json
{
  "message": "Het bericht van de gebruiker",
  "session_id": "session_1729756800000_abc123def"
}
```

### 3. **Antwoord Ontvangen**
Je n8n workflow moet antwoorden met deze JSON structuur:

**Response Format**:
```json
{
  "response": "Het antwoord van de AI assistent",
  "session_id": "session_1729756800000_abc123def"
}
```

- Het `response` veld wordt automatisch als bot-bericht getoond
- De `session_id` wordt gebruikt voor thread management
- Newlines (`\n`) worden automatisch omgezet naar `<br>` tags
- HTML in de response wordt ondersteund

## 🎨 User Experience

### Start Scherm
- Mooie introductie met Sinterklaas emoji
- Duidelijke call-to-action knop
- Animatie voor visueel effect

### Chat Interface
- **User berichten**: Rechts uitgelijnd met 👤 avatar en donkerblauwe achtergrond
- **Bot berichten**: Links uitgelijnd met 🦍 avatar en witte achtergrond
- **Loading indicator**: Animerende dots tijdens het wachten op antwoord
- **Auto-scroll**: Chat scrollt automatisch naar nieuwste bericht

### Functionaliteit
- ✅ Enter toets om bericht te versturen
- ✅ Disabled input/button tijdens laden
- ✅ Error handling met gebruiksvriendelijke foutmelding
- ✅ Session ID wordt bijgehouden gedurende hele gesprek

## 🔧 n8n Workflow Configuratie

### Stap 1: Webhook Trigger
```
Webhook Node:
- HTTP Method: POST
- Path: /webhook-test/receive_message
- Response Mode: Respond to Webhook
```

### Stap 2: Extract Data
```javascript
// Ontvang van frontend
const userMessage = $json.message;
const sessionId = $json.session_id;
```

### Stap 3: AI Processing
- Gebruik sessionId voor thread/context management
- Verwerk bericht met je AI agent (ChatGPT, Claude, etc.)
- Houd conversatie geschiedenis bij per session

### Stap 4: Respond to Webhook
```json
{
  "response": "{{ $json.ai_response }}",
  "session_id": "{{ $json.session_id }}"
}
```

## 🐛 Debugging

### Console Logs
Open de browser console (F12) om te zien:
- Session ID bij chat start
- Verstuurde berichten
- Ontvangen responses
- Eventuele errors

### Test Webhook
Je kunt je webhook testen met cURL:
```bash
curl -X POST https://dev.promptgorillas.com/webhook-test/receive_message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Test bericht",
    "session_id": "test_session_123"
  }'
```

Verwachte response:
```json
{
  "response": "Je AI antwoord hier",
  "session_id": "test_session_123"
}
```

## 💡 Tips

### Voor Gedichten met Opmaak
Je kunt HTML gebruiken in de response voor mooie opmaak:

```json
{
  "response": "<em>Lieve Jan, die altijd rent en fietst,<br>En nooit een training mist...<br><br>Dit gedicht is speciaal voor jou!</em>",
  "session_id": "session_xyz"
}
```

### Error Handling
Als je webhook faalt, ziet de gebruiker:
> "Sorry, er ging iets mis. Probeer het opnieuw! 😅"

De gebruiker kan dan gewoon opnieuw een bericht sturen.

### Session Management
- Elke nieuwe chat krijgt een nieuwe session_id
- Gebruik dit in n8n om conversaties gescheiden te houden
- Je kunt sessions opslaan in een database voor historie

## 🎯 Best Practices

1. **Response Tijd**: Probeer binnen 5 seconden te antwoorden
2. **Foutafhandeling**: Gebruik try-catch in n8n voor robuustheid
3. **Rate Limiting**: Implementeer rate limiting om misbruik te voorkomen
4. **Logging**: Log alle interacties voor debugging en verbetering
5. **Context**: Gebruik session_id om conversatie context bij te houden

## 🚀 Volgende Stappen

1. Test de webhook in n8n
2. Configureer je AI agent (OpenAI, Claude, etc.)
3. Implementeer thread/context management
4. Test de volledige flow
5. Monitor en optimize!

Veel succes! 🎅

