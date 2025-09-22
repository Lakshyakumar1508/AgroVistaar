# chatbot/views.py

import json
import os
import re
import requests
from datetime import datetime
from dotenv import load_dotenv

import google.generativeai as genai
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.exceptions import ImproperlyConfigured

# ---------------- Environment & Gemini API ----------------
load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

try:
    GEMINI_API_KEY = getattr(settings, "GEMINI_API_KEY", None)
    if not GEMINI_API_KEY:
        raise ImproperlyConfigured("GEMINI_API_KEY not set in settings or .env")
    genai.configure(api_key=GEMINI_API_KEY)
except ImproperlyConfigured as e:
    raise ImproperlyConfigured(f"Gemini API configuration error: {e}") from e

# ---------------- Helper Functions ----------------
def normalize(text: str) -> str:
    text = text.lower()
    replacements = {
        r'\bu\b': 'you',
        r'\br\b': 'are',
        r'\bpls\b|\bplz\b': 'please',
        r'\bthx\b|\btnx\b': 'thanks',
        r'\bok\b|\bokay\b|\bthik hai\b|\btheek hai\b': 'ok',
        r'\bya\b|\bhaan\b|\byes\b': 'yes',
        r'\bna\b|\bnahi\b|\bno\b': 'no',
        r'\bhi\b|\bhello\b|\bnamaste\b|\bhola\b': 'hello',
        r'\bbye\b|\bbye bye\b|\balvida\b': 'bye',
        r'\bmausam\b|\bvedar\b': 'weather',
        r'\bfasal\b|\bfassal\b|\bcrop\b': 'crop',
        r'\brog\b|\bbimari\b': 'disease',
        r'\bkhad\b|\burvarak\b': 'fertilizer',
        r'\bbeej\b|\bbeejon\b': 'seeds',
        r'\bsinchai\b|\bpani\b': 'irrigation',
        r'\bke baare me batao\b|\bke baare me bataiye\b|\bbatao\b': '',
        r'\bkaise kare\b|\bkaise karen\b': 'how to do',
        r'\bhelp\b|\bmadad\b|\bany help\b': 'help',
        r'\bthank you\b|\bthanks\b|\bdhanyavad\b': 'thank you',
        r'\bgovernment\b|\byojana\b|\bsubsidy\b|\bscheme\b': 'scheme',
    }
    for pat, rep in replacements.items():
        text = re.sub(pat, rep, text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def detect_hindi(text: str) -> bool:
    return bool(re.search('[\u0900-\u097F]', text))

def get_weather(lat: float, lon: float) -> dict:
    """Return both Hindi and English weather strings"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_API_KEY}"
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        city = data.get('name', '')
        desc = data['weather'][0]['description']
        temp = data['main']['temp']
        return {
            'hi': f"🌤 वर्तमान मौसम {city} में: {desc}, तापमान: {temp}°C है।",
            'en': f"🌤 Current weather in {city}: {desc}, Temp: {temp}°C."
        }
    except requests.RequestException as e:
        print(f"Weather API error: {e}")
        return {
            'hi': "⚠️ मौसम की जानकारी नहीं मिल पाई।",
            'en': "⚠️ Could not fetch weather."
        }

# ---------------- Main Chat View ----------------
@csrf_exempt
def chat_view(request):
    if request.method == 'GET':
        index_path = os.path.join(settings.BASE_DIR, 'chatbot', 'templates', 'chatbot', 'chat.html')
        if os.path.exists(index_path):
            with open(index_path, 'r', encoding='utf-8') as f:
                return HttpResponse(f.read())
        return JsonResponse({'message': 'AgroBot Chat endpoint. Use POST to send messages.'})

    if request.method != 'POST':
        return JsonResponse({'error': f'Method {request.method} not allowed.'}, status=405)

    # ---------------- Parse Request ----------------
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        coords = data.get('coords')
    except json.JSONDecodeError:
        return JsonResponse({'reply_hi': '⚠️ अमान्य JSON।', 'reply_en': '⚠️ Invalid JSON format.'}, status=400)

    if not message:
        return JsonResponse({'reply_hi': '⚠️ कृपया संदेश भेजें।', 'reply_en': '⚠️ Please send a valid message.'}, status=400)

    input_text = normalize(message)

    # ---------------- Basic Replies ----------------
    basic_map = {
        'hello': ("नमस्ते! मैं एग्रोबॉट हूँ। खेती से संबंधित सवाल पूछें।",
                  "Hello! I am AgroBot. Ask me any questions about farming."),
        'thank you': ("खुशी है कि मैं मदद कर सका।", "You're welcome! Happy to help."),
        'ok': ("ठीक है।", "Okay."),
        'bye': ("अलविदा! शुभकामनाएँ।", "Goodbye! Take care."),
    }
    for key, (hi_msg, en_msg) in basic_map.items():
        if key in input_text:
            return JsonResponse({'reply_hi': hi_msg, 'reply_en': en_msg})

    # ---------------- Weather Handling ----------------
    if "weather" in input_text or "mausam" in input_text:
        if coords and coords.get('lat') and coords.get('lon'):
            weather = get_weather(coords['lat'], coords['lon'])
            return JsonResponse({'reply_hi': weather['hi'], 'reply_en': weather['en']})
        else:
            return JsonResponse({
                'reply_hi': "🌤 कृपया मौसम जानकारी के लिए स्थान की अनुमति दें।",
                'reply_en': "🌤 Please allow location access to get weather."
            })

    # ---------------- Government Scheme Handling ----------------
    if "scheme" in input_text:
        if not any(k in input_text for k in ["pm kisan", "soil health card", "kisan credit card"]):
            return JsonResponse({
                'reply_hi': "कृपया बताएं कि आप किस योजना के बारे में जानना चाहते हैं?",
                'reply_en': "Please specify which government scheme you want information about (e.g., PM Kisan, Soil Health Card)."
            })

    # ---------------- Gemini AI for other queries ----------------
    system_prompt = f"""
You are "AgroBot", an expert agricultural assistant for Indian farmers.
Respond in both Hindi and English. Keep responses short, friendly, and actionable.
Current Date: {timezone.now().strftime('%A, %B %d, %Y')}.
User location: latitude {coords['lat'] if coords else 'unknown'}, longitude {coords['lon'] if coords else 'unknown'}.
"""

    try:
        model = genai.GenerativeModel(
            model_name='gemini-1.5-flash',
            system_instruction=system_prompt
        )
        ai_response = model.generate_content(message).text

        # Optionally split Hindi and English manually if needed
        return JsonResponse({
            'reply_hi': ai_response,  # Gemini can generate bilingual text in one response
            'reply_en': ai_response
        })
    except Exception as e:
        print(f"Gemini API error: {e}")
        return JsonResponse({
            'reply_hi': "⚠️ AI से उत्तर नहीं मिला।",
            'reply_en': "⚠️ Could not generate response."
        }, status=500)
