# Filename: check_models.py
import google.generativeai as genai

# Apni API Key yahan dalein
API_KEY = "AIzaSyDuBz5Z518j26r21I2GPRfdSc9pw_P3iHo"

genai.configure(api_key=API_KEY)

print("Available Models for your Key:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"- {m.name}")