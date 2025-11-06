"""
Dog Agent with Gradio UI - Digital life simulation of a dog.

Features:
1. Interactive Mode: Responds to owner's commands via Gradio chat interface
2. Autonomous Mode: Autonomous behaviors triggered by timer when no interaction
3. Real-time state monitoring
"""
import dump_promt

import dotenv
import os
import asyncio
import time
import threading

dotenv.load_dotenv()

import gradio as gr
from agents import Agent, Runner, SQLiteSession
from agents.extensions.models.litellm_model import LitellmModel
from dog_state import DogStateManager
from dog_behaviors import get_all_behavior_tools, set_state_manager


class DogAgentGradio:
    """Dog agent with Gradio UI"""
    
    def __init__(self, session_id: str = "dog_session_gradio"):
        print("[INIT] Initializing Dog Agent...")
        
        # Initialize state manager
        self.state_manager = DogStateManager()
        set_state_manager(self.state_manager)
        
        # Initialize session
        self.session = SQLiteSession(session_id)
        
        # Mode tracking
        self.mode = "autonomous"  # autonomous or interactive
        self.last_interaction_time = time.time()
        self.autonomous_interval = 15  # seconds before triggering autonomous mode
        
        # Create agent
        self.agent = Agent(
            name="Dog",
            instructions=self._get_instructions(),
            tools=get_all_behavior_tools(),
            model=LitellmModel(
                model="deepseek/deepseek-chat",
                api_key=os.getenv("DEEPSEEK_API_KEY")
            )
        )
        
        # Background task flag
        self.running = True
        self.autonomous_task = None
        
        # Current activity tracking
        self.current_activity = "🛌 狗狗正安静地躺着..."
        self.last_activity_time = time.time()
        
        print("[INIT] Dog Agent initialized successfully!")
    
    def _get_instructions(self) -> str:
        """Get dynamic instructions based on mode"""
        base = """你现在是一条狗。你可以使用可用的工具来执行各种行为。

重要规则：
1. 你必须使用工具来执行动作 - 调用相应的工具函数
2. 不要只用文字描述动作，你必须调用工具
3. 你可以按顺序调用多个工具来创建自然的行为组合
4. 保持回复简洁 - 专注于行动，不要长篇解释

可用行为类别：
- 生理类: stretch, yawn, drink_water, eat_food, lick_fur, sleep
- 社交类: wag_tail, nuzzle_owner, lick_hand, follow_owner, look_up_at_owner
- 探索类: sniff_ground, walk_in_circles, paw_at_object, look_out_window, chase_light
- 情绪类: bark, growl, pin_ears_back, tuck_tail, jump_excitedly
- 训练类: sit, lie_down, shake_paw, roll_over, play_dead, fetch_object
- 特殊类: scratch_itch, sneeze, shake_body, snore, dream_twitch

"""
        
        if self.mode == "autonomous":
            return base + """模式：自主模式
你正在根据内部需求独立行动。

根据你当前的状态决定做什么：
- 如果饿了 (>70): eat_food
- 如果渴了 (>70): drink_water
- 如果累了 (>80): sleep
- 如果无聊 (>70): 探索或玩耍 (sniff, chase_light, paw_at_object, 等)
- 如果有多个需求: 优先处理数值最高的
- 否则: 执行日常行为 (stretch, yawn, walk_in_circles, 等)

执行 1-3 个相关的、合理的动作组合。"""
        else:  # interactive
            return base + """模式：交互模式
你正在回应主人的指令和互动。

例子：
主人: "过来"
-> 你: look_up_at_owner(), wag_tail(), follow_owner()

主人: "坐下"
-> 你: sit()

主人: "好狗狗！" (抚摸你)
-> 你: wag_tail(), lick_hand(), jump_excitedly()

主人: "去捡球"
-> 你: jump_excitedly(), fetch_object()

通过调用适当的工具自然地回应主人的指令。"""
    
    async def _run_autonomous_cycle(self):
        """Run one autonomous behavior cycle"""
        print("\n" + "="*60)
        print("[AUTONOMOUS] Dog is acting independently...")
        print("="*60)
        
        # Update instructions for autonomous mode
        self.mode = "autonomous"
        self.agent.instructions = self._get_instructions()
        
        # Get state description
        state_desc = self.state_manager.get_state_description()
        prompt = f"{state_desc}\n\n你现在要做什么？"
        
        print(f"[PROMPT] {prompt}")
        
        # Run agent
        result = await Runner.run(
            self.agent,
            prompt,
            session=self.session
        )
        
        output = f"[自主行为] {result.final_output}"
        print(f"[OUTPUT] {output}")
        
        # Update current activity
        self.current_activity = f"🤖 [自主] {result.final_output}"
        self.last_activity_time = time.time()
        
        return output
    
    async def _run_interactive_cycle(self, user_input: str):
        """Run interactive response to user input"""
        print("\n" + "="*60)
        print(f"[INTERACTIVE] Responding to owner: {user_input}")
        print("="*60)
        
        # Update instructions for interactive mode
        self.mode = "interactive"
        self.agent.instructions = self._get_instructions()
        
        # Get state description
        state_desc = self.state_manager.get_state_description()
        prompt = f"{state_desc}\n\n主人的动作/指令: {user_input}"
        
        print(f"[PROMPT] {prompt}")
        
        # Run agent
        result = await Runner.run(
            self.agent,
            prompt,
            session=self.session
        )
        
        output = result.final_output
        print(f"[OUTPUT] {output}")
        
        # Update current activity
        self.current_activity = f"👤 [交互] {output}"
        self.last_activity_time = time.time()
        
        return output
    
    def get_state_display(self):
        """Get current state as HTML for display"""
        state = self.state_manager.current_state
        self.state_manager.update_state_by_time()
        
        # Determine emoji based on happiness
        mood_emoji = '😊' if state.happiness > 70 else '😐' if state.happiness > 30 else '😞'
        
        html = f"""
        <div style="padding: 15px; background: #f0f0f0; border-radius: 10px; font-family: monospace;">
            <h3 style="margin-top: 0;">🐕 狗狗状态 {mood_emoji}</h3>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div>
                    <b>饥饿值:</b> {state.hunger:.1f}/100 {'⚠️' if state.hunger > 70 else ''}
                </div>
                <div>
                    <b>口渴值:</b> {state.thirst:.1f}/100 {'⚠️' if state.thirst > 70 else ''}
                </div>
                <div>
                    <b>疲劳值:</b> {state.fatigue:.1f}/100 {'⚠️' if state.fatigue > 70 else ''}
                </div>
                <div>
                    <b>无聊值:</b> {state.boredom:.1f}/100 {'⚠️' if state.boredom > 70 else ''}
                </div>
                <div style="grid-column: 1 / -1;">
                    <b>快乐值:</b> {state.happiness:.1f}/100
                </div>
            </div>
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ccc;">
                <b>模式:</b> {'🤖 自主模式' if self.mode == 'autonomous' else '👤 交互模式'}
            </div>
        </div>
        """
        return html
    
    def get_current_activity(self):
        """Get current activity text"""
        # Check if activity is recent (within last 30 seconds)
        time_since_activity = time.time() - self.last_activity_time
        if time_since_activity > 30:
            return "🛌 狗狗正安静地躺着..."
        return self.current_activity
    
    def user_message(self, user_input, history):
        """Handle user message"""
        if not user_input.strip():
            return history, ""
        
        print(f"\n[USER INPUT] {user_input}")
        
        # Update last interaction time
        self.last_interaction_time = time.time()
        
        # Add user message to history
        history = history + [[user_input, None]]
        return history, ""
    
    async def bot_response(self, history):
        """Generate bot response"""
        if not history or history[-1][1] is not None:
            return history
        
        user_input = history[-1][0]
        
        # Check for special commands
        if user_input.lower() in ['exit', 'quit', 'q']:
            history[-1][1] = "👋 再见！下次再来陪我玩！"
            return history
        
        # Run interactive cycle
        response = await self._run_interactive_cycle(user_input)
        history[-1][1] = response
        
        return history
    
    async def autonomous_behavior_loop(self):
        """Background loop for autonomous behavior"""
        print("[BACKGROUND] Autonomous behavior loop started")
        
        while self.running:
            await asyncio.sleep(3)  # Check every 3 seconds
            
            # Check if it's time for autonomous behavior
            time_since_last = time.time() - self.last_interaction_time
            
            if time_since_last >= self.autonomous_interval:
                print(f"[TRIGGER] {time_since_last:.1f}s since last interaction, triggering autonomous mode")
                
                # Run autonomous cycle
                await self._run_autonomous_cycle()
                
                # Reset timer
                self.last_interaction_time = time.time()
    
    def start_autonomous_task(self):
        """Start the autonomous behavior background task"""
        if self.autonomous_task is None:
            loop = asyncio.new_event_loop()
            
            def run_loop():
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.autonomous_behavior_loop())
            
            self.autonomous_task = threading.Thread(target=run_loop, daemon=True)
            self.autonomous_task.start()
            print("[TASK] Autonomous task started in background")
    
    def stop(self):
        """Stop the agent"""
        print("[STOP] Stopping Dog Agent...")
        self.running = False
        self.state_manager.close()
    
    def create_ui(self):
        """Create Gradio UI"""
        with gr.Blocks(title="🐕 狗狗智能体", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 🐕 狗狗智能体 - 数字生命模拟")
            gr.Markdown("和你的虚拟狗狗互动！它会根据你的指令做出反应，也会在无聊时自己做些事情。")
            
            # Add a timer for auto-refresh (ticks every 5 seconds)
            timer = gr.Timer(value=5, active=True)
            
            with gr.Row():
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(
                        label="与狗狗对话",
                        height=500,
                        show_copy_button=True,
                        type='tuples'
                    )
                    
                    with gr.Row():
                        msg = gr.Textbox(
                            label="输入指令",
                            placeholder="试试说：'过来'、'坐下'、'好狗狗'、'去捡球'...",
                            scale=4
                        )
                        submit = gr.Button("发送", variant="primary", scale=1)
                    
                    with gr.Row():
                        clear = gr.Button("清空对话", scale=1)
                        refresh_state = gr.Button("刷新状态", scale=1)
                
                with gr.Column(scale=1):
                    # Current activity display
                    activity_display = gr.Textbox(
                        value=self.get_current_activity(),
                        label="🐾 当前行为",
                        lines=3,
                        max_lines=5,
                        interactive=False,
                        show_copy_button=False
                    )
                    
                    state_display = gr.HTML(
                        value=self.get_state_display(),
                        label="狗狗状态"
                    )
                    
                    gr.Markdown("""
                    ### 💡 使用提示
                    - 像和真狗说话一样自然交流
                    - 15秒无互动会触发自主模式
                    - 狗狗会根据内部状态自主行动
                    - 所有行为都会影响狗狗的状态
                    
                    ### 🎮 试试这些指令
                    - "过来" / "坐下" / "趴下"
                    - "握手" / "打滚" / "装死"
                    - "去捡球" / "好狗狗"
                    - "摸摸你" / "陪我玩"
                    """)
            
            # Event handlers
            def submit_and_respond(user_input, history):
                # Add user message
                history, _ = self.user_message(user_input, history)
                # Get bot response synchronously
                history = asyncio.run(self.bot_response(history))
                return history, "", self.get_current_activity(), self.get_state_display()
            
            msg.submit(
                submit_and_respond,
                [msg, chatbot],
                [chatbot, msg, activity_display, state_display]
            )
            
            submit.click(
                submit_and_respond,
                [msg, chatbot],
                [chatbot, msg, activity_display, state_display]
            )
            
            clear.click(
                lambda: ([], self.get_current_activity(), self.get_state_display()),
                None,
                [chatbot, activity_display, state_display]
            )
            
            refresh_state.click(
                lambda: (self.get_current_activity(), self.get_state_display()),
                None,
                [activity_display, state_display]
            )
            
            # Auto-refresh state and activity with timer
            timer.tick(
                lambda: (self.get_current_activity(), self.get_state_display()),
                None,
                [activity_display, state_display]
            )
        
        return demo


def main():
    """Main entry point"""
    print("="*60)
    print("🐕 Starting Dog Agent with Gradio UI")
    print("="*60)
    
    # Create agent
    dog_agent = DogAgentGradio()
    
    # Start autonomous behavior task
    dog_agent.start_autonomous_task()
    
    # Create and launch UI
    demo = dog_agent.create_ui()
    
    try:
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False
        )
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Shutting down...")
    finally:
        dog_agent.stop()


if __name__ == "__main__":
    main()

