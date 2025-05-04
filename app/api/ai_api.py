from flask import Blueprint, jsonify, request
from flask_login import login_required
import os
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/advice', methods=['POST'])
@login_required
def get_ai_advice():
    try:
        # Get prompt from request
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'No prompt provided'}), 400
        
        # Get API key from environment variables
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            detailed_message = (
                "Gemini API key not configured. Please contact the server administrator "
                "to ensure the GEMINI_API_KEY is properly set in the environment variables. "
                "Without this key, AI-assisted trading features cannot function."
            )
            return jsonify({'success': False, 'error': detailed_message}), 500
        
        # Check if API key is just the placeholder from .env.example
        if api_key == "your_gemini_api_key_here":
            detailed_message = (
                "The Gemini API key appears to be using a placeholder value. "
                "Please contact the server administrator to set up a valid API key "
                "in the environment variables. Without a valid key, AI-assisted trading "
                "features cannot function."
            )
            return jsonify({'success': False, 'error': detailed_message}), 500
        
        try:
            # Initialize Gemini API client
            client = genai.Client(api_key=api_key)
            model_id = "gemini-2.0-flash"
            
            # Set up Google Search tool
            google_search_tool = Tool(
                google_search=GoogleSearch()
            )
            
            # Generate content with Gemini
            response = client.models.generate_content(
                model=model_id,
                contents=prompt,
                config=GenerateContentConfig(
                    tools=[google_search_tool],
                    response_modalities=["TEXT"],
                )
            )
            
            # Extract the response text
            response_text = ""
            for part in response.candidates[0].content.parts:
                response_text += part.text
                
            # Get the search grounding metadata (if available)
            grounding_metadata = {}
            try:
                grounding_metadata = {
                    "search_results": response.candidates[0].grounding_metadata.search_entry_point.rendered_content
                }
            except (AttributeError, TypeError):
                # No grounding metadata available
                pass
                
            return jsonify({
                'success': True, 
                'advice': response_text,
                'grounding_metadata': grounding_metadata
            })
        except Exception as e:
            api_error_message = (
                f"Error connecting to Google Gemini API: {str(e)}. "
                "This may be due to an invalid API key or a service outage. "
                "Please contact the server administrator to verify API key configuration."
            )
            return jsonify({'success': False, 'error': api_error_message}), 500
            
    except Exception as e:
        print(f"Error in AI advice: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500 