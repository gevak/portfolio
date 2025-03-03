import asyncio
import logging
import os
from datetime import datetime

import utils

MODEL = 'openrouter/google/gemini-2.0-flash-exp:free'

# Minimal logging setup for console only
logging.basicConfig(level=logging.INFO)


def generate_page(model: str):
    design_text = utils.get_design(MODEL)

    # Log the design
    logging.info("Generated design: %s", design_text)

    impl_code = utils.get_impl(design_text, MODEL)
    
    # Create result path dirs
    today_dir = os.path.join('archive', datetime.now().strftime("%Y%m%d"))
    os.makedirs(today_dir, exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    # Save the results 
    design_file = os.path.join(today_dir, 'design.txt')
    
    html_file = os.path.join(today_dir, 'index.html')
    with open(design_file, 'w', encoding='utf-8') as f:
        f.write(design_text)
    logging.info(f"Design saved to {design_file}")
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(impl_code)
    logging.info(f"HTML saved to {html_file}")
    with open(os.path.join('templates', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(impl_code)
    logging.info(f"HTML template used to replace templates/index.html")
    with open(os.path.join('docs', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(impl_code)
    logging.info(f"HTML template used to replace docs/index.html")

    # Save screenshot
    # screenshot_jpg = asyncio.run(utils.get_screenshot(impl_code))
    # screenshot_file = os.path.join(today_dir, 'screenshot.jpg')
    # screenshot_jpg.save(screenshot_file)
    # logging.info(f"Screenshot saved to {screenshot_file}")


def main():
    generate_page(model=MODEL)


if __name__ == '__main__':
    main()
