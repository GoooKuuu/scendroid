#!/usr/bin/env python3
"""
Terminal TUI Interface for Layered Task Testing
Hierarchical tasktest interface implemented using the Textual framework

Top panel (60%): Conversation Panel — displays environment output, task information, and user interactions
Bottom panel (40%): Agent Trace Panel — displays the Agent execution process (reasoning and actions)
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal, ScrollableContainer
from textual.widgets import Header, Footer, Static, Input, Log, Button, Label
from textual.binding import Binding
from rich.text import Text
from rich.panel import Panel
import asyncio
from typing import Optional, Callable
from datetime import datetime


class ConversationPanel(Log):
    """Top panel: Conversation and environment output panel"""
    
    def __init__(self):
        super().__init__(highlight=True, auto_scroll=True)
    
    def log_system(self, message: str, icon: str = "📋"):
        """System message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.write_line(f"{timestamp} {icon} System: {message}")
        self.refresh()
    
    def log_success(self, message: str):
        """successmessage"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.write_line(f"{timestamp} ✅ Success: {message}")
        self.refresh()
    
    def log_warning(self, message: str):
        """warningmessage"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.write_line(f"{timestamp} ⚠️  Warning: {message}")
        self.refresh()
    
    def log_error(self, message: str):
        """errormessage"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.write_line(f"{timestamp} ❌ Error: {message}")
        self.refresh()
    
    def log_task_info(self, task_id: int, name: str, level: str, instruction: str):
        """taskinfo"""
        self.write_line("\n" + "─" * 60)
        self.write_line(f"🎯 Task Selected")
        self.write_line(f"   ID: {task_id}")
        self.write_line(f"   Name: {name}")
        self.write_line(f"   Level: {level}")
        self.write_line(f"   Instruction: {instruction}")
        self.write_line("─" * 60 + "\n")
        self.refresh()
    
    def log_user_input(self, message: str):
        """User input"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.write_line(f"{timestamp} 💬 User: {message}")
        self.refresh()
    
    def log_question(self, question: str):
        """Agent question"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.write_line(f"{timestamp} ❓ Agent Question: {question}")
        self.refresh()

    def log_evaluation_start(self):
        """startevaluation"""
        self.write_line("\n" + "═" * 60)
        self.write_line("🔍 Evaluation Phase")
        self.write_line("═" * 60)
        self.refresh()
    
    def log_evaluation_result(self, score: float, passed: bool, details: str = ""):
        """evaluation result"""
        status = "✅ PASSED" if passed else "❌ FAILED"
        self.write_line(f"\n📊 Evaluation Result:")
        self.write_line(f"   Score: {score:.2f}")
        self.write_line(f"   Status: {status}")
        if details:
            self.write_line(f"   Details: {details}")
        self.write_line("═" * 60 + "\n")
        self.refresh()
    
    def show_separator(self, title: str = ""):
        """Display separator line"""
        if title:
            self.write_line(f"\n{'─' * 20} {title} {'─' * 20}\n")
        else:
            self.write_line("\n" + "─" * 60 + "\n")
        self.refresh()


class AgentTracePanel(Log):
    """Bottom panel: Agent execution trace panel"""
    
    def __init__(self):
        super().__init__(highlight=True, auto_scroll=True)
        self.step_count = 0
        self.task_running = False
    
    def start_task(self):
        """starttask"""
        self.task_running = True
        self.write_line("🚀 Agent Started")
        self.write_line("")
        self.refresh()
    
    def end_task(self, success: bool = True):
        """endtask"""
        self.task_running = False
        self.write_line("")
        if success:
            self.write_line("✅ Agent Task Completed")
        else:
            self.write_line("❌ Agent Task Failed")
        self.refresh()
    
    def log_thought(self, thought: str):
        """Agent reasoning"""
        self.step_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.write_line(f"{timestamp} [Step {self.step_count}] 💭 Thought:")
        self.write_line(f"   {thought}")
        self.refresh()
    
    def log_action(self, action: str, details: str = ""):
        """Agent action"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.write_line(f"{timestamp} [Step {self.step_count}] 🎬 Action: {action}")
        if details:
            self.write_line(f"   {details}")
        self.refresh()
    
    def log_observation(self, observation: str):
        """Observation result"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.write_line(f"{timestamp} [Step {self.step_count}] 👁️  Observation:")
        self.write_line(f"   {observation}")
        self.write_line("")
        self.refresh()
    
    def log_result(self, result: str, success: bool = True):
        """Action result"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = "✅" if success else "❌"
        self.write_line(f"{timestamp} [Step {self.step_count}] {icon} Result: {result}")
        self.write_line("")
        self.refresh()
    
    def log_error(self, error: str):
        """errorinfo"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.write_line(f"{timestamp} [Step {self.step_count}] ❌ Error: {error}")
        self.write_line("")
        self.refresh()
    
    def log_status(self, status: str):
        """Overall status"""
        self.write_line(f"Status: {status}")
        self.refresh()
    
    def reset(self):
        """Reset step count"""
        self.step_count = 0
        self.task_running = False
        self.clear()


class LayeredTaskTUI(App):
    """Hierarchical tasktest TUI application"""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    
    #top_container {
        height: 60%;
        border: solid cyan;
        background: $surface;
    }
    
    #conversation_panel {
        height: 100%;
        padding: 1;
        background: $surface;
    }
    
    #bottom_container {
        height: 38%;
        border: solid magenta;
        background: $surface;
    }
    
    #agent_panel {
        height: 100%;
        padding: 1;
        background: $surface;
    }
    
    #input_container {
        height: auto;
        dock: bottom;
        background: $panel;
        padding: 0 1;
    }
    
    #input_box {
        width: 85%;
    }
    
    #send_btn {
        width: 15%;
        min-width: 10;
    }
    
    Header {
        background: $accent;
    }
    
    Footer {
        background: $panel;
    }
    
    .label-title {
        width: 100%;
        background: $boost;
        color: $text;
        padding: 0 1;
        text-style: bold;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("ctrl+l", "clear_logs", "Clear Logs"),
        Binding("ctrl+r", "reset_agent", "Reset Agent"),
        Binding("ctrl+s", "save_logs", "Save Logs", show=True),
        Binding("ctrl+d", "show_debug_log", "Show Debug Log", show=True),
        Binding("f1", "show_help", "Help"),
    ]
    
    TITLE = "🎯 Layered Task Testing System"
    SUB_TITLE = "Terminal User Interface"
    
    def __init__(self):
        super().__init__()
        self.conversation_panel: Optional[ConversationPanel] = None
        self.agent_panel: Optional[AgentTracePanel] = None
        self.input_widget: Optional[Input] = None
        
        # Callback function (for external registration)
        self.on_user_message_callback: Optional[Callable] = None
        
        # Message queue (for asynchronous communication)
        self.message_queue = asyncio.Queue()
    
    def compose(self) -> ComposeResult:
        """Create UI components"""
        yield Header()
        
        # Top panel: Conversation panel
        with Container(id="top_container"):
            yield Label("🌐 Conversation Panel", classes="label-title")
            conversation_panel = ConversationPanel()
            self.conversation_panel = conversation_panel
            yield conversation_panel
        
        # Bottom panel: Agent trace panel
        with Container(id="bottom_container"):
            yield Label("🤖 Agent Trace Panel", classes="label-title")
            agent_panel = AgentTracePanel()
            self.agent_panel = agent_panel
            yield agent_panel
        
        # Bottom input field
        with Horizontal(id="input_container"):
            input_widget = Input(
                placeholder="Input message, answer questions or issue commands...",
                id="input_box"
            )
            self.input_widget = input_widget
            yield input_widget
            yield Button("send", id="send_btn", variant="primary")
        
        yield Footer()
    
    def on_mount(self):
        """initialize"""
        try:
            self.conversation_panel.log_system("🚀 Hierarchical tasktest system started", icon="🎉")
            self.conversation_panel.log_system("Press Ctrl+C to exit, Ctrl+L to clear logs, F1 for help", icon="💡")
            self.conversation_panel.show_separator()
            self.input_widget.focus()
        except Exception as e:
            # If an error occurs, at least display something
            import traceback
            self.conversation_panel.write_line(f"❌ initializeerror: {e}")
            self.conversation_panel.write_line(traceback.format_exc())
    
    def on_button_pressed(self, event: Button.Pressed):
        """Send button click"""
        if event.button.id == "send_btn":
            self.handle_user_input()
    
    def on_input_submitted(self, event: Input.Submitted):
        """Input field Enter key press"""
        self.handle_user_input()
    
    def handle_user_input(self):
        """Handle user input"""
        message = self.input_widget.value.strip()
        if not message:
            return
        
        # Display user input
        self.conversation_panel.log_user_input(message)
        self.input_widget.value = ""
        
        # Place message into queue
        try:
            asyncio.create_task(self.message_queue.put(message))
        except Exception as e:
            self.conversation_panel.log_error(f"messagequeueerror: {e}")
        
        # If a callback is registered, invoke it
        if self.on_user_message_callback:
            try:
                self.on_user_message_callback(message)
            except Exception as e:
                self.conversation_panel.log_error(f"Error handling message: {e}")
                import traceback
                self.conversation_panel.write_line(traceback.format_exc())
    
    def action_clear_logs(self):
        """clearlog"""
        self.conversation_panel.clear()
        self.agent_panel.clear()
        self.conversation_panel.log_system("Logs cleared", icon="🧹")
    
    def action_reset_agent(self):
        """Reset Agent panel"""
        self.agent_panel.reset()
        self.conversation_panel.log_system("Agent panel reset", icon="🔄")
    
    def action_save_logs(self):
        """Save logs to file"""
        import datetime
        import os
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_dir = "tui_logs"
        
        # createlogdirectory
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        log_file = os.path.join(log_dir, f"tui_log_{timestamp}.txt")
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("Conversation Panel Log\n")
                f.write("=" * 80 + "\n\n")
                
                # Get text content of the Conversation Panel
                if self.conversation_panel:
                    # The lines property of the Log widget contains all log lines
                    for line in self.conversation_panel._lines:
                        f.write(line + "\n")
                
                f.write("\n" + "=" * 80 + "\n")
                f.write("Agent Trace Panel Log\n")
                f.write("=" * 80 + "\n\n")
    
                # Get text content of the Agent Panel
                if self.agent_panel:
                    for line in self.agent_panel._lines:
                        f.write(line + "\n")
                
                # ✅ Append background debug log
                f.write("\n" + "=" * 80 + "\n")
                f.write("Backend Debug Log (tui_debug.log)\n")
                f.write("=" * 80 + "\n\n")
                
                try:
                    if os.path.exists("tui_debug.log"):
                        with open("tui_debug.log", 'r', encoding='utf-8') as debug_f:
                            f.write(debug_f.read())
                    else:
                        f.write("(No debug log file found)\n")
                except Exception as e:
                    f.write(f"(Error reading debug log: {e})\n")
            
            self.conversation_panel.log_success(f"log saved to: {log_file}")
            self.conversation_panel.write_line("💡 Tip: Includes TUI display content and background debug log")
            self.conversation_panel.write_line("💡 You can open this file with a text editor to view the complete log")
            
        except Exception as e:
            self.conversation_panel.log_error(f"savelogfailed: {e}")
    
    def action_show_debug_log(self):
        """Display the last few lines of the background debug log"""
        import os
        
        try:
            if not os.path.exists("tui_debug.log"):
                self.conversation_panel.log_warning("not founddebuglogfile tui_debug.log")
                return
            
            # Read the last 50 lines
            with open("tui_debug.log", 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Display the last 50 lines
            last_lines = lines[-50:] if len(lines) > 50 else lines
            
            self.conversation_panel.show_separator("Backend Debug Log (Last 50 lines)")
            self.conversation_panel.write_line("")
            
            for line in last_lines:
                self.conversation_panel.write_line(line.rstrip())
            
            self.conversation_panel.write_line("")
            self.conversation_panel.show_separator()
            self.conversation_panel.write_line(f"💡 Complete log file: tui_debug.log (total {len(lines)} lines)")
            self.conversation_panel.write_line("💡 Press Ctrl+S to save a file containing the complete background log")
            
        except Exception as e:
            self.conversation_panel.log_error(f"Failed to read debug log: {e}")
            import traceback
            self.conversation_panel.write_line(traceback.format_exc())
    
    def action_show_help(self):
        """Display help"""
        self.conversation_panel.show_separator("Keyboard Shortcut Help")
        self.conversation_panel.write_line("Ctrl+C - Exit the program")
        self.conversation_panel.write_line("Ctrl+L - Clear all logs")
        self.conversation_panel.write_line("Ctrl+R - Reset the Agent panel")
        self.conversation_panel.write_line("Ctrl+S - Save logs to a file (including background debug log)")
        self.conversation_panel.write_line("Ctrl+D - Display the background debug log (last 50 lines)")
        self.conversation_panel.write_line("F1 - Display this help")
        self.conversation_panel.write_line("Enter - sendmessage")
        self.conversation_panel.write_line("")
        self.conversation_panel.write_line("💡 Tip: Background error information is in the tui_debug.log file")
        self.conversation_panel.write_line("💡 Press Ctrl+D to view the most recent background logs")
        self.conversation_panel.show_separator()
    
    # ========== External APIs (for calling by existing code) ==========
    
    def show_task_list(self, tasks: list):
        """show task list"""
        self.conversation_panel.log_system(f"Total {len(tasks)} tasks available", icon="📚")
        self.conversation_panel.show_separator("task list")
        
        # Group and display by app
        apps = {}
        for task in tasks:
            if task.app not in apps:
                apps[task.app] = []
            apps[task.app].append(task)
        
        for app, app_tasks in sorted(apps.items()):
            self.conversation_panel.write_line("")
            self.conversation_panel.write_line(f"📱 {app} ({len(app_tasks)} task):")
            for task in app_tasks:
                l0 = task.get_instruction('L0')
                if len(l0) > 50:
                    l0 = l0[:47] + "..."
                self.conversation_panel.write_line(f"  [{task.task_id}] {task.name}")
                self.conversation_panel.write_line(f"      {l0}")
        
        self.conversation_panel.show_separator()
    
    def show_task_details(self, task, level: str):
        """Display task details"""
        instruction = task.get_instruction(level)
        self.conversation_panel.log_task_info(
            task.task_id, task.name, level, instruction
        )
        
        # Display additional information
        level_data = task.levels[level]
        if level_data.missing:
            self.conversation_panel.write_line("⚠️  Missing Information:")
            for missing in level_data.missing:
                self.conversation_panel.write_line(f"   - {missing}")
            self.conversation_panel.write_line("")
        
        # Display L0 Ground Truth
        l0_instruction = task.get_l0_instruction()
        self.conversation_panel.write_line("✅ Ground Truth (L0):")
        self.conversation_panel.write_line(f"   {l0_instruction}")
        self.conversation_panel.write_line("")
    
    def log_initialization(self, message: str, success: bool = None):
        """Log the initialization process"""
        if success is True:
            self.conversation_panel.log_success(message)
        elif success is False:
            self.conversation_panel.log_error(message)
        else:
            self.conversation_panel.log_system(message, icon="⚙️")
    
    def log_agent_step(self, thought: str = None, action: str = None, 
                       observation: str = None, result: str = None, 
                       success: bool = True):
        """Log Agent execution step (flexible parameters)"""
        if thought:
            self.agent_panel.log_thought(thought)
        if action:
            self.agent_panel.log_action(action)
        if observation:
            self.agent_panel.log_observation(observation)
        if result:
            self.agent_panel.log_result(result, success)
    
    def start_agent_execution(self):
        """startAgentexecute"""
        self.agent_panel.start_task()
    
    def end_agent_execution(self, success: bool = True):
        """endAgentexecute"""
        self.agent_panel.end_task(success)
    
    def show_evaluation_result(self, score: float, passed: bool, details: str = ""):
        """Display evaluation result"""
        self.conversation_panel.log_evaluation_start()
        self.conversation_panel.log_evaluation_result(score, passed, details)
    
    def reset_agent_panel(self):
        """Reset Agent panel"""
        self.agent_panel.reset()
    
    def ask_question(self, question: str):
        """Agent asks a question (e.g., awaiting user response)"""
        self.conversation_panel.log_question(question)
        self.input_widget.focus()
    
    async def wait_for_user_input(self) -> str:
        """e.g., await user input (asynchronous)"""
        message = await self.message_queue.get()
        return message
    
    def register_message_callback(self, callback: Callable):
        """Register message handler callback"""
        self.on_user_message_callback = callback


# ========== Convenient global instance and helper functions ==========

# Global TUI instance (singleton)
_tui_instance: Optional[LayeredTaskTUI] = None


def get_tui() -> LayeredTaskTUI:
    """Get the global TUI instance"""
    global _tui_instance
    if _tui_instance is None:
        _tui_instance = LayeredTaskTUI()
    return _tui_instance


def init_tui() -> LayeredTaskTUI:
    """initializeTUIinstance"""
    global _tui_instance
    _tui_instance = LayeredTaskTUI()
    return _tui_instance


# ========== Demo program ==========

async def demo_run():
    """Demonstrate TUI functionality"""
    tui = init_tui()
    
    async def simulate_task():
        """Simulate task execution"""
        await asyncio.sleep(1)
        
        # Simulate task list
        class MockTask:
            def __init__(self, task_id, name, app):
                self.task_id = task_id
                self.name = name
                self.app = app
                self.levels = {
                    'L0': type('obj', (object,), {
                        'instruction': f'Open {app} app and do something',
                        'missing': None
                    })()
                }
            def get_instruction(self, level):
                return self.levels['L0'].instruction
            def get_l0_instruction(self):
                return self.levels['L0'].instruction
        
        tasks = [
            MockTask(1, "SetAlarm", "Clock"),
            MockTask(2, "SetBrightness", "Settings"),
            MockTask(3, "CreateMeeting", "Calendar"),
        ]
        
        # show task list
        tui.show_task_list(tasks)
        
        await asyncio.sleep(2)
        
        # Display task details
        tui.show_task_details(tasks[0], 'L0')
        
        await asyncio.sleep(1)
        
        # Simulate initialize
        tui.log_initialization("Initializing environment...")
        await asyncio.sleep(0.5)
        tui.log_initialization("✅ environmentinitializecomplete", success=True)
        
        await asyncio.sleep(1)
        
        # Simulate Agent execute
        tui.start_agent_execution()
        
        await asyncio.sleep(1)
        tui.log_agent_step(
            thought="I need to open the Clock app to set up an alarm",
            action="click(element='Clock App Icon')"
        )
        
        await asyncio.sleep(2)
        tui.log_agent_step(
            observation="The Clock app is open, displaying the current alarm list",
            result="Successfully opened app",
            success=True
        )
        
        await asyncio.sleep(2)
        tui.log_agent_step(
            thought="Now I need to click the Add Alarm button",
            action="click(element='Add Alarm Button')"
        )
        
        await asyncio.sleep(2)
        tui.log_agent_step(
            observation="The New Alarm Setup dialog is open",
            result="Dialog displayed",
            success=True
        )
        
        await asyncio.sleep(2)
        tui.log_agent_step(
            thought="Set alarm time to 8:00 AM",
            action="set_time(hour=8, minute=0, period='AM')"
        )
        
        await asyncio.sleep(1)
        tui.log_agent_step(
            result="Time set to 8:00 AM",
            success=True
        )
        
        await asyncio.sleep(1)
        tui.end_agent_execution(success=True)
        
        # Display evaluation result
        await asyncio.sleep(1)
        tui.show_evaluation_result(
            score=1.0, 
            passed=True, 
            details="All checkpoints passed: alarm time is correct, status is enabled"
        )
    
    # Run simulated task in background
    asyncio.create_task(simulate_task())
    
    # Run TUI application
    await tui.run_async()


if __name__ == "__main__":
    print("🚀 Launching TUI demo program...")
    print("💡 Tip: Press Ctrl+C to exit, F1 to view help\n")
    asyncio.run(demo_run())
