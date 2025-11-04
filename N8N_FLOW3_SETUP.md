# n8n Flow 3: Word Document Generator - Setup Guide

## Overzicht
Deze flow ontvangt een gedicht van de frontend, converteert het naar een gestructureerde JSON via LLM, en genereert een mooi geformatteerd Word-document met de Sinterklaas-template.

## Flow Structuur

```
[Webhook] → [LLM Node] → [HTTP Request] → [Respond to Webhook]
```

---

## Stap 1: Webhook Node

**Configuratie:**
- **Name:** Receive Poem Request
- **HTTP Method:** POST
- **Path:** `/styling-gedicht`
- **Authentication:** None (of zoals je hebt ingesteld)
- **Response Mode:** Respond with Last Node

**Verwachte Input:**
```json
{
  "session_id": "session_1730000000_abc123",
  "poem": "Het volledige gedicht\nMet regels\n\nEn strofes"
}
```

**Test URL:**
```
POST https://dev.promptgorillas.com/webhook/styling-gedicht
```

---

## Stap 2: LLM Node (OpenAI/Anthropic/etc.)

**Configuratie:**
- **Name:** Parse Poem to JSON
- **Model:** GPT-4 of Claude (aanbevolen voor nauwkeurigheid)
- **Temperature:** 0.1 (lage variatie voor consistentie)
- **Max Tokens:** 2000

**System Prompt:**
```
Je bent een expert in het parseren en structureren van Sinterklaasgedichten voor gebruik in Word-templates.

TAAK:
Je ontvangt een Sinterklaasgedicht en moet dit converteren naar JSON format.

OUTPUT FORMAT (alleen JSON, geen extra tekst):
{
  "voornaam": "Voornaam uit het gedicht",
  "session_id": "De ontvangen session_id",
  "rijm": "Het gedicht met \\n voor regels en \\n\\n tussen strofes"
}

REGELS:
1. Voornaam: Extraheer uit gedicht, gebruik "Beste vriend" als niet gevonden
2. Rijm formatting:
   - Elke versregel eindigt met \\n
   - Tussen strofes: \\n\\n (dubbele newline voor lege regel)
   - GEEN HTML tags zoals <br>
   - Max \\n\\n (niet meer)
3. Session_id: Behoud exact zoals ontvangen
4. Output: Alleen geldige JSON, geen extra tekst

VOORBEELD:
Input: "Lieve Jan\\nJe bent geweldig\\n\\nSinterklaas is blij"
Output:
{
  "voornaam": "Jan",
  "session_id": "session_123",
  "rijm": "Lieve Jan\\nJe bent geweldig\\n\\nSinterklaas is blij"
}
```

**User Message/Prompt:**
```
Converteer het volgende Sinterklaasgedicht naar JSON format.

Session ID: {{ $json.body.session_id }}

Gedicht:
{{ $json.body.poem }}

Geef alleen de JSON terug, geen extra tekst.
```

**Output Parsing:**
- **Parse Output:** Ja
- **Output Format:** JSON
- **Extract:** `$json` (of `$json.choices[0].message.content` voor OpenAI)

---

## Stap 3: Code Node (Optioneel - voor validatie)

**Voor extra zekerheid kun je een Code node toevoegen:**

```javascript
// Validate and clean the LLM output
const llmOutput = $input.item.json;

// Parse if string
let parsedData;
if (typeof llmOutput === 'string') {
    parsedData = JSON.parse(llmOutput);
} else {
    parsedData = llmOutput;
}

// Ensure all fields are present
if (!parsedData.voornaam || !parsedData.session_id || !parsedData.rijm) {
    throw new Error('Missing required fields in LLM output');
}

// Clean up rijm: ensure proper line breaks
parsedData.rijm = parsedData.rijm
    .replace(/\r\n/g, '\n')  // Normalize Windows line endings
    .replace(/\r/g, '\n')    // Normalize old Mac line endings
    .replace(/\n{3,}/g, '\n\n') // Max 2 consecutive newlines
    .trim();

return parsedData;
```

---

## Stap 4: HTTP Request Node

**Configuratie:**
- **Name:** Generate Word Document
- **Method:** POST
- **URL:** `https://sinterklaas-poem-backend.onrender.com/generate-word`
  - **Development:** `http://localhost:3000/generate-word`
  - **Production:** `https://sinterklaas-poem-backend.onrender.com/generate-word`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "voornaam": "{{ $json.voornaam }}",
  "session_id": "{{ $json.session_id }}",
  "rijm": "{{ $json.rijm }}"
}
```

**Response:**
- **Response Format:** File (Binary)
- **Binary Property:** `data` (of standaard)

---

## Stap 5: Respond to Webhook Node

**Configuratie:**
- **Name:** Return Word File
- **Respond With:** Using 'Respond to Webhook' Node
- **Response Code:** 200

**Headers:**
```
Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
Content-Disposition: attachment; filename="sinterklaas_gedicht_{{ $('Parse Poem to JSON').item.json.session_id }}.docx"
```

**Response Body:**
- **Response Mode:** Binary
- **Binary Property:** `data` (de output van de HTTP Request node)

**Alternatief (als binary niet werkt):**

Als n8n moeilijk doet met binary responses, kun je ook een redirect doen of de file als base64 teruggeven:

```json
{
  "file_data": "{{ $binary.data.toString('base64') }}",
  "file_name": "sinterklaas_gedicht_{{ $('Parse Poem to JSON').item.json.session_id }}.docx"
}
```

---

## Complete Flow Diagram

```
┌─────────────┐
│   Webhook   │ POST /styling-gedicht
│  (Receive)  │ Body: { session_id, poem }
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  LLM Node   │ System Prompt + User Message
│   (Parse)   │ Output: { voornaam, session_id, rijm }
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ HTTP Request│ POST to Backend
│ (Generate)  │ → /generate-word
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Respond to │ Return .docx file
│   Webhook   │ to Frontend
└─────────────┘
```

---

## Testing

### Test Input (via Postman/n8n)

```bash
curl -X POST https://dev.promptgorillas.com/webhook/styling-gedicht \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session_123",
    "poem": "Lieve Anna, zus zo fijn\nVol van liefde, nooit alleen\nJe helpt altijd met een glimlach\nDat maakt je bijzonder, zonder zweem\n\nSinterklaas heeft dit gezien\nEn geeft je daarom dit cadeau\nGeniet ervan met volle gloed\nAnna, jij bent echt heel mooi en goed"
  }'
```

### Verwachte Output

Een `.docx` bestand dat je kunt downloaden met:
- Voornaam: "Anna" ingevuld in de template
- Rijm: Het gedicht met correcte regeleindes en strofes

---

## Troubleshooting

### Probleem: LLM geeft geen geldige JSON terug

**Oplossing:** 
- Verhoog de temperature naar 0
- Voeg aan de prompt toe: "Output MUST be valid JSON only, no markdown, no explanations"
- Gebruik JSON mode als je model dat ondersteunt

### Probleem: Line breaks werken niet in Word

**Oplossing:**
- Check of de LLM `\n` gebruikt (niet `<br>` of `\\n`)
- Verifieer dat de template `{{rijm}}` gebruikt (niet `{{ rijm }}` met spaties)
- Check de backend logs voor error details

### Probleem: "Multi error" van docxtemplater

**Oplossing:**
- Installeer de linebreaks module: `npm install docxtemplater-line-module`
- Of gebruik de handmatige XML benadering (zie server.js alternatief hieronder)

### Probleem: Voornaam niet correct geëxtraheerd

**Oplossing:**
- Verbeter de LLM prompt met meer voorbeelden
- Voeg fallback logica toe in een Code node

---

## Backend URL's

### Development:
```
http://localhost:3000/generate-word
```

### Production:
```
https://sinterklaas-poem-backend.onrender.com/generate-word
```

---

## Alternatieve Server.js (zonder linebreaks module)

Als de `linebreaks: true` optie niet werkt, gebruik deze alternatieve aanpak:

```javascript
// In server.js, vervang de render sectie:

// Convert \n to manual line breaks for Word
const formattedRijm = rijm
    .replace(/\r\n/g, '\n')  // Normalize
    .replace(/\r/g, '\n')    
    .split('\n')
    .map(line => line.trim())
    .filter(line => line.length > 0 || line === '') // Keep empty lines
    .join('\n');

// Render with manual breaks
doc.render({
    voornaam: voornaam,
    rijm: formattedRijm
});
```

---

## Checklist voor Go-Live

- [ ] Webhook URL geconfigureerd in n8n
- [ ] LLM System Prompt correct ingesteld
- [ ] Backend URL aangepast naar productie
- [ ] Template bestand aanwezig op server
- [ ] Test gedicht succesvol gegenereerd
- [ ] Frontend download-knop getest
- [ ] Error handling getest (ongeldige input)
- [ ] Line breaks correct in Word-document

---

## Support

Bij problemen, check:
1. **Backend logs:** Render dashboard → Logs
2. **n8n execution logs:** Click op de execution in n8n
3. **Frontend console:** Browser Developer Tools (F12)
4. **Test endpoint:** `GET https://sinterklaas-poem-backend.onrender.com/health`

