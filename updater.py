import asyncio
import logging
import os
from datetime import datetime

import archive_utils
import utils

MODEL = 'openrouter/google/gemini-2.0-flash-exp:free'

LIKE_BUTTON_CODE = """<!-- Add this block to embed the like button -->
    <script src="/static/js/like_button.js"></script>
    <script>
        LikeButton.init({{
          pageId: "{page_id}",
          position: "bottom-right", // Options: bottom-right, bottom-left, top-right, top-left
        }});
    </script>
"""

# Minimal logging setup for console only
logging.basicConfig(level=logging.INFO)


def perform_overrides(code: str, metadata: dict[str, str]) -> str:
    """Perform overrides on the AI-generated code based on metadata.
    
    Used to force some things in the resulting website.
    """
    # Add like button code before the closing body tag.
    assert "</body>" in code, "No </body> tag found in the code: %s" % code
    # Escape the curly braces in the code.
    code = code.replace("{", "{{").replace("}", "}}")
    code = code.replace("</body>", "{like_button_code}\n</body>")
    return code.format(**metadata)

def generate_page(model: str):
    page_id = datetime.now().strftime("%Y%m%d")
    idea_title = utils.get_idea_title(model)
    logging.info("Generating idea: %s", idea_title)

    design_text = utils.get_design(idea_title, model)
    logging.info("Generated design: %s", design_text)

    impl_code = utils.get_impl(design_text, model)
    # Perform overrides in the code.
    like_button_code = LIKE_BUTTON_CODE.format(page_id=page_id)
    impl_code = perform_overrides(impl_code, {"like_button_code": like_button_code})
    
    # Create result path dirs
    today_dir = os.path.join('static', 'archive', page_id)
    os.makedirs(today_dir, exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    # Save the results 
    idea_file = os.path.join(today_dir, 'title.txt')
    design_file = os.path.join(today_dir, 'design.txt')
    html_file = os.path.join(today_dir, 'index.html')
    with open(idea_file, 'w', encoding='utf-8') as f:
        f.write(idea_title)
    with open(design_file, 'w', encoding='utf-8') as f:
        f.write(design_text)
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(impl_code)
    logging.info(f"HTML saved to {html_file}")
    with open(os.path.join('templates', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(impl_code)
    logging.info("HTML template used to replace templates/index.html")
    with open(os.path.join('docs', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(impl_code)
    logging.info("HTML template used to replace docs/index.html")
    logging.info("Creating DB entry")
    archive_utils.save_like_count(0, page_id, title=idea_title)

    # Save screenshot
    screenshot_jpg = asyncio.run(utils.get_screenshot(impl_code))
    screenshot_file = os.path.join(today_dir, 'screenshot.jpg')
    screenshot_jpg.save(screenshot_file)
    logging.info(f"Screenshot saved to {screenshot_file}")


def main():
    generate_page(model=MODEL)


if __name__ == '__main__':
    main()
