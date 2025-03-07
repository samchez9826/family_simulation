# 导入所有游戏模块
from family_simulation.game.game_state import GameState
from family_simulation.game.character import Character
from family_simulation.game.events import add_event, generate_random_event, ai_interaction
from family_simulation.game.activities import process_activity
from family_simulation.game.utils import generate_name, get_available_activities, format_money, serialize_game_data, serialize_character