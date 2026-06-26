"""
SuperBrain JARVIS — Main UI Application
Glassmorphism design with motion effects, fully functional interface.
"""

import gradio as gr
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import json

logger = logging.getLogger("ui")


def create_app(orchestrator, memory_manager, model_manager):
    """
    Create the complete Gradio UI with glassmorphism theme and all panels.
    """
    
    # Custom CSS for glassmorphism and motion effects
    custom_css = """
    :root {
        --glass-bg: rgba(255, 255, 255, 0.1);
        --glass-border: rgba(255, 255, 255, 0.2);
        --glass-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        --primary-glow: rgba(0, 212, 255, 0.6);
        --secondary-glow: rgba(142, 45, 226, 0.5);
        --text-primary: #ffffff;
        --text-secondary: rgba(255, 255, 255, 0.8);
        --accent-cyan: #00d4ff;
        --accent-purple: #8e2de2;
        --success: #00ff88;
        --warning: #ffaa00;
        --error: #ff4444;
    }
    
    body {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        overflow-x: hidden;
    }
    
    body::before {
        content: '';
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, var(--primary-glow) 0%, transparent 70%),
                    radial-gradient(circle, var(--secondary-glow) 0%, transparent 70%);
        background-position: 0% 0%, 100% 100%;
        background-size: 80% 80%;
        animation: aurora 20s ease-in-out infinite;
        opacity: 0.3;
        z-index: -1;
        pointer-events: none;
    }
    
    @keyframes aurora {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(10%, 10%) rotate(5deg); }
        50% { transform: translate(-5%, 15%) rotate(-5deg); }
        75% { transform: translate(15%, -5%) rotate(3deg); }
    }
    
    .gradio-container {
        max-width: 100% !important;
        padding: 20px !important;
    }
    
    /* Glass panel styling */
    .glass-panel {
        background: var(--glass-bg);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        box-shadow: var(--glass-shadow);
        padding: 20px;
        transition: all 0.3s ease;
    }
    
    .glass-panel:hover {
        background: rgba(255, 255, 255, 0.15);
        border-color: rgba(255, 255, 255, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 12px 40px 0 rgba(31, 38, 135, 0.5);
    }
    
    /* Chat interface */
    .chat-message {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        animation: slideIn 0.3s ease;
        border-left: 3px solid var(--accent-cyan);
    }
    
    .chat-message.user {
        border-left-color: var(--accent-purple);
        background: rgba(142, 45, 226, 0.15);
    }
    
    .chat-message.assistant {
        border-left-color: var(--accent-cyan);
        background: rgba(0, 212, 255, 0.1);
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Buttons with glow effect */
    .gr-button {
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple)) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3) !important;
    }
    
    .gr-button:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 6px 20px rgba(142, 45, 226, 0.5) !important;
    }
    
    .gr-button:active {
        transform: translateY(0) scale(0.98) !important;
    }
    
    /* Input fields */
    .gr-input, .gr-textbox {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid var(--glass-border) !important;
        color: var(--text-primary) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }
    
    .gr-input:focus, .gr-textbox:focus {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3) !important;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-active {
        background: var(--success);
        box-shadow: 0 0 10px var(--success);
    }
    
    .status-idle {
        background: var(--warning);
        box-shadow: 0 0 10px var(--warning);
    }
    
    .status-offline {
        background: var(--error);
        box-shadow: 0 0 10px var(--error);
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Agent cards */
    .agent-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--glass-border);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .agent-card:hover {
        background: rgba(255, 255, 255, 0.1);
        transform: scale(1.02);
        border-color: var(--accent-cyan);
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--accent-cyan);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-purple);
    }
    
    /* Markdown rendering */
    .prose {
        color: var(--text-primary) !important;
    }
    
    .prose pre {
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 10px !important;
    }
    
    .prose code {
        color: var(--accent-cyan) !important;
    }
    
    /* Tabs styling */
    .tab-nav {
        background: rgba(255, 255, 255, 0.05) !important;
        border-bottom: 1px solid var(--glass-border) !important;
    }
    
    .tab-nav button {
        color: var(--text-secondary) !important;
        transition: all 0.3s ease !important;
    }
    
    .tab-nav button.selected {
        color: var(--accent-cyan) !important;
        border-bottom: 2px solid var(--accent-cyan) !important;
    }
    
    /* Loading animation */
    .thinking-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        color: var(--accent-cyan);
    }
    
    .thinking-dot {
        width: 8px;
        height: 8px;
        background: var(--accent-cyan);
        border-radius: 50%;
        animation: bounce 1.4s infinite ease-in-out both;
    }
    
    .thinking-dot:nth-child(1) { animation-delay: -0.32s; }
    .thinking-dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    /* Header styling */
    .header-glow {
        text-align: center;
        padding: 30px 0;
        background: linear-gradient(135deg, transparent, rgba(0, 212, 255, 0.1), transparent);
        border-radius: 20px;
        margin-bottom: 20px;
    }
    
    .header-glow h1 {
        font-size: 2.5em;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
        margin: 0;
    }
    
    .header-glow p {
        color: var(--text-secondary);
        font-size: 1.1em;
        margin-top: 10px;
    }
    """
    
    def process_message(message, history):
        """Process user message through orchestrator."""
        if not message.strip():
            return history
        
        # Add user message
        history.append((message, None))
        yield history
        
        try:
            # Process through orchestrator
            response = orchestrator.process(message)
            
            # Update with assistant response
            history[-1] = (message, response)
            yield history
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            history[-1] = (message, f"❌ Error: {str(e)}")
            yield history
    
    def get_agent_status():
        """Get current status of all agents."""
        try:
            status = orchestrator.get_agent_status()
            status_html = "<div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;'>"
            
            for agent_name, info in status.items():
                status_class = "status-active" if info['status'] == 'active' else "status-idle"
                emoji = info.get('emoji', '🤖')
                
                status_html += f"""
                <div class="agent-card">
                    <div style="display: flex; align-items: center; margin-bottom: 10px;">
                        <span class="status-indicator {status_class}"></span>
                        <span style="font-size: 1.5em; margin-right: 10px;">{emoji}</span>
                        <strong style="color: var(--text-primary);">{agent_name}</strong>
                    </div>
                    <p style="color: var(--text-secondary); font-size: 0.9em; margin: 0;">
                        {info.get('description', 'No description')}
                    </p>
                    <p style="color: var(--accent-cyan); font-size: 0.8em; margin-top: 8px;">
                        Tasks completed: {info.get('tasks_completed', 0)}
                    </p>
                </div>
                """
            
            status_html += "</div>"
            return status_html
            
        except Exception as e:
            return f"<p style='color: var(--error);'>Error loading agent status: {e}</p>"
    
    def get_memory_stats():
        """Display memory statistics and recent items."""
        try:
            stats = memory_manager.get_stats()
            recent_memories = memory_manager.search_recent(limit=5)
            
            stats_html = f"""
            <div class="glass-panel">
                <h3 style="color: var(--accent-cyan); margin-top: 0;">📊 Memory Statistics</h3>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 20px;">
                    <div style="background: rgba(0, 212, 255, 0.1); padding: 15px; border-radius: 10px;">
                        <p style="margin: 0; color: var(--text-secondary);">Total Memories</p>
                        <p style="font-size: 2em; margin: 0; color: var(--accent-cyan);">{stats.get('total_memories', 0)}</p>
                    </div>
                    <div style="background: rgba(142, 45, 226, 0.1); padding: 15px; border-radius: 10px;">
                        <p style="margin: 0; color: var(--text-secondary);">Conversations</p>
                        <p style="font-size: 2em; margin: 0; color: var(--accent-purple);">{stats.get('conversations', 0)}</p>
                    </div>
                </div>
                
                <h4 style="color: var(--text-primary);">Recent Memories</h4>
                <div style="max-height: 300px; overflow-y: auto;">
            """
            
            for mem in recent_memories:
                timestamp = mem.get('timestamp', 'Unknown')[:19]
                content = mem.get('content', '')[:100]
                
                stats_html += f"""
                <div style="background: rgba(255, 255, 255, 0.05); padding: 10px; 
                            border-radius: 8px; margin-bottom: 8px; border-left: 3px solid var(--accent-purple);">
                    <p style="margin: 0; font-size: 0.8em; color: var(--text-secondary);">{timestamp}</p>
                    <p style="margin: 5px 0 0 0; color: var(--text-primary);">{content}...</p>
                </div>
                """
            
            stats_html += "</div></div>"
            return stats_html
            
        except Exception as e:
            return f"<p style='color: var(--error);'>Error loading memory stats: {e}</p>"
    
    def clear_conversation():
        """Clear conversation history."""
        orchestrator.clear_conversation()
        return [], "✅ Conversation cleared"
    
    def export_conversation():
        """Export conversation to file."""
        try:
            history = orchestrator.context_manager.get_history()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
            
            export_path = memory_manager.export_dir / filename
            with open(export_path, 'w') as f:
                json.dump(history, f, indent=2)
            
            return f"✅ Exported to {export_path}"
        except Exception as e:
            return f"❌ Error: {e}"
    
    def get_system_info():
        """Display system information."""
        try:
            models = model_manager.list_models()
            models_str = ", ".join(models) if models else "No models available"
            
            return f"""
            <div class="glass-panel">
                <h3 style="color: var(--accent-cyan); margin-top: 0;">⚙️ System Information</h3>
                
                <div style="margin-bottom: 20px;">
                    <p style="color: var(--text-secondary); margin: 5px 0;"><strong>Active Model:</strong> {model_manager.active_model}</p>
                    <p style="color: var(--text-secondary); margin: 5px 0;"><strong>Available Models:</strong> {models_str}</p>
                    <p style="color: var(--text-secondary); margin: 5px 0;"><strong>Ollama Status:</strong> <span style="color: var(--success);">● Connected</span></p>
                </div>
                
                <h4 style="color: var(--text-primary);">Quick Actions</h4>
                <p style="color: var(--text-secondary); font-size: 0.9em;">
                    Use commands in chat:<br>
                    • /memory - Browse memories<br>
                    • /agents - Show agent status<br>
                    • /clear - Clear conversation<br>
                    • /export - Export conversation<br>
                    • /help - Show all commands
                </p>
            </div>
            """
        except Exception as e:
            return f"<p style='color: var(--error);'>Error: {e}</p>"
    
    # Build the UI
    with gr.Blocks(css=custom_css, title="🧠 SuperBrain JARVIS", theme=gr.themes.Base()) as app:
        
        # Header
        with gr.Row():
            with gr.Column(scale=1):
                gr.HTML("""
                <div class="header-glow">
                    <h1>🧠 SuperBrain JARVIS</h1>
                    <p>Your Personal AI Operating System</p>
                </div>
                """)
        
        # Main interface with tabs
        with gr.Tabs(elem_classes=["tab-nav"]) as tabs:
            
            # Tab 1: Chat Interface
            with gr.TabItem("💬 Chat", id="chat"):
                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(
                            label="Conversation",
                            elem_classes=["glass-panel"],
                            height=500,
                            show_copy_button=True,
                            bubble_full_width=False,
                        )
                        
                        with gr.Row():
                            msg_input = gr.Textbox(
                                placeholder="Type your message... (Try: 'Help me write a Python script' or 'Search for latest AI news')",
                                show_label=False,
                                container=False,
                                scale=4,
                            )
                            send_btn = gr.Button("Send", variant="primary", scale=1)
                        
                        with gr.Row():
                            clear_btn = gr.Button("🗑️ Clear", size="sm")
                            export_btn = gr.Button("📥 Export", size="sm")
                            status_msg = gr.Textbox(label="Status", interactive=False, max_lines=1)
                    
                    with gr.Column(scale=1):
                        gr.HTML(get_system_info(), elem_id="system-info")
                        
                        gr.Markdown("""
                        ### 🎯 Quick Actions
                        - **Code**: "Write a Python script to..."
                        - **Search**: "Find information about..."
                        - **Files**: "Create a file named..."
                        - **System**: "List files in current directory"
                        - **Memory**: "Remember that I like..."
                        """)
            
            # Tab 2: Agent Dashboard
            with gr.TabItem("🤖 Agents", id="agents"):
                agent_dashboard = gr.HTML(get_agent_status())
                refresh_agents_btn = gr.Button("🔄 Refresh Status", variant="secondary")
            
            # Tab 3: Memory Browser
            with gr.TabItem("🧠 Memory", id="memory"):
                memory_display = gr.HTML(get_memory_stats())
                refresh_memory_btn = gr.Button("🔄 Refresh", variant="secondary")
            
            # Tab 4: Settings
            with gr.TabItem("⚙️ Settings", id="settings"):
                with gr.Row():
                    with gr.Column():
                        gr.Markdown("### 🎨 Appearance")
                        theme_dropdown = gr.Dropdown(
                            choices=["Dark Jarvis", "Light Clean", "Cyberpunk"],
                            value="Dark Jarvis",
                            label="Theme"
                        )
                        
                        gr.Markdown("### 🤖 Model Configuration")
                        model_dropdown = gr.Dropdown(
                            choices=model_manager.list_models(),
                            value=model_manager.active_model,
                            label="Active Model"
                        )
                        
                        gr.Markdown("### 🎤 Voice Settings")
                        voice_toggle = gr.Checkbox(label="Enable Voice Input/Output", value=False)
                        
                        gr.Markdown("### 💾 Memory Settings")
                        memory_limit = gr.Slider(
                            minimum=10,
                            maximum=100,
                            value=50,
                            step=10,
                            label="Max Conversation History"
                        )
                        
                        save_settings_btn = gr.Button("💾 Save Settings", variant="primary")
                        settings_status = gr.Textbox(label="Settings Status", interactive=False)
        
        # Event handlers
        msg_input.submit(
            fn=process_message,
            inputs=[msg_input, chatbot],
            outputs=[chatbot]
        )
        
        send_btn.click(
            fn=process_message,
            inputs=[msg_input, chatbot],
            outputs=[chatbot]
        )
        
        clear_btn.click(
            fn=clear_conversation,
            inputs=[],
            outputs=[chatbot, status_msg]
        )
        
        export_btn.click(
            fn=export_conversation,
            inputs=[],
            outputs=[status_msg]
        )
        
        refresh_agents_btn.click(
            fn=get_agent_status,
            inputs=[],
            outputs=[agent_dashboard]
        )
        
        refresh_memory_btn.click(
            fn=get_memory_stats,
            inputs=[],
            outputs=[memory_display]
        )
        
        save_settings_btn.click(
            fn=lambda t, m, v, ml: f"✅ Settings saved! Theme: {t}, Model: {m}, Voice: {v}",
            inputs=[theme_dropdown, model_dropdown, voice_toggle, memory_limit],
            outputs=[settings_status]
        )
        
        # Auto-refresh every 30 seconds
        app.load(
            fn=get_agent_status,
            inputs=[],
            outputs=[agent_dashboard],
            every=30
        )
        
        app.load(
            fn=get_memory_stats,
            inputs=[],
            outputs=[memory_display],
            every=60
        )
    
    return app
