from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from docxtpl import DocxTemplate
from jinja2 import Environment as JinjaEnvironment
import os
import tempfile

app = Flask(__name__)
CORS(app)

# Template path
BASE_DIR = os.path.dirname(__file__)
TEMPLATE_PATH = os.path.join(BASE_DIR, 'template_gedicht_sinterklaas.docx')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Sinterklaas Word Generator is running"})

@app.route('/generate-word', methods=['POST'])
def generate_word():
    """
    Generate a Word document from the Sinterklaas template using Jinja templating
    """
    try:
        # Get JSON data from request
        data = request.get_json() or {}
        
        voornaam = data.get('voornaam', '')
        session_id = data.get('session_id', '')
        rijm = data.get('rijm', '')
        
        if not voornaam or not rijm:
            return jsonify({"error": "voornaam and rijm are required"}), 400
        
        # Check if template exists
        if not os.path.exists(TEMPLATE_PATH):
            return jsonify({"error": "Template file not found"}), 500
        
        # Load the template
        doc = DocxTemplate(TEMPLATE_PATH)
        
        # Custom Jinja filter for converting \n to paragraphs
        def nl2para(value, style=None):
            """
            Convert text with \n line breaks to Word paragraphs
            - Single \n creates a new line within the same section
            - Double \n\n creates a blank line (new strofe/section)
            """
            if not isinstance(value, str):
                return doc.new_subdoc()
            
            text = value.strip()
            if not text:
                return doc.new_subdoc()
            
            # Create subdocument
            sub = doc.new_subdoc()
            
            # Split on double newlines (strofes/sections)
            strofes = text.split('\n\n')
            
            for i, strofe in enumerate(strofes):
                if i > 0:
                    # Add blank paragraph between strofes
                    sub.add_paragraph('', style=style)
                
                # Split lines within strofe
                lines = strofe.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        # Add each line as a paragraph
                        sub.add_paragraph(line, style=style)
            
            return sub
        
        # Register custom Jinja filter
        env = JinjaEnvironment(autoescape=False)
        env.filters['nl2para'] = nl2para
        
        # Prepare context for template
        context = {
            'voornaam': voornaam,
            'rijm': rijm  # Template should use: {{ rijm|nl2para }}
        }
        
        # Render the template
        doc.render(context, jinja_env=env)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
            doc.save(tmp.name)
            tmp_path = tmp.name
        
        # Generate filename
        filename = f"sinterklaas_gedicht_{session_id}.docx"
        
        # Send the file
        return send_file(
            tmp_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
    except Exception as e:
        print(f"Error generating Word document: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Failed to generate Word document",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    # Get port from environment or use default
    PORT = int(os.environ.get('PORT', 5000))
    HOST = os.environ.get('HOST', '0.0.0.0')
    
    # Check if template exists
    print(f"Template path: {TEMPLATE_PATH}")
    print(f"Template exists: {os.path.exists(TEMPLATE_PATH)}")
    
    app.run(host=HOST, port=PORT, debug=False)

