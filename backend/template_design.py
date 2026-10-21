import os
import json
import re
import uuid
from typing import Dict, Any, List
from state import OrchestratorState
from openai import OpenAI
from dotenv import load_dotenv
import colorsys
import concurrent.futures
import base64
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
TEMPLATES_DIR = OUTPUT_DIR / "templates"
STATUS_FILE = OUTPUT_DIR / "status.txt"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")


def generate_ai_image(client, prompt, output_path):
    """Generate an image via OpenAI's image model and save it to disk.
    Returns the filename on success, or None on failure (never raises)."""
    try:
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1536x1024"
        )

        image = base64.b64decode(result.data[0].b64_json)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "wb") as f:
            f.write(image)

        return os.path.basename(output_path)
    except Exception as e:
        print(f"[TemplateAgent] Image generation failed for '{output_path}': {e}")
        return None


def build_image_prompt(industry, page, section, goal=""):
    return f"""
Create a premium, photorealistic website image.


Business industry: {industry}
Website page: {page}
Business objective: {goal}
Section: {section}

Requirements:
- Image must be directly relevant to the business and section.
- Show realistic objects, people, or environments for this industry.
- Professional lighting and modern art direction.
- Wide landscape composition suitable for a website.
- No text, watermark, fake logos, or unrelated stock imagery.
"""


def _inject_hero_image(html: str, hero_rel_path: str) -> str:
    """Replace the src of the .hero-bg-layer <img> tag with a locally
    generated AI image, regardless of attribute order in the tag."""
    if not hero_rel_path:
        return html

    pattern = re.compile(r'<img\b[^>]*class=["\'][^"\']*hero-bg-layer[^"\']*["\'][^>]*>', re.IGNORECASE)
    match = pattern.search(html)
    if not match:
        return html

    tag = match.group(0)
    if re.search(r'src=["\'][^"\']*["\']', tag):
        new_tag = re.sub(r'src=["\'][^"\']*["\']', f'src="{hero_rel_path}"', tag, count=1)
    else:
        new_tag = tag.replace('<img', f'<img src="{hero_rel_path}"', 1)

    return html[:match.start()] + new_tag + html[match.end():]


def _hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 3:
        hex_color = ''.join(c + c for c in hex_color)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def _adjust_color_lightness(hex_color: str, amount: float):
    try:
        r, g, b = _hex_to_rgb(hex_color)
        h, l, s = colorsys.rgb_to_hls(r / 255.0, g / 255.0, b / 255.0)
        new_l = min(1.0, max(0.0, l * amount))
        nr, ng, nb = colorsys.hls_to_rgb(h, new_l, s)
        return f"#{int(nr * 255):02x}{int(ng * 255):02x}{int(nb * 255):02x}"
    except Exception:
        # Fallback to the original hex if anything goes wrong
        return hex_color


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCTION-QUALITY CSS DESIGN SYSTEM
# This CSS is embedded directly so alignment, spacing, and polish are GUARANTEED.
# The LLM only generates HTML content using these exact class names.
# ═══════════════════════════════════════════════════════════════════════════════

BASE_CSS = """

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
  --primary: #6C63FF;
  --secondary: #FF6584;
  --primary-rgb: 108, 99, 255;
  --secondary-rgb: 255, 101, 132;
  --bg-dark: #000000;
  --text-primary: #FFFFFF;
  --text-secondary: rgba(255,255,255,0.7);
  --glass-bg: rgba(20, 20, 20, 0.4);
  --glass-border: rgba(255, 255, 255, 0.1);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: var(--bg-dark); color: var(--text-primary); font-family: 'Inter', sans-serif; line-height: 1.6; overflow-x: hidden; }

.container { max-width: 1400px; margin: 0 auto; padding: 0 40px; position: relative; z-index: 10; }

/* ═══ SLEEK NAVBAR ═══ */
.navbar { position: fixed; top: 0; left: 0; width: 100%; padding: 32px 0; z-index: 1000; transition: all 0.4s ease; }
.navbar.scrolled { padding: 16px 0; background: rgba(10,10,15,0.6); backdrop-filter: blur(24px); border-bottom: 1px solid rgba(255,255,255,0.05); }
.navbar .container { display: flex; justify-content: space-between; align-items: center; }
.nav-logo { font-size: 1.5rem; font-weight: 800; color: #fff; letter-spacing: -0.5px; text-transform: uppercase; }
.nav-img-logo { max-height: 40px; width: auto; object-fit: contain; }
.nav-links { display: flex; gap: 24px; }
.nav-link { color: rgba(255,255,255,0.8); font-size: 0.95rem; font-weight: 500; text-decoration: none; padding: 8px 4px; transition: 0.3s; position: relative; }
.nav-link:hover, .nav-link.active { color: #fff; }
.nav-link::after { content: ''; position: absolute; bottom: 0; left: 50%; width: 0; height: 2px; background: linear-gradient(90deg, var(--primary), var(--secondary)); transition: 0.3s; transform: translateX(-50%); }
.nav-link:hover::after, .nav-link.active::after { width: 100%; top: auto; }

/* ═══ CINEMATIC FULLSCREEN HERO ═══ */
.hero-fullscreen { position: relative; min-height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 120px 20px 80px; }
.hero-bg-layer { position: absolute; inset: 0; z-index: 0; width: 100%; height: 100%; object-fit: cover; }
.hero-overlay { position: absolute; inset: 0; z-index: 1; background: radial-gradient(circle at top right, rgba(var(--primary-rgb), 0.4), transparent 60%), radial-gradient(circle at bottom left, rgba(var(--secondary-rgb), 0.3), transparent 60%), linear-gradient(to bottom, transparent, rgba(0,0,0,0.95) 90%); }

.hero-bottom-grid { display: flex; flex-direction: column; align-items: center; gap: 32px; width: 100%; max-width: 1000px; position: relative; z-index: 2; margin: 0 auto; }

.hero-title-group { max-width: 100%; text-align: center; }
.hero-badge { display: inline-flex; padding: 6px 16px; background: rgba(255,255,255,0.1); border-radius: 50px; font-size: 0.85rem; color: #fff; margin-bottom: 24px; backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.1); }
.hero-title-group h1 { font-size: clamp(3.5rem, 6vw, 5.5rem); line-height: 1.1; letter-spacing: -2px; color: #fff; font-weight: 700; margin-bottom: 0; }

.hero-info-group { max-width: 750px; text-align: center; }
.hero-info-group p { font-size: 1.25rem; color: var(--text-secondary); margin-bottom: 32px; line-height: 1.7; }
.hero-buttons { display: flex; flex-direction: row; gap: 20px; justify-content: center; flex-wrap: wrap; margin-top: 16px; }
.btn-glass { display: inline-flex; align-items: center; justify-content: center; background: rgba(var(--primary-rgb), 0.15); border: 1px solid rgba(var(--primary-rgb), 0.4); color: #fff; padding: 14px 32px; border-radius: 50px; font-weight: 600; font-size: 0.95rem; backdrop-filter: blur(10px); transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); box-shadow: 0 4px 15px rgba(var(--primary-rgb), 0.2), inset 0 1px 1px rgba(255,255,255,0.1); width: max-content; text-decoration: none; }
.btn-glass:hover { background: rgba(var(--primary-rgb), 0.3); transform: translateY(-4px) scale(1.05); box-shadow: 0 15px 30px rgba(var(--primary-rgb), 0.4), inset 0 1px 1px rgba(255,255,255,0.2); border-color: rgba(var(--primary-rgb), 0.8); color: #fff; }
.btn-solid { display: inline-flex; align-items: center; justify-content: center; background: linear-gradient(135deg, var(--primary), var(--secondary)); color: #fff; padding: 14px 32px; border-radius: 50px; font-weight: 700; font-size: 0.95rem; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); box-shadow: 0 8px 25px rgba(var(--primary-rgb), 0.4), inset 0 2px 2px rgba(255,255,255,0.3); border: none; width: max-content; text-decoration: none; }
.btn-solid:hover { transform: translateY(-4px) scale(1.05); box-shadow: 0 15px 35px rgba(var(--primary-rgb), 0.6), inset 0 2px 2px rgba(255,255,255,0.4); filter: brightness(1.1); color: #fff; }

/* ═══ GRIDS, CARDS & FEATURES (FOR REMAINING CONTENT) ═══ */
.section { padding: 120px 0; background: #020202; position: relative; z-index: 10; }
.section-dark { padding: 120px 0; background: radial-gradient(circle at top right, rgba(var(--primary-rgb), 0.35), transparent 70%), radial-gradient(circle at bottom left, rgba(var(--primary-rgb), 0.15), transparent 60%), #000; position: relative; z-index: 10; }

.container-lg { max-width: 1200px; margin: 0 auto; padding: 0 40px; position: relative; z-index: 10; }
.grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 40px; }
.grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 32px; }
.gap-3 { gap: 24px; } .gap-4 { gap: 32px; }
.text-center { text-align: center; }

.card { background: linear-gradient(145deg, rgba(var(--primary-rgb),0.15) 0%, rgba(20,20,20,0.9) 100%); box-shadow: 0 10px 30px rgba(0,0,0,0.5), inset 0 1px 1px rgba(var(--primary-rgb), 0.2); border: 1px solid rgba(var(--primary-rgb), 0.2); border-radius: 20px; padding: 40px; position: relative; overflow: hidden; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.card:hover { border-color: rgba(var(--primary-rgb), 0.4); transform: translateY(-5px) scale(1.02); box-shadow: 0 15px 40px rgba(var(--primary-rgb), 0.15); }
.card-icon { font-size: 3rem; margin-bottom: 20px; color: var(--primary); }
.card h3 { font-size: 1.6rem; letter-spacing: -0.5px; margin-bottom: 12px; }
.card p { color: var(--text-secondary); font-size: 1.05rem; }

.section-header { margin-bottom: 60px; max-width: 800px; margin-left: auto; margin-right: auto; text-align: center; }
.section-header p { font-size: 1.15rem; color: var(--text-secondary); line-height: 1.7; margin-top: 16px; }
.section-header h2 { font-size: clamp(2.5rem, 5vw, 4rem); letter-spacing: -1.5px; margin-bottom: 15px; color: #fff; font-weight: 800; text-transform: uppercase; line-height: 1.1; }
.badge { display: inline-block; padding: 8px 16px; background: linear-gradient(90deg, rgba(var(--primary-rgb),0.15), rgba(var(--secondary-rgb),0.15)); color: #fff; border: 1px solid rgba(255,255,255,0.2); border-radius: 50px; font-size: 0.95rem; margin-bottom: 24px; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; }

.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 40px; text-align: center; margin-top: 60px; }
.stat-item h3 { font-size: 3.5rem; letter-spacing: -2px; margin-bottom: 8px; background: linear-gradient(135deg, var(--primary), var(--secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.stat-item p { color: var(--text-secondary); font-size: 1.1rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

.features-split { display: flex; flex-wrap: wrap; gap: 60px; align-items: center; justify-content: space-between; }
.features-split > img { flex: 1 1 400px; width: 100%; height: auto; border-radius: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.6); object-fit: cover; }
.features-split > .features-list, .features-split > div { flex: 1 1 400px; }
.feature-item { display: flex; gap: 24px; margin-bottom: 40px; align-items: flex-start; }
.feature-item .icon { font-size: 1.6rem; color: #fff; background: linear-gradient(135deg, var(--primary), var(--secondary)); border: none; width: 64px; height: 64px; display: flex; align-items: center; justify-content: center; border-radius: 16px; box-shadow: 0 10px 20px rgba(var(--primary-rgb), 0.4); flex-shrink: 0; }
.feature-item h4 { font-size: 1.3rem; margin-bottom: 8px; }
.feature-item p { color: var(--text-secondary); font-size: 1rem; }

/* ═══ CTA TEXT & BANNERS ═══ */
.cta-banner { padding: 80px 40px; background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%); border-radius: 24px; margin: 40px 0; box-shadow: 0 20px 50px rgba(var(--primary-rgb), 0.2); position: relative; overflow: hidden; text-align: center; }
.cta-banner * { color: #fff; position: relative; z-index: 2; }
.cta-banner h2 { font-size: clamp(2.5rem, 4vw, 3.5rem); margin-bottom: 20px; letter-spacing: -1.5px; line-height: 1.1; }
.cta-banner p { font-size: 1.2rem; opacity: 0.9; max-width: 600px; margin: 0 auto 32px; }
.cta-banner .btn-solid { background: #fff; color: #000; box-shadow: 0 10px 30px rgba(0,0,0,0.3), inset 0 -3px 0 rgba(0,0,0,0.1); text-shadow: none; filter: none; }
.cta-banner .btn-solid:hover { box-shadow: 0 15px 40px rgba(0,0,0,0.4), inset 0 -3px 0 rgba(0,0,0,0.1); filter: none; transform: translateY(-4px) scale(1.05); color: #000; }
.gradient-text { background: linear-gradient(135deg, var(--primary), var(--secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.cta-banner .gradient-text { background: none; -webkit-text-fill-color: initial; color: #fff; }

/* ═══ FORMS ═══ */
.contact-form-wrapper { position: relative; max-width: 700px; margin: 0 auto; }
.contact-form-wrapper::before { content: ''; position: absolute; inset: -2px; border-radius: 26px; z-index: 1; background: linear-gradient(135deg, var(--primary), var(--secondary)); opacity: 0.5; filter: blur(10px); }
.contact-form { position: relative; z-index: 2; display: flex; flex-direction: column; gap: 24px; text-align: left; background: rgba(10,10,12,0.9); padding: 40px; border-radius: 24px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 20px 40px rgba(0,0,0,0.8); backdrop-filter: blur(20px); }
.form-input, .form-textarea { width: 100%; padding: 18px 24px; background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; color: #fff; font-size: 1rem; font-family: inherit; transition: 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
.form-input:focus, .form-textarea:focus { border-color: var(--secondary); outline: none; background: rgba(0,0,0,0.7); box-shadow: 0 0 20px rgba(var(--secondary-rgb), 0.3); }
.form-textarea { min-height: 160px; resize: vertical; }
.btn-submit { background: linear-gradient(135deg, var(--primary), var(--secondary)); color: #fff; padding: 16px 32px; border: none; border-radius: 50px; font-weight: 700; font-size: 1.1rem; cursor: pointer; transition: 0.4s; box-shadow: 0 10px 20px rgba(var(--primary-rgb), 0.3); }
.btn-submit:hover { transform: translateY(-4px) scale(1.02); box-shadow: 0 15px 30px rgba(var(--secondary-rgb), 0.5); filter: brightness(1.2); }

/* ═══ FOOTER ═══ */
.footer { background: #050505; color: var(--text-secondary); padding: 80px 0; font-size: 0.95rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 60px; }
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1.5fr; gap: 40px; }

.footer-brand .nav-logo { font-size: 2rem; color: #fff; margin-bottom: 5px; }
.footer-brand .brand-tagline { color: var(--primary); font-size: 0.85rem; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 16px; }
.footer-brand p { margin-bottom: 24px; line-height: 1.6; max-width: 300px; }

.social-links { display: flex; gap: 12px; }
.social-links a { display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; color: #fff; transition: 0.3s; text-decoration: none; }
.social-links a:hover { border-color: var(--primary); color: var(--primary); }

.footer h4 { color: #fff; font-size: 1rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 24px; }
.footer ul { list-style: none; }
.footer ul li { margin-bottom: 12px; display: flex; align-items: flex-start; gap: 8px; }
.footer ul li a { color: var(--text-secondary); text-decoration: none; transition: 0.3s; }
.footer ul li a:hover { color: var(--primary); }
.footer ul li::before { content: '›'; color: var(--primary); font-size: 1.2rem; line-height: 1; }

.contact-list li::before { content: none; } 
.contact-item { display: flex; align-items: flex-start; gap: 12px; margin-bottom: 16px; }
.contact-item .icon { color: var(--primary); font-size: 1.2rem; margin-top: 2px; }

.animate-on-scroll { opacity: 0; transform: translateY(30px); transition: 0.8s ease-out; }
.animate-on-scroll.visible { opacity: 1; transform: translateY(0); }

"""

# JavaScript for scroll animations and mobile nav toggle
BASE_JS = """
<script>
// Scroll Animation Observer
document.addEventListener('DOMContentLoaded', () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));

  // Mobile Nav Toggle
  const toggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  if (toggle && navLinks) {
    toggle.addEventListener('click', () => navLinks.classList.toggle('open'));
  }

  // Navbar Background on Scroll
  const navbar = document.querySelector('.navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    });
  }
});
</script>
"""


def _call_llm(client: OpenAI, system_prompt: str, user_prompt: str) -> str:
    """Call LLM and return raw text content."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=6000,
        )
        return response.choices[0].message.content or ""
    except Exception as e:
        error_msg = f"[TemplateAgent] LLM Error: {e}"
        print(error_msg)

        # status.txt me bhi error likho
        try:
            status_file = str(STATUS_FILE)
            with open(status_file, "a", encoding="utf-8") as f:
                f.write(error_msg + "\n")
        except Exception:
            pass

        return ""


def _call_llm_json(client: OpenAI, system_prompt: str, user_prompt: str) -> dict:
    """Call LLM and return parsed JSON."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=16000,
        )
        return json.loads(response.choices[0].message.content or "{}")
    except Exception as e:
        print(f"[TemplateAgent] LLM JSON Error: {e}")
        return {}


def _extract_html(raw: str) -> str:
    """Extract clean HTML from LLM response, stripping markdown fences."""
    # Try to find HTML between ```html ... ``` fences
    match = re.search(r'```html\s*([\s\S]*?)```', raw)
    if match:
        return match.group(1).strip()
    # Try generic fences
    match = re.search(r'```\s*([\s\S]*?)```', raw)
    if match:
        return match.group(1).strip()
    # If starts with <!DOCTYPE or <html, use as-is
    stripped = raw.strip()
    if stripped.startswith('<!') or stripped.startswith('<html'):
        return stripped
    return stripped


def _postprocess_html(html: str) -> str:
    """Fix common LLM mistakes in generated HTML to guarantee correct rendering."""
    # 1. Fix CSS filename variants (styles.css, stylesheet.css, main.css, etc.) → style.css
    html = re.sub(
        r'href=["\'](?:styles?\.css|stylesheet\.css|main\.css|css/style\.css|css/styles\.css)["\']',
        'href="style.css"',
        html,
        flags=re.IGNORECASE
    )

    # 2. Remove any <style>...</style> blocks the LLM may have injected
    html = re.sub(r'<style[^>]*>[\s\S]*?</style>', '', html, flags=re.IGNORECASE)

    # 3. Remove any inline style= attributes
    html = re.sub(r'\s+style="[^"]*"', '', html)
    html = re.sub(r"\s+style='[^']*'", '', html)

    # 4. Ensure the CSS link exists in <head>. If missing, inject it.
    if 'href="style.css"' not in html:
        html = html.replace('</head>', '    <link rel="stylesheet" href="style.css">\n</head>')

    # 5. Ensure viewport meta exists for responsive design
    if 'viewport' not in html:
        html = html.replace('</head>', '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n</head>')

    return html


# ═══════════════════════════════════════════════════════════════════════════════
# AVAILABLE CSS CLASSES REFERENCE (given to LLM so it knows exactly what to use)
# ═══════════════════════════════════════════════════════════════════════════════

CSS_CLASS_REFERENCE = """

AVAILABLE CSS CLASSES (MUST STRICTLY ADHERE TO THESE CLASSES):

CINEMATIC HERO (CRITICAL FOR YOUR LAYOUT - DO NOT DEVIATE):
1. Wrap the entire first screen in: `<div class="hero-fullscreen">`
2. Insight it, add the background image: `<img class="hero-bg-layer" src="https://loremflickr.com/1920/1080/[topic]" alt="Bg">`
3. Add the dark fade: `<div class="hero-overlay"></div>`
4. Add the bottom content container: `<div class="container"><div class="hero-bottom-grid">...</div></div>`
5. Inside `hero-bottom-grid`, first column is `<div class="hero-title-group"><span class="hero-badge">Badge</span><h1>Huge Title</h1></div>`
6. Inside `hero-bottom-grid`, second column is `<div class="hero-info-group"><p>Paragraph...</p><div class="hero-buttons"><a class="btn-glass">Button</a><a class="btn-solid">Button</a></div></div>`

CAPSULE NAVIGATION:
- You MUST build the navbar structure as follows:
`<nav class="navbar"><div class="container"><div class="nav-logo">BRAND</div><div class="nav-links"><a class="nav-link active" href="...">Link</a>...</div></div></nav>`

SECTIONS & FEATURES:
- Use `.section > .container > .section-header` embedding a `<span class="badge">` AND a `<h2>Huge Title</h2>` for group titles.
- Use `.grid-3.gap-4` containing multiple `.card.animate-on-scroll` elements for feature grids (each card can have a `.card-icon`).
- For side-by-side layouts, wrap them in `<div class="features-split">`. The FIRST element must be an `<img>` and the SECOND element must be `<div class="features-list">`. Failure to follow this order will break the flexbox grid!
- Use `.stats-row > .stat-item` > `h3` + `p` to show massive metric numbers!
- Use `.section-dark` for alternating sections to create dynamic background depth.
- IF generating a Contact page, layout MUST include a gorgeously framed form: `<div class="contact-form-wrapper"><form class="contact-form"><input class="form-input">...<button class="btn-submit" type="submit">Send</button></form></div>`
- Use `<section class="cta-banner"><div class="container text-center"><h2>...</h2><p>...</p><a class="btn-solid">Action</a></div></section>` for Call to Actions!
- Use `<span class="gradient-text">text</span>` to highlight key words in titles.

FOOTER ARCHITECTURE (MANDATORY):
- Structure exactly like: `<footer class="footer"><div class="container"><div class="footer-grid">...</div></div></footer>`
- `footer-grid` MUST have exactly 3 columns:
  1. `<div class="footer-brand">`: Use `<div class="nav-logo">BRAND</div>`, then `<div class="brand-tagline">TAGLINE</div>`, paragraph, then `<div class="social-links"><a href="#">FB</a>...</div>`
  2. Quick Links: `<h4>` then `<ul><li><a href="...">...</a></li></ul>`
  3. Get In Touch: `<h4>` then `<ul class="contact-list"><li class="contact-item"><span class="icon">📍</span> Address</li></ul>`
- DO NOT INCLUDE ANY OTHER COLUMNS OR FOOTER BOTTOM STRIPS.

CRUCIAL IMAGES:
Do NOT use external placeholder image URLs like loremflickr or picsum.
For the hero section, always include:
<img class="hero-bg-layer" src="hero-placeholder" alt="Hero Background">
The Python code will automatically replace "hero-placeholder" with an AI-generated image.
"""


def template_design_agent(state: OrchestratorState) -> Dict[str, Any]:
    """
    Genius-level Template Design Agent.
    Uses a hardcoded production CSS design system + multi-step LLM pipeline
    so every generated website has guaranteed perfect alignment and polish,
    with AI-generated hero imagery per page.
    """
    client_goal_raw = state.get("client_goal", "")
    try:
        client_goal = f"Objective: {client_goal_raw.objective}, Audience: {client_goal_raw.target_audience}, Industry: {client_goal_raw.industry}"
        industry = client_goal_raw.industry or "General Business"
    except AttributeError:
        client_goal = str(client_goal_raw)
        industry = "General Business"

    brand_context = state.get("brand_context", "")
    brand_color = state.get("brand_color", "#6C63FF")
    secondary_color = state.get("secondary_color", "#FF6584")
    logo_data = state.get("logo_data", "")

    # SECURITY FIX: never hardcode API keys. Load from environment (.env) instead.
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {
            "messages": ["Template Design: Failed (Missing OPENAI_API_KEY in environment/.env)."]
        }

    # FIX: use the key loaded from the environment above, instead of a
    # hardcoded literal key. Never commit real API keys into source code.
    client = OpenAI(
        api_key=api_key, timeout=120.0)
    
    base_dir = str(TEMPLATES_DIR)
    run_id = str(uuid.uuid4())[:8]
    output_dir = os.path.join(base_dir, f"template_{run_id}")
    os.makedirs(output_dir, exist_ok=True)

    logo_filename = ""
    if logo_data and logo_data.startswith("data:image"):
        try:
            header, encoded = logo_data.split(",", 1)
            ext = "png"
            if "svg" in header:
                ext = "svg"
            elif "jpeg" in header or "jpg" in header:
                ext = "jpg"
            elif "webp" in header:
                ext = "webp"

            logo_filename = f"brand_logo.{ext}"
            logo_path = os.path.join(output_dir, logo_filename)
            with open(logo_path, "wb") as f:
                f.write(base64.b64decode(encoded))
        except Exception as e:
            print(f"[TemplateAgent] Logo processing failed: {e}")

    status_file = str(STATUS_FILE)
    with open(status_file, "w", encoding="utf-8") as f:
        f.write(f"Generating Template [{run_id}]...\n")

    def log_status(msg):
        print(msg)
        with open(status_file, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    files_generated = 0
    file_paths = []

    # ─── STEP 1: PLAN PAGES ───
    log_status("[TemplateAgent] Step 1/3: Planning page architecture...")
    raw_target_pages = state.get("target_pages", [])

    target_pages = []
    for p in raw_target_pages:
        p_clean = p.lower().strip()
        if p_clean == "home":
            target_pages.append("index.html")
        else:
            p_clean = re.sub(r'[^a-z0-9\s-]', '', p_clean)
            p_clean = re.sub(r'[\s]+', '-', p_clean)
            if not p_clean.endswith('.html'):
                p_clean += '.html'
            target_pages.append(p_clean)

    if target_pages and len(target_pages) > 0:
        plan_sys = (
            "You are a web project planner. Given a client goal, extract a site_name and tagline for the website. "
            "Output ONLY a JSON object: {\"site_name\": \"...\", \"tagline\": \"...\"}"
        )
        plan_user = f"Client Goal:\n{client_goal}\n\nBrand Context:\n{brand_context}\n\nList the site_name and tagline."
        plan_data = _call_llm_json(client, plan_sys, plan_user)

        pages = target_pages
        site_name = plan_data.get("site_name", "Brand")
        tagline = plan_data.get("tagline", "")
    else:
        plan_sys = (
            "You are a web project planner. Given a client goal, extract the EXACT list of HTML pages needed. "
            "Output ONLY a JSON object: {\"pages\": [\"index.html\", \"about.html\", ...], \"site_name\": \"...\", \"tagline\": \"...\"}"
        )
        plan_user = f"Client Goal:\n{client_goal}\n\nBrand Context:\n{brand_context}\n\nList the exact HTML page filenames."
        plan_data = _call_llm_json(client, plan_sys, plan_user)

        pages = plan_data.get("pages", ["index.html"])
        site_name = plan_data.get("site_name", "Brand")
        tagline = plan_data.get("tagline", "")

    if not pages:
        return {"messages": ["Architecture planning failed."]}

    log_status(f"[TemplateAgent]   → Pages mapped: {', '.join(pages)}")

    # ─── STEP 2: WRITE CSS FILE ───
    log_status("[TemplateAgent] Step 2/3: Generating and mapping brand CSS...")

    # Generate dynamic CSS based on brand color
    try:
        r, g, b = _hex_to_rgb(brand_color)
        primary_rgb = f"{r}, {g}, {b}"
        primary_dark = _adjust_color_lightness(brand_color, 0.8)   # 20% darker
        primary_light = _adjust_color_lightness(brand_color, 1.3)  # 30% lighter

        r2, g2, b2 = _hex_to_rgb(secondary_color)
        secondary_rgb = f"{r2}, {g2}, {b2}"

        # Replace the hardcoded base purple and pink with the chosen colors
        dynamic_css = BASE_CSS.replace("#6C63FF", brand_color.upper())
        dynamic_css = dynamic_css.replace("#6c63ff", brand_color.upper())  # case fallback
        dynamic_css = dynamic_css.replace("108, 99, 255", primary_rgb)
        dynamic_css = dynamic_css.replace("#5A52D5", primary_dark.upper())
        dynamic_css = dynamic_css.replace("#8B83FF", primary_light.upper())

        dynamic_css = dynamic_css.replace("#FF6584", secondary_color.upper())
        dynamic_css = dynamic_css.replace("#ff6584", secondary_color.upper())
        dynamic_css = dynamic_css.replace("255, 101, 132", secondary_rgb)
    except Exception as e:
        print(f"[TemplateAgent] CSS color processing failed: {e}. Falling back to default CSS.")
        dynamic_css = BASE_CSS

    css_path = os.path.join(output_dir, "style.css")
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(dynamic_css)
    files_generated += 1
    file_paths.append(css_path)

    # Assets folder for AI-generated images — created once, shared across pages
    assets_dir = os.path.join(output_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # ─── STEP 3: GENERATE EACH HTML PAGE ───
    logo_instruction = (
        f"12. For the website logo (.nav-logo), use an image! `<img src='{logo_filename}' alt='Logo' class='nav-img-logo'>`. Do NOT use text."
        if logo_filename else "12. For the website logo (.nav-logo), use TEXT ONLY (e.g., the Site Name). Do NOT put an <img> tag in the nav-logo."
    )

    nav_links_html = ""
    for pg in pages:
        label = pg.replace(".html", "").replace("_", " ").replace("-", " ").title()
        if pg == "index.html":
            label = "Home"
        nav_links_html += f'        <a href="{pg}">{label}</a>\n'

    def _generate_page(i, page):
        page_label = page.replace(".html", "").replace("_", " ").replace("-", " ").title()
        
        # Normalize page filename before saving
        page_name = (
            page.strip()
                .lower()
                .replace(".html", "")
                .replace(" ", "_")
        )

        if page_name in ["home", "index"]:
            filename = "index.html"
        elif page_name in ["about", "our_story"]:
            filename = "about.html"
        elif page_name == "services":
            filename = "services.html"
        elif page_name == "contact":
            filename = "contact.html"
        else:
            filename = f"{page_name}.html"

        page_path = os.path.join(output_dir, filename)

        if page == "index.html":
            page_label = "Home"

        # Generate AI images for multiple sections of this page
        sections = ["Hero", "About", "Services", "Features", "Contact"]

        generated_images = []

        # FIX: the append used to sit OUTSIDE this for-loop, so `filename`
        # only ever held the result of the LAST section (Contact), and every
        # other generated image was silently dropped. Now every successfully
        # generated section image is collected.
        for section in sections:
            prompt = build_image_prompt(
                industry,
                page_label,
                section,
                goal=f"{client_goal}. Brand context: {brand_context}"
            )

            filename = generate_ai_image(
                client,
                prompt,
                os.path.join(
                    assets_dir,
                    f"{page_label.lower().replace(' ', '_')}_{section.lower()}.png"
                )
            )

            if filename:
                generated_images.append(f"assets/{filename}")

        hero_rel_path = generated_images[0] if generated_images else None

        log_status(f"[TemplateAgent] Step 3/3: Designing UI and content for {page} ({i+1}/{len(pages)})...")

        page_sys = f"""You are an elite, world-class UI/UX designer and frontend developer specialized in ultra-premium cinematic web experiences.

YOUR TASK: Generate the COMPLETE HTML for the "{page_label}" page of a business named "{site_name}".

CRITICAL RULES (FOLLOW EXACTLY):
1. Output ONLY raw HTML code. Start with <!DOCTYPE html>.
2. Stylesheet is EXACTLY <link rel="stylesheet" href="style.css">.
3. ALL styling comes from the pre-built CSS classes provided. Do NOT use inline styles, EVER.
4. DO NOT WRITE BASIC GENERIC WEBSITES. You MUST write visually dramatic, cinematic designs exactly matching the CSS Rules below.
5. EVERY PAGE MUST START WITH `.hero-fullscreen` WITH A `.hero-bg-layer` IMAGE. THIS IS MANDATORY. The background image must be breathtaking (use high res placeholder keywords).
6. The Navigation MUST use `.nav-pill` buttons, centered, matching Apple/Stripe aesthetics.
7. YOU MUST STRICTLY USE EXACTLY THESE NAVIGATION LINKS INSIDE THE `.nav-links` CONTAINER AND ABSOLUTELY NO OTHERS:
<div class="nav-links">
{nav_links_html}
</div>
(Do NOT hallucinate additional pages like 'Shop' or 'Blog' if they are not in the list above!)
8. CONTENT QUALITY & DEPTH (CRITICAL): Generate very long, highly detailed pages requiring substantial scrolling. Do NOT create short, basic pages. You MUST generate at least 4 to 6 distinct, highly detailed layout sections per page. EVERY single element must be strictly and highly relevant to the specific '{page_label}' topic. Write highly engaging, professional, persuasive, industry-specific copywriting. Treat every text block like it was written by an elite premium ad agency.
9. IMAGE DIRECTIVES (MANDATORY): Do NOT use external image URLs like loremflickr or picsum. For every visual section (Hero, About, Services, Features, Contact), use an <img> tag with a simple placeholder src="hero-placeholder". These placeholders will be automatically replaced with AI-generated images after the HTML is generated.
10. NO HALLUCINATED URLs (CRITICAL): EVERY `href` link in your navigation OR buttons MUST link ONLY to one of the exact valid pages provided below. NEVER invent unrequested links (like `reserve.html`, `shop.html`, or `pricing.html`). If a button needs a link, use `index.html` or a valid page.
11. CARD RESTRICTIONS: Do NOT put `<img>` tags inside the `.card` component. Cards are for text/icons only. Use `.features-split` if you want images.
12. {logo_instruction}
13. ANTI-PLAGIARISM PROTOCOL (MANDATORY): You must generate 100% unique, unplagiarized text. NEVER use generic corporate filler or cliché industry idioms. Invert standard sentence structures (use active voice, start with action verbs). Use domain-specific synonyms to replace common phrases. Alter cadence: mix short, punchy single-sentence paragraphs with longer explanatory ones. Do not replicate text patterns from standard web templates!

{CSS_CLASS_REFERENCE}
"""

        page_user = f"""Build the "{page_label}" page for:
Site: {site_name}
Tagline: {tagline}
Brand: {brand_context}
Goal: {client_goal}

This is the {page_label} page. Make it absolutely stunning with rich, detailed content. Write real content paragraphs, not placeholders. Include multiple sections. Make it feel like a $10,000 professionally designed website."""

        raw_html = _call_llm(client, page_sys, page_user)
        html_content = _extract_html(raw_html)

        if not html_content:
            log_status(f"[TemplateAgent] ❌ Empty HTML returned for {page}")
            print(f"[TemplateAgent] ❌ Raw LLM response: {repr(raw_html[:300])}")
            return None

        # Post-process: fix CSS links, strip inline styles, ensure correct references
        html_content = _postprocess_html(html_content)

        # Swap the LLM's placeholder hero image for our AI-generated one, if we have it
        if hero_rel_path:
            html_content = _inject_hero_image(html_content, hero_rel_path)

        # Replace remaining image placeholders with AI-generated images
        remaining_images = generated_images[1:]  # Hero already used

        img_pattern = re.compile(
            r'<img\b(?![^>]*hero-bg-layer)[^>]*src=["\'][^"\']*["\'][^>]*>',
            re.IGNORECASE
        )

        def replace_img(match):
            if remaining_images:
                img_tag = match.group(0)
                next_img = remaining_images.pop(0)
                return re.sub(
                    r'src=["\'][^"\']*["\']',
                    f'src="{next_img}"',
                    img_tag,
                    count=1
                )
            return match.group(0)

        html_content = img_pattern.sub(replace_img, html_content)

        if logo_filename:
            # Forcefully inject the logo directly into the nav-logo div to bypass LLM hallucination
            html_content = re.sub(
                r'(<[a-zA-Z0-9]+[^>]*?class=["\'][^"\']*?nav-logo[^"\']*?["\'][^>]*?>).*?(</[a-zA-Z0-9]+>)',
                f'\\1<img src="{logo_filename}" alt="Logo" class="nav-img-logo">\\2',
                html_content,
                flags=re.DOTALL
            )

        # Inject the JS before closing </body>
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", BASE_JS + "\n</body>")
        else:
            html_content += "\n" + BASE_JS

        with open(page_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"[DEBUG] Saved file: {page_path}")

        log_status(f"[TemplateAgent]   ✓ {filename} generated ({len(html_content):,} chars)")
        return page_path

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_generate_page, i, p): p for i, p in enumerate(pages)}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                files_generated += 1
                file_paths.append(res)

    log_status("[TemplateAgent] ✅ Complete! Ready to preview.")

    return {
        "messages": [
            f"Template Design: Generated {files_generated} premium files.",
            f"Templates saved to: {output_dir}"
        ],
        "execution_results": {
            "template_dir": output_dir,
            "generated_files": file_paths,
            "run_id": run_id
        }
    }
