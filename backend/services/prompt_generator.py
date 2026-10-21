class PromptGenerator:

    def build_prompt(self, niche, page, section, content):

        return f"""
Create a premium website illustration.

Business: {niche}
Page: {page}
Section: {section}

Context:
{content}

Style:
- Modern
- Professional
- No text
- High quality
- Soft lighting
- Consistent branding
"""