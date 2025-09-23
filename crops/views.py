import json
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import google.generativeai as genai

# --- Gemini API Configuration ---
GEMINI_API_KEY = getattr(settings, "GEMINI_API_KEY", None)
if not GEMINI_API_KEY:
    raise ImproperlyConfigured("GEMINI_API_KEY is not set in Django settings.")
genai.configure(api_key=GEMINI_API_KEY)

# --- Main Crop Info View ---
def crop_info_view(request):
    if request.method == "GET":
        # Render the HTML form
        return render(request, "crops/index.html")

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_query = data.get("message", "").strip()
            coords = data.get("coords")
        except json.JSONDecodeError:
            return JsonResponse({
                "reply_hi": "⚠️ अमान्य अनुरोध।",
                "reply_en": "⚠️ Invalid request format."
            }, status=400)

        if not user_query:
            return JsonResponse({
                "reply_hi": "⚠️ कृपया अपना प्रश्न दर्ज करें।",
                "reply_en": "⚠️ Please enter a question."
            }, status=400)

        # Gemini system prompt
        system_prompt = f"""
        You are an advanced agricultural assistant for Indian farmers.
        Analyze the crop scenario and provide detailed info about:
        - Crop growth duration
        - Fertilizer requirements
        - Total production and per-hectare yield

        Respond in both Hindi and English.

        Context:
        Current Date: {timezone.now().strftime('%A, %B %d, %Y')}
        User Location: Latitude {coords.get('lat', 'not provided') if coords else 'not provided'},
        Longitude {coords.get('lon', 'not provided') if coords else 'not provided'}
        """

        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=system_prompt
            )
            ai_response = model.generate_content(user_query).text
            return JsonResponse({
                "reply_hi": ai_response,
                "reply_en": ai_response
            })
        except Exception as e:
            print(f"ERROR: Gemini API call failed: {e}")
            return JsonResponse({
                "reply_hi": "⚠️ AI सिम्युलेटर से संपर्क करने में त्रुटि हुई।",
                "reply_en": "⚠️ An error occurred while contacting the AI simulator."
            }, status=500)

    return JsonResponse({"error": f"Method {request.method} not allowed."}, status=405)
