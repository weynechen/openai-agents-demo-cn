"""
Dog behavior tools - 32 behaviors across 6 categories.
Each behavior is a function_tool that modifies dog state.
"""

from agents import function_tool
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dog_state import DogStateManager

# Global state manager (will be set by main program)
state_manager: 'DogStateManager' = None


def set_state_manager(manager: 'DogStateManager'):
    """Set the global state manager"""
    global state_manager
    state_manager = manager


def _log_behavior(message: str) -> str:
    """Log behavior action to console"""
    print(f"  🐾 {message}")
    return message


# ==================== Physiological Behaviors ====================

@function_tool
def stretch() -> str:
    """Dog stretches body"""
    state_manager.modify_state(fatigue=-3, happiness=2)
    return _log_behavior("伸懒腰，前腿向前伸展...感觉舒服多了！")


@function_tool
def yawn() -> str:
    """Dog yawns"""
    state_manager.modify_state(fatigue=-2)
    return _log_behavior("张大嘴巴...哈~~~欠~")


@function_tool
def drink_water() -> str:
    """Dog drinks water"""
    state_manager.modify_state(thirst=-30, happiness=5)
    return _log_behavior("走向水碗...舔舔舔...解渴了！")


@function_tool
def eat_food() -> str:
    """Dog eats food"""
    state_manager.modify_state(hunger=-40, happiness=10, boredom=-5)
    return _log_behavior("从碗里吃东西...咀嚼咀嚼...真好吃！")


@function_tool
def lick_fur() -> str:
    """Dog licks and grooms fur"""
    state_manager.modify_state(happiness=3, boredom=-2)
    return _log_behavior("舔爪子梳理毛发...保持干净！")


@function_tool
def sleep() -> str:
    """Dog sleeps"""
    state_manager.modify_state(fatigue=-50, boredom=-10, hunger=5)
    return _log_behavior("蜷缩起来...闭上眼睛...zzz...(安详地睡着了)")


# ==================== Social Behaviors ====================

@function_tool
def wag_tail() -> str:
    """Dog wags tail happily"""
    state_manager.modify_state(happiness=5)
    return _log_behavior("尾巴兴奋地摇摆！好开心！")


@function_tool
def nuzzle_owner() -> str:
    """Dog nuzzles against owner"""
    state_manager.modify_state(happiness=8, boredom=-5)
    return _log_behavior("用头蹭主人的腿...寻求关注！")


@function_tool
def lick_hand() -> str:
    """Dog licks owner's hand"""
    state_manager.modify_state(happiness=7, boredom=-3)
    return _log_behavior("深情地舔主人的手...表达爱意！")


@function_tool
def follow_owner() -> str:
    """Dog follows owner around"""
    state_manager.modify_state(happiness=5, boredom=-5)
    return _log_behavior("紧紧跟随主人...待在主人身边！")


@function_tool
def look_up_at_owner() -> str:
    """Dog looks up at owner"""
    state_manager.modify_state(happiness=3)
    return _log_behavior("用大眼睛抬头看着主人...等待关注！")


# ==================== Exploration Behaviors ====================

@function_tool
def sniff_ground() -> str:
    """Dog sniffs the ground"""
    state_manager.modify_state(boredom=-8, fatigue=2)
    return _log_behavior("鼻子贴着地面...到处闻闻...调查中！")


@function_tool
def walk_in_circles() -> str:
    """Dog walks in circles"""
    state_manager.modify_state(boredom=-5, fatigue=3)
    return _log_behavior("绕圈走...探索空间！")


@function_tool
def paw_at_object() -> str:
    """Dog paws at objects"""
    state_manager.modify_state(boredom=-10, happiness=5)
    return _log_behavior("用爪子扒有趣的东西...调查中！")


@function_tool
def look_out_window() -> str:
    """Dog looks out the window"""
    state_manager.modify_state(boredom=-12, happiness=5)
    return _log_behavior("看向窗外...观察外面的世界！")


@function_tool
def chase_light() -> str:
    """Dog chases light reflections"""
    state_manager.modify_state(boredom=-15, fatigue=8, happiness=10)
    return _log_behavior("追逐光点！兴奋地跑来跑去！")


# ==================== Emotional Expression ====================

@function_tool
def bark() -> str:
    """Dog barks"""
    state_manager.modify_state(boredom=-5)
    return _log_behavior("汪！汪！(吠叫)")


@function_tool
def growl() -> str:
    """Dog growls softly"""
    state_manager.modify_state(happiness=-5)
    return _log_behavior("呜呜...(低吼声)")


@function_tool
def pin_ears_back() -> str:
    """Dog pins ears back (nervous/submissive)"""
    state_manager.modify_state(happiness=-3)
    return _log_behavior("耳朵贴向脑后...感到不安")


@function_tool
def tuck_tail() -> str:
    """Dog tucks tail between legs (scared/submissive)"""
    state_manager.modify_state(happiness=-5)
    return _log_behavior("尾巴夹在两腿之间...感到害怕或顺从")


@function_tool
def jump_excitedly() -> str:
    """Dog jumps up and down excitedly"""
    state_manager.modify_state(happiness=8, boredom=-10, fatigue=5)
    return _log_behavior("上下跳跃！太兴奋了！蹦蹦跳跳！")


# ==================== Training Actions ====================

@function_tool
def sit() -> str:
    """Dog sits down"""
    state_manager.modify_state(happiness=5, fatigue=-3)
    return _log_behavior("乖乖坐下...尾巴摇摆！")


@function_tool
def lie_down() -> str:
    """Dog lies down"""
    state_manager.modify_state(fatigue=-5, happiness=3)
    return _log_behavior("平躺在地上...休息！")


@function_tool
def shake_paw() -> str:
    """Dog offers paw to shake"""
    state_manager.modify_state(happiness=8, boredom=-5)
    return _log_behavior("抬起爪子握手...好狗狗的技能！")


@function_tool
def roll_over() -> str:
    """Dog rolls over"""
    state_manager.modify_state(happiness=10, boredom=-8, fatigue=3)
    return _log_behavior("翻滚露出肚皮...展示肚子！棒极了！")


@function_tool
def play_dead() -> str:
    """Dog plays dead"""
    state_manager.modify_state(happiness=7, boredom=-6)
    return _log_behavior("夸张地倒下...装死！(舌头伸出)")


@function_tool
def fetch_object() -> str:
    """Dog fetches an object"""
    state_manager.modify_state(happiness=12, boredom=-15, fatigue=10)
    return _log_behavior("跑去捡东西...把它叼回来！完美的取物！")


# ==================== Special/Unusual Behaviors ====================

@function_tool
def scratch_itch() -> str:
    """Dog scratches an itch"""
    state_manager.modify_state(happiness=3)
    return _log_behavior("用后腿抓痒...啊，舒服多了！")


@function_tool
def sneeze() -> str:
    """Dog sneezes"""
    return _log_behavior("阿嚏！(打喷嚏)")


@function_tool
def shake_body() -> str:
    """Dog shakes whole body"""
    state_manager.modify_state(happiness=3)
    return _log_behavior("用力抖动全身...毛发四处飞扬！")


@function_tool
def snore() -> str:
    """Dog snores while sleeping"""
    return _log_behavior("呼...呼...(轻轻打呼)")


@function_tool
def dream_twitch() -> str:
    """Dog twitches while dreaming"""
    return _log_behavior("腿在抽动...爪子在动...(梦见在奔跑！)")


# ==================== Utility Function ====================

def get_all_behavior_tools():
    """Get all behavior tools for agent"""
    return [
        # Physiological
        stretch, yawn, drink_water, eat_food, lick_fur, sleep,
        # Social
        wag_tail, nuzzle_owner, lick_hand, follow_owner, look_up_at_owner,
        # Exploration
        sniff_ground, walk_in_circles, paw_at_object, look_out_window, chase_light,
        # Emotional
        bark, growl, pin_ears_back, tuck_tail, jump_excitedly,
        # Training
        sit, lie_down, shake_paw, roll_over, play_dead, fetch_object,
        # Special
        scratch_itch, sneeze, shake_body, snore, dream_twitch
    ]

