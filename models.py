from google import genai
from openai import OpenAI
import os
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def prompt_gemini(prompt: str) -> str:
  api_key = os.environ['GOOGLE_API_KEY']
  client = genai.Client(api_key=api_key)
  response = client.models.generate_content(
      model='gemini-2.0-pro-exp-02-05', contents=prompt
  )
  return response.text


def prompt_claude(prompt, system_prompt=None, temperature=0.7, max_tokens=8192):
    api_key = os.environ['ANTHROPIC_API_KEY']
    client = anthropic.Anthropic(
        api_key=api_key,  # Replace with your actual API key
    )
    
    # Prepare the message request
    messages_params = [{"role": "user", "content": prompt}]
    
    # Create additional parameters for the request
    params = {
        #"model": "claude-3-7-sonnet-20250219",
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages_params
    }
    
    # Add system prompt if provided
    if system_prompt:
        params["system"] = system_prompt
        
    # Send request to Claude
    response = client.messages.create(**params)
    
    # Return just the text response
    return response.content[0].text


def prompt_openrouter(prompt: str, model: str = 'google/gemini-2.0-flash-exp:free') -> str:
    api_key = os.environ['OPENROUTER_API_KEY']
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    )
    completion = client.chat.completions.create(
    model=model,
    messages=[
        {
        "role": "user",
        "content": prompt
        }
    ]
    )
    return completion.choices[0].message.content
