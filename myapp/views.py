# myapp/views.py
from django.shortcuts import render
import os
import numpy as np
import tensorflow as tf
import joblib
from django.conf import settings

# Paths
MODEL_PATH = os.path.join(settings.BASE_DIR, 'myapp', 'model', 'crop_recommendation_model.h5')
SCALER_PATH = os.path.join(settings.BASE_DIR, 'myapp', 'model', 'crop_scaler.pkl')
ENCODER_PATH = os.path.join(settings.BASE_DIR, 'myapp', 'model', 'crop_label_encoder.pkl')

# Load model and preprocessors
try:
    crop_model = tf.keras.models.load_model(MODEL_PATH)
    crop_scaler = joblib.load(SCALER_PATH)
    crop_encoder = joblib.load(ENCODER_PATH)
    model_loaded = True
except Exception as e:
    print(f"Error loading model or preprocessors: {e}")
    crop_model = None
    crop_scaler = None
    crop_encoder = None
    model_loaded = False

# Fertilizer map
fertilizer_map = {
    'rice': 'Urea', 'maize': 'Urea', 'chickpea': 'DAP', 'kidneybeans': 'Urea',
    'pigeonpeas': 'DAP', 'mothbeans': 'Urea', 'mungbean': 'DAP', 'blackgram': 'DAP',
    'lentil': 'DAP', 'pomegranate': 'NPK', 'banana': 'Urea', 'mango': 'Urea',
    'grapes': 'NPK', 'watermelon': 'NPK', 'muskmelon': 'NPK', 'apple': 'NPK',
    'orange': 'NPK', 'papaya': 'Urea', 'coconut': 'NPK', 'cotton': 'NPK',
    'jute': 'Urea', 'coffee': 'DAP'
}

# Features in order
FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# Prediction & Dashboard view
def prediction_view(request):
    prediction_result = None
    fertilizer_result = None
    input_data = {f: '' for f in FEATURES}

    if request.method == 'POST' and model_loaded:
        try:
            # Collect input data
            input_data = {f: request.POST.get(f, 0) for f in FEATURES}
            X = np.array([float(input_data[f]) for f in FEATURES]).reshape(1, -1)

            # Scale inputs and predict
            X_scaled = crop_scaler.transform(X)
            pred_idx = np.argmax(crop_model.predict(X_scaled, verbose=0), axis=1)[0]
            predicted_crop = crop_encoder.inverse_transform([pred_idx])[0]

            # Capitalize first letter
            predicted_crop = predicted_crop.capitalize()

            # Fertilizer recommendation
            recommended_fertilizer = fertilizer_map.get(predicted_crop.lower(), "General Urea/DAP")

            prediction_result = predicted_crop
            fertilizer_result = recommended_fertilizer

        except Exception as e:
            prediction_result = f"Error: {e}"

    elif not model_loaded:
        prediction_result = "Model not loaded. Check server logs."

    context = {
        'prediction': prediction_result,
        'fertilizer': fertilizer_result,
        'submitted_inputs': input_data,
        'FEATURES': FEATURES
    }

    return render(request, 'myapp/recomm.html', context)
