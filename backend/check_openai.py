import os
import openai

def check_environment():
    api_key = os.getenv('Open_AI_API')
    if api_key:
        print("OpenAI API key is set")
        print(f"OpenAI package version: {openai.__version__}")
        return True
    else:
        print("OpenAI API key is not set")
        return False

if __name__ == "__main__":
    check_environment()
