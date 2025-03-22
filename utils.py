import models

import logging
import random
import re
from PIL import Image
from io import BytesIO
from playwright.async_api import async_playwright
from datetime import datetime

_DESIGNER_PROMPT_FILE = 'designer_prompt.txt'
_CODER_PROMPT_FILE = 'coder_prompt.txt'
_DREAMER_PROMPT_FILE = 'dreamer_prompt.txt'

_MODEL_TO_PROMPT = {
    'gemini': models.prompt_gemini,
    'claude': models.prompt_claude,
    'mock': lambda prompt: 'Response for: "' + prompt + '"'
}

def prompt(prompt: str, model: str) -> str:
  if model.startswith('openrouter/'):
    model = model[len('openrouter/'):]
    return models.prompt_openrouter(prompt, model)
  assert model in _MODEL_TO_PROMPT
  return _MODEL_TO_PROMPT[model](prompt)

def get_design(idea_title: str, model: str) -> str:
  designer_prompt = open(_DESIGNER_PROMPT_FILE, 'r').read()
  current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  return prompt(designer_prompt.format(idea_title=idea_title, current_time=current_timestamp), model)

def get_impl(design: str, model: str) -> str:
  impl_prompt = open(_CODER_PROMPT_FILE, 'r').read()
  text = prompt(impl_prompt.format(design=design), model)
  assert '<html' in text
  assert '</html>' in text
  html_code = text[text.find('<html'):text.find('</html>')+len('</html>')]
  return html_code

def get_idea_title(model: str) -> str:
  dreamer_prompt = open(_DREAMER_PROMPT_FILE, 'r').read()
  response = prompt(dreamer_prompt, model)
  logging.info("Got ideas response: %s", response)
  pattern = r'\**\s*idea\s+\d+:\s*\**\s*(.*)'
  ideas = []
  for line in response.splitlines():
    match = re.match(pattern, line, re.IGNORECASE) 
    if match:
      extracted_idea = match.group(1)
      ideas.append(extracted_idea)
  assert len(ideas) > 0
  idea = random.choice(ideas)
  idea = idea[idea.find(':') + 1:].strip()
  return idea

def convert_png_to_jpg(bytes_image_png: bytes, jpg_quality: int) -> Image.Image:
    image_png = Image.open(BytesIO(bytes_image_png))
    image_png = image_png.convert("RGB")
    output = BytesIO()
    image_png.save(output, format="JPEG", quality=jpg_quality)
    bytes_image_jpg = output.getvalue()
    image_jpg = Image.open(BytesIO(bytes_image_jpg))
    return image_jpg

async def get_screenshot(html_code: str) -> str:
  async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context(user_agent='test', device_scale_factor=2)
    page = await context.new_page()
    await page.set_content(html_code)
    await page.wait_for_load_state("networkidle")
    screenshot_data = await page.screenshot(full_page=True)
    image_jpg = convert_png_to_jpg(bytes_image_png=screenshot_data, jpg_quality=65)
    await context.close()
    await browser.close()
    return image_jpg
