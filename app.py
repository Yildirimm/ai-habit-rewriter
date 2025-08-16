import gradio as gr 
from utils import generate_variations, export_pdf


def pick_version(versions, idx):
    """ return the selected version text by index"""

    try:
        return versions[idx] if versions and 0<= idx < len(versions) else "Invalid selection"
    except Exception as e:
        return ""
    

def store_edit(edited_text, versions ,idx):
    """Write the edited text back into the correct slot so it persists when switching tabs."""
    if not isinstance(versions, list) or versions is None:
        versions = ["", "", ""]

    if idx is None:
        idx = 0  # Default to the first version if no index is provided
    
    while len(versions) < 3:
        versions.append("")
    
    if 0 <= idx < len(versions):
        versions[idx] = edited_text
    
    return versions # return the updated versions list for gr.State


with gr.Blocks(css="#wrap{max-width:880px;margin:auto;}") as demo:
        gr.Markdown("# AI Habit Rewriter (SMART)\nPaste a goal, get 3 versions, click to switch, edit, and export.")

        with gr.Column(elem_id="wrap"):
            goal = gr.Textbox(label="Your Goal", placeholder="e.g. I want to lose weight", lines=4, interactive=True)
            gen_btn = gr.Button("Generate My Habits (3 Variants)")

            # State Containers 
            version_state = gr.State([]) # for v1, v2, v3
            selected_idx = gr.State(0)  # Index of the currently selected version (0, 1, 2)
           
            # Version buttons
            with gr.Row():  
                v1_btn = gr.Button("V1")
                v2_btn = gr.Button("V2")
                v3_btn = gr.Button("V3")

            # Editable Output 
            output_box = gr.Textbox(label="SMART habit", lines=14, interactive=True)

            # PDF Export Button
            export_btn = gr.Button("Export as PDF")
            pdf_file = gr.File(label="Download", type="filepath")



            # 1- Generate -> fill state + show v1 
            def on_generate(goal):
                print(f"DEBUG: Goal received: '{goal}'")
                versions = generate_variations(goal)
                print(f"DEBUG: Versions returned: {versions}")
                return versions, 0, versions[0] if versions else "No output generated"
            
            gen_btn.click(on_generate, inputs=[goal], outputs=[version_state, selected_idx, output_box])
            
            # Click -> takes current edited text -> returns a file path
            export_btn.click(fn=export_pdf, inputs=[output_box], outputs=[pdf_file])

            # 2- Select Version 
            def on_v1(versions): return 0, pick_version(versions, 0)
            def on_v2(versions): return 1, pick_version(versions, 1)
            def on_v3(versions): return 2, pick_version(versions, 2)

            v1_btn.click(on_v1, inputs=[version_state], outputs=[selected_idx, output_box])
            v2_btn.click(on_v2, inputs=[version_state], outputs=[selected_idx, output_box])
            v3_btn.click(on_v3, inputs=[version_state], outputs=[selected_idx, output_box])

            # 3- Persist Edits to correct versions 
            output_box.change(store_edit, inputs=[output_box, version_state, selected_idx],
                              outputs=[version_state])
            
demo.launch(share=True)