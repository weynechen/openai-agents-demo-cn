"""
Dog Agent - Digital life simulation of a dog.

Features:
1. Interactive Mode: Responds to owner's commands and performs actions
2. Autonomous Mode: Autonomous behaviors based on internal states

Mode switching:
- Default: Autonomous mode
- Switches to Interactive mode when user inputs command
- Returns to Autonomous mode after 10 seconds of no input

32 behaviors across 6 categories:
- Physiological: stretch, yawn, drink, eat, groom, sleep
- Social: wag tail, nuzzle, lick hand, follow, look up
- Exploration: sniff, circle, paw, look out window, chase light
- Emotional: bark, growl, pin ears, tuck tail, jump
- Training: sit, lie down, shake, roll over, play dead, fetch
- Special: scratch, sneeze, shake body, snore, dream twitch
"""
import dump_promt


import dotenv
import os
import asyncio
import sys
import termios
import tty

dotenv.load_dotenv()

from agents import Agent, Runner, SQLiteSession
from agents.extensions.models.litellm_model import LitellmModel
from dog_state import DogStateManager
from dog_behaviors import get_all_behavior_tools, set_state_manager


class DogAgent:
    """Dog agent with autonomous and interactive modes"""
    
    def __init__(self, session_id: str = "dog_session"):
        # Initialize state manager
        self.state_manager = DogStateManager()
        set_state_manager(self.state_manager)
        
        # Initialize session
        self.session = SQLiteSession(session_id)
        
        # Mode tracking
        self.mode = "autonomous"  # autonomous or interactive
        
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
        
        # Input timeout
        self.input_timeout = 10  # seconds
    
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
    
    async def _get_user_input_with_timeout(self) -> str:
        """Get user input with timeout. Returns None if timeout."""
        # Flush any pending input
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
        
        try:
            # Run input in thread to avoid blocking
            user_input = await asyncio.wait_for(
                asyncio.to_thread(input, "You: "),
                timeout=self.input_timeout
            )
            return user_input.strip()
        except asyncio.TimeoutError:
            # Clear the line and move to next line
            print()  # Move to new line after timeout
            return None
    
    async def _run_autonomous_cycle(self):
        """Run one autonomous behavior cycle"""
        print(f"\n{'='*60}")
        print("🤖 [自主模式] 狗狗正在独立行动...")
        print(f"{'='*60}")
        
        # Update instructions for autonomous mode
        self.mode = "autonomous"
        self.agent.instructions = self._get_instructions()
        
        # Get state description
        state_desc = self.state_manager.get_state_description()
        prompt = f"{state_desc}\n\n你现在要做什么？"
        print(prompt)
        # Run agent
        result = await Runner.run(
            self.agent,
            prompt,
            session=self.session
        )
        
        # print(f"\n返回： {result.final_output}")
    
    async def _run_interactive_cycle(self, user_input: str):
        """Run interactive response to user input"""
        print(f"\n{'='*60}")
        print("👤 [交互模式] 正在回应主人...")
        print(f"{'='*60}")
        
        # Update instructions for interactive mode
        self.mode = "interactive"
        self.agent.instructions = self._get_instructions()
        
        # Get state description
        state_desc = self.state_manager.get_state_description()
        prompt = f"{state_desc}\n\n主人的动作/指令: {user_input}"
        
        # Run agent
        result = await Runner.run(
            self.agent,
            prompt,
            session=self.session
        )
        
        print(f"\n🐕 {result.final_output}")
    
    async def run(self):
        """Main run loop"""
        print("=" * 60)
        print("🐕 狗狗智能体已启动！")
        print("=" * 60)
        print("\n狗狗正安静地躺着...")
        print(self.state_manager.current_state.get_status_text())
        print("\n💡 提示:")
        print("  - 像和真狗说话一样自然交流（例如：'过来'、'坐下'、'好狗狗'）")
        print(f"  - 如果 {self.input_timeout} 秒内没有输入，狗狗会进入自主模式")
        print("  - 输入 'status' 查看狗狗当前状态")
        print("  - 输入 'exit' 或 'quit' 退出程序")
        print("=" * 60)
        
        try:
            while True:
                # Wait for user input with timeout
                print(f"\n[等待输入... ({self.input_timeout}秒后进入自主模式)]")
                user_input = await self._get_user_input_with_timeout()
                
                if user_input is None:
                    # Timeout - enter autonomous mode
                    await self._run_autonomous_cycle()
                    # Show updated state
                    print(self.state_manager.current_state.get_status_text())
                    # Flush stdin again before next input
                    termios.tcflush(sys.stdin, termios.TCIFLUSH)
                    await asyncio.sleep(1)  # Brief pause
                    
                elif user_input.lower() in ['exit', 'quit', 'q']:
                    print("\n👋 再见！你的狗狗会想念你的！")
                    break
                    
                elif user_input.lower() == 'status':
                    # Show status
                    print(self.state_manager.current_state.get_status_text())
                    
                elif user_input:
                    # User input - interactive mode
                    await self._run_interactive_cycle(user_input)
                    # Show updated state
                    print(self.state_manager.current_state.get_status_text())
                    
        except KeyboardInterrupt:
            print("\n\n👋 已中断。再见！")
        finally:
            self.state_manager.close()


async def main():
    """Main entry point"""
    dog = DogAgent()
    await dog.run()


if __name__ == "__main__":
    asyncio.run(main())
