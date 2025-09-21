import os
import cv2
import numpy as np
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from flask_cors import CORS # Import CORS

# --- Initialization ---
app = Flask(__name__)
# Enable CORS for all routes, allowing the frontend to make requests from a different origin.
CORS(app) 

# Define the model path and image size.
MODEL_PATH = 'crop_disease_model.h5'
IMG_SIZE = 128
# These class names must match the output classes of the trained model.
CLASS_NAMES = [
    'Pepper__bell___Bacterial_spot',
    'Pepper__bell___healthy',
]

# Load the trained Keras model.
# This is done once when the server starts to improve performance.
try:
    model = load_model(MODEL_PATH)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}. The server will not be able to make predictions.")
    model = None

# --- Helper Function for Preprocessing ---
def preprocess_image(image_bytes):
    """
    Decodes and preprocesses an image for model prediction.
    
    Args:
        image_bytes (bytes): The raw image data.
        
    Returns:
        numpy.ndarray: The preprocessed image ready for the model.
    """
    # Convert image bytes to a numpy array.
    image_array = np.frombuffer(image_bytes, np.uint8)
    # Decode the image from the array using OpenCV.
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    # Resize the image to the required dimensions for the model.
    resized_img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    # Normalize the pixel values to be between 0 and 1.
    normalized_img = resized_img / 255.0
    # Add a batch dimension to the image.
    batched_img = np.expand_dims(normalized_img, axis=0)
    return batched_img

# --- Route to serve the main page ---
@app.route('/', methods=['GET'])
def index():
    """
    Returns a simple string to indicate the server is running.
    The HTML has been removed from this file.
    """
    return "The Flask server is running. Use the /predict endpoint to make predictions."

# --- API Endpoint for Prediction ---
@app.route('/predict', methods=['POST'])
def predict():
    """
    Handles image upload, preprocesses the image, and returns a prediction.
    """
    # Check if the model was loaded correctly at server startup.
    if model is None:
        return jsonify({'error': 'Model is not loaded. Please check the model file path and format.'}), 500

    # Ensure a file was included in the request.
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request.'}), 400
    
    file = request.files['file']
    
    # Check if the file name is not empty.
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading.'}), 400

    try:
        # Read the image data from the request.
        image_bytes = file.read()
        
        # Preprocess the image for the model.
        processed_image = preprocess_image(image_bytes)
        
        # Make a prediction using the loaded model.
        prediction = model.predict(processed_image)
        
        # Get the index of the class with the highest confidence.
        predicted_class_index = np.argmax(prediction, axis=1)[0]
        # Get the confidence score for the predicted class.
        confidence = float(np.max(prediction, axis=1)[0])
        # Get the class name from the predefined list.
        predicted_class_name = CLASS_NAMES[predicted_class_index]
        
        # Create a JSON response. Returning confidence as a float is a best practice.
        response = {
            'predicted_class': predicted_class_name,
            'confidence': confidence
        }
        return jsonify(response)
    
    except Exception as e:
        # Log the full error for debugging purposes.
        print(f"Prediction error: {e}")
        return jsonify({'error': f'An error occurred during prediction: {str(e)}'}), 500

# --- Run the App ---
if __name__ == '__main__':
    # Run the Flask app on host '0.0.0.0' to be accessible externally.
    # The port is set to 5000 as per the original request.
    app.run(host='0.0.0.0', port=5000, debug=True)
