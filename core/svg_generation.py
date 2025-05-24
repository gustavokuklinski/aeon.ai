import uuid
from pathlib import Path
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def generate_svg_from_prompt(prompt: str, llm, output_dir: str) -> str:
    """
    Generates an SVG based on the prompt using the configured LLM.
    The LLM is prompted to produce raw SVG XML.
    """
    filename_base = prompt.lower().replace(" ", "_").replace("'", "").replace('"', '')[:50]
    filename_base = "".join(c for c in filename_base if c.isalnum() or c in ['_', '-'])
    output_file = Path(output_dir) / f"{filename_base}_{uuid.uuid4().hex[:8]}.svg"

    if llm is None:
        return "\033[91m[ERROR]\033[0m LLM not initialized. Cannot generate SVG."

    try:
        svg_gen_system_prompt = (
            "You are an expert SVG code generator. Your task is to generate a complete, valid, "
            "and self-contained SVG XML code based on the user's request. "
            "The SVG should have a white background, be 200x200 pixels, and use a viewBox of 0 0 200 200. "
            "**Crucially, only output the raw SVG XML. Do NOT include any explanation, "
            "markdown formatting (e.g., ```xml`, ```svg`), or any other programming language code (like Python). "
            "Start directly with `<svg` and end with `</svg>`.**"
        )
        svg_gen_prompt_template = ChatPromptTemplate.from_messages([
            ("system", svg_gen_system_prompt),
            ("human", "Generate SVG for: {prompt}")
        ])

        svg_chain = svg_gen_prompt_template | llm | StrOutputParser()
        print(f"\033[1;34m[INFO]\033[0m Requesting SVG from LLM for prompt: '{prompt}'...")
        svg_content_raw = svg_chain.invoke({"prompt": prompt})

        svg_content = svg_content_raw.strip()
        
        # More robust cleaning:
        # Find the first occurrence of '<svg' and the last occurrence of '</svg>'
        # and extract only the content between them.
        svg_start_index = svg_content.lower().find('<svg')
        svg_end_index = svg_content.lower().rfind('</svg>')

        if svg_start_index != -1 and svg_end_index != -1:
            svg_content = svg_content[svg_start_index : svg_end_index + len('</svg>')].strip()
        else:
            print("\033[1;33m[WARN]\033[0m Could not find complete <svg>...</svg> tags in LLM output. Attempting to use raw output.")
            # Fallback to previous cleaning if start/end tags not found, though less reliable
            if svg_content.startswith("```xml"):
                svg_content = svg_content[len("```xml"):].strip()
            if svg_content.startswith("```svg"):
                svg_content = svg_content[len("```svg"):].strip()
            if svg_content.endswith("```"):
                svg_content = svg_content[:-len("```")].strip()


        # Ensure it's a valid SVG structure and has a white background
        if not svg_content.lower().startswith("<svg"):
            # If LLM didn't start with <svg, wrap it
            # Corrected xmlns attribute
            svg_content = f'<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="200" height="200" fill="white"/>{svg_content}</svg>'
            print("\033[1;33m[WARN]\033[0m LLM output was not a complete SVG. Wrapped it with a default SVG tag.")
        elif not '<rect x="0" y="0" width="200" height="200" fill="white"/>' in svg_content:
            # If <svg> exists but no background rect, try to add one after the opening <svg> tag
            insert_point = svg_content.lower().find('>') + 1
            if insert_point > 0:
                svg_content = svg_content[:insert_point] + '<rect x="0" y="0" width="200" height="200" fill="white"/>' + svg_content[insert_point:]
                print("\033[1;33m[WARN]\033[0m Added white background to LLM-generated SVG.")

        with open(output_file, 'w') as f:
            f.write(svg_content)

        return (f"\033[1;34m[INFO]\033[0m Generated SVG for prompt '{prompt}'. "
                f"SVG saved to: \033[36m{output_file}\033[0m. "
                f"\033[1;33m[NOTE]\033[0m Quality depends on LLM's SVG generation capability and its adherence to instructions.")
    except Exception as e:
        return f"\033[91m[ERROR]\033[0m Failed to generate SVG with LLM: {e}. " \
               f"Check LLM output for syntax errors or connectivity."