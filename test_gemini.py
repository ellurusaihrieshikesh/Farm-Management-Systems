import google.generativeai as genai

# Configure the API key
genai.configure(api_key='AIzaSyD_N1eBFFsh1gk7CVLmy8qUTIgUCAOmdR4')

# List available models
print("Available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(f"  {m.name}")

# Try to use a model
try:
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("Hello, what's your name?")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")