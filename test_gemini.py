import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Please set GEMINI_API_KEY in .env file")
    exit()

genai.configure(api_key=api_key)

print("Available Gemini models:")
print("-" * 50)
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"✓ {m.name}")
        
print("\nTesting model...")
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Say hello!")
    print(f"\n✓ Success! Response: {response.text}")
except Exception as e:
    print(f"\n✗ Error with gemini-pro: {e}")
    print("\nTrying alternative models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            try:
                model = genai.GenerativeModel(m.name)
                response = model.generate_content("Say hello!")
                print(f"\n✓ {m.name} works! Response: {response.text}")
                break
            except:
                continue
