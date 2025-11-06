"""
Dog state management with SQLite persistence.
Manages internal states: hunger, thirst, fatigue, boredom, happiness
"""

import sqlite3
import json
import time
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class DogState:
    """Dog's internal state"""
    hunger: float = 20.0      # 0-100, increases over time
    thirst: float = 20.0      # 0-100, increases over time
    fatigue: float = 20.0     # 0-100, increases over time
    boredom: float = 30.0     # 0-100, increases over time
    happiness: float = 70.0   # 0-100, affected by interactions
    last_update_time: float = None
    
    def __post_init__(self):
        if self.last_update_time is None:
            self.last_update_time = time.time()
    
    def to_dict(self):
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create from dictionary"""
        return cls(**data)
    
    def clamp_values(self):
        """Ensure all values are within 0-100 range"""
        self.hunger = max(0, min(100, self.hunger))
        self.thirst = max(0, min(100, self.thirst))
        self.fatigue = max(0, min(100, self.fatigue))
        self.boredom = max(0, min(100, self.boredom))
        self.happiness = max(0, min(100, self.happiness))
    
    def get_status_text(self) -> str:
        """Get readable status text"""
        return f"""
🐕 狗狗状态:
  饥饿值: {self.hunger:.1f}/100 {'⚠️  (饿了!)' if self.hunger > 70 else ''}
  口渴值: {self.thirst:.1f}/100 {'⚠️  (渴了!)' if self.thirst > 70 else ''}
  疲劳值: {self.fatigue:.1f}/100 {'⚠️  (累了!)' if self.fatigue > 70 else ''}
  无聊值: {self.boredom:.1f}/100 {'⚠️  (无聊!)' if self.boredom > 70 else ''}
  快乐值: {self.happiness:.1f}/100 {'😊' if self.happiness > 70 else '😐' if self.happiness > 30 else '😞'}
"""


class DogStateManager:
    """Manage dog state with SQLite persistence"""
    
    def __init__(self, db_path: str = "dog_state.db"):
        self.db_path = db_path
        # Allow connection to be used across threads
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()
        self.current_state = self._load_or_create_state()
    
    def _init_db(self):
        """Initialize database schema"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dog_state (
                id INTEGER PRIMARY KEY,
                state_data TEXT NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        self.conn.commit()
    
    def _load_or_create_state(self) -> DogState:
        """Load existing state or create new one"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT state_data FROM dog_state WHERE id = 1")
        row = cursor.fetchone()
        
        if row:
            state_dict = json.loads(row[0])
            return DogState.from_dict(state_dict)
        else:
            # Create initial state
            return DogState()
    
    def update_state_by_time(self):
        """Update state based on elapsed time"""
        current_time = time.time()
        elapsed_seconds = current_time - self.current_state.last_update_time
        elapsed_minutes = elapsed_seconds / 60.0
        
        # Update values based on time
        self.current_state.hunger += elapsed_minutes * 2.0    # +2 per minute
        self.current_state.thirst += elapsed_minutes * 1.5    # +1.5 per minute
        self.current_state.fatigue += elapsed_minutes * 1.0   # +1 per minute
        self.current_state.boredom += elapsed_minutes * 1.5   # +1.5 per minute
        
        # Unhappiness increases if needs are not met
        if self.current_state.hunger > 70 or self.current_state.thirst > 70:
            self.current_state.happiness -= elapsed_minutes * 0.5
        
        self.current_state.last_update_time = current_time
        self.current_state.clamp_values()
    
    def save_state(self):
        """Save current state to database"""
        cursor = self.conn.cursor()
        state_json = json.dumps(self.current_state.to_dict())
        
        cursor.execute("""
            INSERT OR REPLACE INTO dog_state (id, state_data, updated_at)
            VALUES (1, ?, ?)
        """, (state_json, time.time()))
        
        self.conn.commit()
    
    def modify_state(self, **kwargs):
        """Modify state values (delta changes)"""
        for key, value in kwargs.items():
            if hasattr(self.current_state, key):
                current = getattr(self.current_state, key)
                setattr(self.current_state, key, current + value)
        
        self.current_state.clamp_values()
        self.save_state()
    
    def get_state_description(self) -> str:
        """Get state description for agent context"""
        self.update_state_by_time()
        self.save_state()
        
        state = self.current_state
        
        # Determine needs
        needs = []
        if state.hunger > 70:
            needs.append("非常饿")
        elif state.hunger > 40:
            needs.append("有点饿")
        
        if state.thirst > 70:
            needs.append("非常渴")
        elif state.thirst > 40:
            needs.append("有点渴")
        
        if state.fatigue > 80:
            needs.append("筋疲力尽")
        elif state.fatigue > 50:
            needs.append("累了")
        
        if state.boredom > 70:
            needs.append("非常无聊")
        elif state.boredom > 40:
            needs.append("有点无聊")
        
        needs_text = "、".join(needs) if needs else "满足"
        
        return f"""当前内部状态:
- 饥饿值: {state.hunger:.1f}/100
- 口渴值: {state.thirst:.1f}/100
- 疲劳值: {state.fatigue:.1f}/100
- 无聊值: {state.boredom:.1f}/100
- 快乐值: {state.happiness:.1f}/100
- 整体感觉: {needs_text}"""
    
    def close(self):
        """Close database connection"""
        self.conn.close()

