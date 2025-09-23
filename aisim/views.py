import json
import os
from datetime import datetime

import google.generativeai as genai
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

# --- Environment & Gemini API Configuration ---
# It's good practice to load environment variables once, typically in settings.py,
# but loading them here also works for a self-contained app.
load_dotenv()

try:
    # It's more standard to access settings via the django.conf.settings object
    GEMINI_API_KEY = settings.GEMINI_API_KEY
    if not GEMINI_API_KEY:
        raise ImproperlyConfigured(
            "The GEMINI_API_KEY is not set in your Django settings or .env file."
        )
    genai.configure(api_key=GEMINI_API_KEY)
except (AttributeError, ImproperlyConfigured) as e:
    raise ImproperlyConfigured(f"Fatal Error: Gemini API configuration failed. {e}") from e

# --- Main AI Simulator View ---
def ai_simulator_view(request):
    if request.method == 'GET':
        return render(request, 'aisim/index.html')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_query = data.get('message', '').strip()
            coords = data.get('coords')
        except json.JSONDecodeError:
            return JsonResponse({
                'reply_hi': '⚠️ अमान्य अनुरोध।',
                'reply_en': '⚠️ Invalid request format.'
            }, status=400)

        if not user_query:
            return JsonResponse({
                'reply_hi': '⚠️ कृपया अपना प्रश्न दर्ज करें।',
                'reply_en': '⚠️ Please enter your question.'
            }, status=400)

        # Updated system prompt with deep analysis focus
        system_prompt = f"""
        You are an advanced agricultural scenario simulator for Indian farmers. Your task is to deeply analyze "what if" questions related to crop production, yield optimization, fertilization, irrigation, climate effects, and overall farm profitability.
        
        **Instructions:**
        1. **Analyze the Scenario:** Provide a detailed, step-by-step analysis of the user's scenario.
        2. **Bilingual Output:** Respond in both Hindi (Devanagari) and English.
        3. **Structured Response:** Include the following sections:
           * **Scenario (परिदृश्य):** Restate the user's scenario clearly.
           * **Potential Impacts (संभावित प्रभाव):** Discuss effects on crop production, yield, resource use, and profitability.
           * **Recommended Actions (अनुशंसित कार्रवाइयां):** Give practical steps to optimize yield and farm outcomes.
        4. **Tone:** Professional, empathetic, and encouraging.
        5. **Context:**
           * Current Date: {timezone.now().strftime('%A, %B %d, %Y')}
           * User Location: Latitude {coords.get('lat', 'not provided') if coords else 'not provided'}, Longitude {coords.get('lon', 'not provided') if coords else 'not provided'}
        """

        try:
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                system_instruction=system_prompt
            )
            ai_response = model.generate_content(user_query).text
            return JsonResponse({
                'reply_hi': ai_response,
                'reply_en': ai_response
            })
        except Exception as e:
            print(f"ERROR: Gemini API call failed. {e}")
            return JsonResponse({
                'reply_hi': '⚠️ AI सिम्युलेटर से संपर्क करने में त्रुटि हुई।',
                'reply_en': '⚠️ An error occurred while contacting the AI simulator.'
            }, status=500)

    return JsonResponse({'error': f'Method {request.method} not allowed.'}, status=405)
