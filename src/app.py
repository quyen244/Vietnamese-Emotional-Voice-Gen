"""
Gradio Frontend UI Blocks

This module configures the visual interface and binds Python logic handlers 
for the inference pipeline.
"""
import gradio as gr
import time
import os

def create_gradio_blocks(model_instance):
    """
    Constructs the Gradio Blocks UI and sets up the event listening queue.
    """
    # Define themes and aesthetics
    theme = gr.themes.Soft(
        primary_hue="indigo",
        secondary_hue="purple",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
    )

    with gr.Blocks(theme=theme, title="Vn-EmoVoice: Vietnamese Emotional TTS") as demo:
        gr.Markdown(
            """
            # 🎙️ Vn-EmoVoice
            ### Premium Emotional Text-to-Speech Generation for Vietnamese
            Powered by VibeVoice architecture & fine-tuned on specialized expressive datasets.
            """
        )
        
        with gr.Row():
            # Left Column: Input text and controls
            with gr.Column(scale=2):
                text_input = gr.Textbox(
                    label="Script / Text Input",
                    placeholder="Enter Vietnamese text here...",
                    lines=8,
                    max_lines=20
                )
                
                with gr.Row():
                    speaker_selection = gr.Radio(
                        choices=["Male", "Female"],
                        value="Female",
                        label="Select Speaker"
                    )
                    topic_selection = gr.Dropdown(
                        choices=["Podcast", "Horror Story", "Audiobook", "News", "Emotional Narrative", "Neutral Assistant"],
                        value="Neutral Assistant",
                        label="Synthesis Style / Topic"
                    )
                
                with gr.Row():
                    generate_btn = gr.Button("🚀 Generate Audio", variant="primary")
                    stop_btn = gr.Button("🛑 Stop", variant="stop")
            
            # Right Column: Live Progress and Audio Output
            with gr.Column(scale=1):
                progress_panel = gr.Textbox(
                    label="Live Processing Stream",
                    placeholder="Waiting for input...",
                    lines=4,
                    interactive=False
                )
                
                audio_output = gr.Audio(
                    label="Synthesized Voice",
                    type="numpy",
                    interactive=False,
                    format="wav" # standard format
                )
                
                save_btn = gr.Button("💾 Downlaod / Save Audio", visible=False)

        # Event Handlers
        
        def stream_progress_mock(text):
            """
            A mock wrapper to simulate UI streaming. In a real scenario, this uses Gr.Progress
            or the async generator from the `model_instance`. 
            """
            if not text.strip():
                yield "No text provided."
                return
            
            # Use model's preprocess
            sentences = model_instance._preprocess_text(text)
            current_log = ""
            for s in sentences:
                time.sleep(0.5) # Simulate chunking delay
                current_log += f"✓ Processed: {s}\n"
                yield current_log
            yield current_log + "\n✔️ Done processing. Synthesizing audio..."
            
        def run_synthesis(text, speaker, topic):
            if not text.strip():
                return None, gr.update(visible=False)
            
            sr, audio = model_instance.synthesize(text, speaker, topic)
            return (sr, audio), gr.update(visible=True)
            
        # Hook buttons
        stream_event = generate_btn.click(
            fn=stream_progress_mock,
            inputs=[text_input],
            outputs=[progress_panel],
            queue=True
        )
        
        gen_event = generate_btn.click(
            fn=run_synthesis,
            inputs=[text_input, speaker_selection, topic_selection],
            outputs=[audio_output, save_btn],
            queue=True
        )
        
        stop_btn.click(
            fn=None,
            inputs=None,
            outputs=None,
            cancels=[stream_event, gen_event]
        )
        
    return demo

# For direct local testing running 'python src/app.py' mapping to mock model
if __name__ == "__main__":
    from src.model import VibeVoiceTTS
    dummy_model = VibeVoiceTTS(device="cpu")
    app = create_gradio_blocks(dummy_model)
    app.launch(server_name="localhost", server_port=7860)

# py -m src.app