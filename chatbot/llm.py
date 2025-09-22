import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Initialize client
client = genai.Client(api_key=GEMINI_KEY)

# Example prompt
prompt_text = "Explain how AI works in a few words"

# Create a response
response = client.responses.create(
    model="gemini-2.5-flash",
    input=prompt_text
)

# Access the text output
print(response.output_text)
