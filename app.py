from flask import Flask, render_template, request, jsonify, session
import os
import json
from flask_session import Session
from game.game_state import GameState
from game.character import Character
from game.activities import process_activity
from game.events import add_event
from game.utils import generate_name

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "saves"
Session(app)

# 确保存档目录存在
os.makedirs("saves", exist_ok=True)


@app.route('/')
def index():
    """主页/游戏界面"""
    return render_template('index.html')


@app.route('/api/game_state', methods=['GET'])
def get_game_state():
    """获取当前游戏状态"""
    if 'game_state' not in session:
        return jsonify({"error": "No active game"}), 404

    game_state = session['game_state']
    return jsonify(game_state.to_dict())


@app.route('/api/new_game', methods=['POST'])
def new_game():
    """创建新游戏"""
    game_state = GameState()
    session['game_state'] = game_state
    return jsonify({"status": "success", "message": "New game created"})


@app.route('/api/create_character', methods=['POST'])
def create_character():
    """创建角色"""
    data = request.json
    name = data.get('name', '')
    gender = data.get('gender', '男性')
    age = int(data.get('age', 25))
    education = data.get('education', '高中')

    # 如果名字为空，生成随机名字
    if not name:
        name = generate_name(gender)

    # 创建角色
    character = Character(name, gender, age)
    character.education_level = education

    # 根据教育水平调整初始属性
    edu_bonus = {
        "高中": 0,
        "大专": 5,
        "本科": 10,
        "硕士": 15,
        "博士": 20
    }

    bonus = edu_bonus.get(education, 0)
    character.intelligence += bonus
    character.financial_intelligence += bonus * 0.5

    # 设置为玩家角色
    if 'game_state' not in session:
        session['game_state'] = GameState()

    game_state = session['game_state']
    game_state.player = character
    game_state.family_members = []  # 清空家族成员

    add_event(game_state, f"创建了新角色: {character.name}")

    # 为角色寻找初始工作
    # Note: This is a placeholder, we'll need to implement proper job hunting
    character.job = "初级白领"
    character.salary = 5000

    session['game_state'] = game_state

    return jsonify({
        "status": "success",
        "character": character.to_dict(),
        "game_state": game_state.to_dict()
    })


@app.route('/api/activity', methods=['POST'])
def do_activity():
    """执行活动"""
    if 'game_state' not in session:
        return jsonify({"error": "No active game"}), 404

    data = request.json
    activity_type = data.get('activity_type')
    activity_params = data.get('params', {})

    game_state = session['game_state']

    result = process_activity(game_state, activity_type, activity_params)

    session['game_state'] = game_state

    return jsonify({
        "status": "success",
        "result": result,
        "game_state": game_state.to_dict()
    })


@app.route('/api/next_day', methods=['POST'])
def next_day():
    """进入下一天"""
    if 'game_state' not in session:
        return jsonify({"error": "No active game"}), 404

    game_state = session['game_state']

    # 恢复玩家精力
    game_state.player.energy = 100

    # 更新游戏状态
    game_state.update_daily()

    # 自动存档
    game_state.save_game("autosave")

    session['game_state'] = game_state

    return jsonify({
        "status": "success",
        "message": "Advanced to next day",
        "game_state": game_state.to_dict()
    })


@app.route('/api/save_game', methods=['POST'])
def save_game():
    """保存游戏"""
    if 'game_state' not in session:
        return jsonify({"error": "No active game"}), 404

    data = request.json
    filename = data.get('filename', 'autosave')

    game_state = session['game_state']
    success, message = game_state.save_game(filename)

    return jsonify({
        "status": "success" if success else "error",
        "message": message
    })


@app.route('/api/load_game', methods=['POST'])
def load_game():
    """加载游戏"""
    data = request.json
    filename = data.get('filename', 'autosave')

    success, result = GameState.load_game(filename)

    if success:
        session['game_state'] = result
        return jsonify({
            "status": "success",
            "message": f"Game loaded: {filename}",
            "game_state": result.to_dict()
        })
    else:
        return jsonify({
            "status": "error",
            "message": f"Failed to load game: {result}"
        }), 400


@app.route('/api/get_saves', methods=['GET'])
def get_saves():
    """获取存档列表"""
    if 'game_state' not in session:
        game_state = GameState()
    else:
        game_state = session['game_state']

    save_files = game_state.get_save_files()

    return jsonify({
        "status": "success",
        "saves": save_files
    })


if __name__ == '__main__':
    app.run(debug=True)