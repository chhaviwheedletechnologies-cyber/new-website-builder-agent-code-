import os

target = "c:/Users/jC/Downloads/ai-website-builder/backend/template_design.py"
with open(target, "r", encoding="utf-8") as f:
    code = f.read()

if "import concurrent.futures" not in code:
    code = code.replace("import colorsys\n", "import colorsys\nimport concurrent.futures\n")

code = code.replace("client = OpenAI(api_key=api_key)", "client = OpenAI(api_key=api_key, timeout=120.0)")

loop_start_str = "    for i, page in enumerate(pages):\n"
before_loop, rest = code.split(loop_start_str, 1)

loop_end_str = "    log_status(f\"[TemplateAgent] ✅ Complete! Ready to preview.\")\n"
loop_body, after_loop = rest.split(loop_end_str, 1)

new_loop_def = "    def _generate_page(i, page):\n"
indented_body = "\n".join("    " + line if line.strip() else line for line in loop_body.split("\n"))

indented_body = indented_body.replace(
    "        files_generated += 1\n        file_paths.append(pg_path)\n", 
    ""
)
indented_body = indented_body.replace("            continue\n", "            return None\n")
indented_body = indented_body.rstrip() + "\n        return pg_path\n\n"

new_executor = """    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(_generate_page, i, p): p for i, p in enumerate(pages)}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                files_generated += 1
                file_paths.append(res)
                
"""
final_code = before_loop + new_loop_def + indented_body + new_executor + loop_end_str + after_loop

with open(target, "w", encoding="utf-8") as f:
    f.write(final_code)
print("Patch applied successfully.")
