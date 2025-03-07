import random
import json
from typing import Dict, List, Any, Optional
from openai import OpenAI

# Moonshot AI 接口设置 (与原代码保持一致)
client = OpenAI(
    base_url="https://api.moonshot.cn/v1",
    api_key="sk-5cQrmHuwTrt7VsVEqZO9k4dB47kKiv6SAy90luWXbsJIw19N",
)

# 用于缓存AI响应以减少API调用
AI_CACHE = {}


def add_event(game_state, event_text: str, hidden: bool = False):
    """
    添加事件到游戏状态的事件历史记录

    Args:
        game_state: 游戏状态对象
        event_text: 事件文本描述
        hidden: 是否隐藏事件（比如未被发现的出轨事件）
    """
    date = f"第{game_state.current_day}天"

    event = {
        "date": date,
        "event": event_text
    }

    if hidden:
        event["hidden"] = True

    game_state.events_history.append(event)
    print(f"[{date}] {event_text}")  # 调试输出

    return event


def ai_interaction(prompt: str, context: List[Dict] = None) -> str:
    """与AI互动获取游戏内容 - 直接从原代码复制"""
    # 检查缓存中是否有类似的请求
    cache_key = f"{prompt}_{str(context)}"
    if cache_key in AI_CACHE:
        return AI_CACHE[cache_key]

    if context is None:
        context = []

    # 构建消息
    messages = [
        {
            "role": "system",
            "content": "你是一个家族兴衰模拟游戏中的AI助手，负责生成有趣和合理的游戏内容。请根据玩家的状态和请求，生成适合的事件、对话和故事情节。回复要简洁、生动，符合游戏设定。"
        }
    ]

    # 添加上下文
    for ctx in context:
        messages.append(ctx)

    # 添加用户请求
    messages.append({
        "role": "user",
        "content": prompt
    })

    try:
        # 调用API
        completion = client.chat.completions.create(
            model="moonshot-v1-128k",
            messages=messages,
        )
        response = completion.choices[0].message.content

        # 缓存响应
        AI_CACHE[cache_key] = response

        # 限制缓存大小
        if len(AI_CACHE) > 500:  # 最多保存500个缓存
            # 移除最旧的缓存项
            oldest_key = list(AI_CACHE.keys())[0]
            AI_CACHE.pop(oldest_key)

        return response
    except Exception as e:
        print(f"AI互动出错: {e}")
        return "AI系统暂时无法响应，请稍后再试。"


def generate_random_event(game_state, character):
    """
    为指定角色生成一个随机事件 - 使用与原代码相同的AI调用逻辑

    Args:
        game_state: 游戏状态对象
        character: 角色对象

    Returns:
        str: 事件描述文本
    """
    # 定义事件类型
    event_types = [
        "日常", "职场", "健康", "社交", "经济", "家庭",
        "心理", "人际", "学习", "特殊"
    ]

    # 根据角色状态选择更可能的事件类型
    weights = [30, 20, 10, 10, 10, 5, 5, 5, 3, 2]  # 默认权重

    # 调整权重
    if character.mental_state != "正常":
        weights[6] += 15  # 增加心理事件
    if character.health < 60:
        weights[2] += 15  # 增加健康事件
    if character.job != "无业":
        weights[1] += 10  # 增加职场事件
    if character.relationship_status in ["恋爱中", "已婚"]:
        weights[5] += 10  # 增加家庭事件
    if character.assets > 100000:
        weights[4] += 10  # 增加经济事件

    # 基于人脉网络调整
    for network_type, level in character.network.items():
        if level > 50:
            if network_type == "商业":
                weights[4] += 5  # 增加经济事件
            elif network_type == "学术":
                weights[8] += 5  # 增加学习事件
            elif network_type in ["娱乐", "政界"]:
                weights[7] += 5  # 增加人际事件

    # 归一化权重
    total = sum(weights)
    weights = [w / total for w in weights]

    # 选择事件类型
    event_type = random.choices(event_types, weights=weights)[0]

    # 构建上下文 - 与原代码保持一致
    context = [
        {
            "role": "system",
            "content": json.dumps({
                "角色状态": {
                    "姓名": character.name,
                    "性别": character.gender,
                    "年龄": character.age,
                    "健康": character.health,
                    "工作": character.job,
                    "资产": character.assets,
                    "关系状态": character.relationship_status,
                    "心理状态": character.mental_state,
                    "快乐指数": character.happiness
                },
                "家族状态": {
                    "家族财富": game_state.family_fortune,
                    "家族声望": game_state.family_prestige
                },
                "事件类型": event_type
            }, ensure_ascii=False)
        }
    ]

    prompt = f"请为这个角色生成一个{event_type}类型的随机事件，事件应该简短（50字以内），可能对角色属性产生轻微影响。事件应该具体、生动，并与角色当前状态相关。"

    event_description = ai_interaction(prompt, context)

    # 根据事件类型和描述调整属性
    apply_event_effects(character, event_type, event_description)

    return event_description


def apply_event_effects(character, event_type, event_description):
    """
    根据事件描述和类型应用相应的属性变化 - 直接从原代码复制
    """
    # 分析事件描述中的关键词
    keywords = {
        "正面": ["成功", "获得", "好运", "幸运", "提升", "改善", "奖励", "开心", "高兴", "满意", "赢得"],
        "负面": ["失败", "损失", "倒霉", "不幸", "降低", "恶化", "惩罚", "难过", "悲伤", "不满", "输掉"],
        "健康": ["健康", "生病", "受伤", "病毒", "疾病", "医院", "药物", "治疗", "康复", "锻炼"],
        "金钱": ["钱", "财富", "收入", "支出", "花费", "购买", "售卖", "资产", "投资", "赌博", "彩票"],
        "社交": ["朋友", "同事", "聚会", "聚餐", "社交", "交流", "认识", "交往", "人际"],
        "工作": ["工作", "职场", "升职", "加薪", "考核", "项目", "老板", "下属", "绩效"],
        "感情": ["爱情", "约会", "暧昧", "表白", "恋爱", "婚姻", "离婚", "争吵", "和好"]
    }

    # 判断事件情感倾向
    sentiment = "中性"
    for word in keywords["正面"]:
        if word in event_description:
            sentiment = "正面"
            break
    for word in keywords["负面"]:
        if word in event_description:
            sentiment = "负面"
            break

    # 基于事件类型和情感倾向应用效果
    intensity = random.randint(1, 5)  # 效果强度

    effects = {
        "日常": {
            "正面": {"happiness": 1 * intensity},
            "负面": {"happiness": -1 * intensity},
            "中性": {}
        },
        "职场": {
            "正面": {"career_prestige": 1 * intensity, "assets": 100 * intensity},
            "负面": {"career_prestige": -1 * intensity, "stress_level": 2 * intensity},
            "中性": {"career_prestige": 0.5 * intensity}
        },
        "健康": {
            "正面": {"health": 1 * intensity},
            "负面": {"health": -2 * intensity},
            "中性": {"health": 0.5 * intensity}
        },
        "社交": {
            "正面": {"personal_connections": 1 * intensity, "happiness": 2 * intensity},
            "负面": {"personal_connections": -1 * intensity, "happiness": -1 * intensity},
            "中性": {"personal_connections": 0.5 * intensity}
        },
        "经济": {
            "正面": {"assets": 500 * intensity, "financial_intelligence": 0.5 * intensity},
            "负面": {"assets": -300 * intensity, "stress_level": 2 * intensity},
            "中性": {"financial_intelligence": 0.3 * intensity}
        },
        "家庭": {
            "正面": {"happiness": 3 * intensity},
            "负面": {"happiness": -2 * intensity, "stress_level": 3 * intensity},
            "中性": {"happiness": 1 * intensity}
        },
        "心理": {
            "正面": {"happiness": 2 * intensity, "stress_level": -3 * intensity},
            "负面": {"happiness": -2 * intensity, "stress_level": 4 * intensity, "depression_risk": 2 * intensity},
            "中性": {"self_esteem": 1 * intensity}
        },
        "人际": {
            "正面": {"charm": 0.5 * intensity, "personal_connections": 2 * intensity},
            "负面": {"charm": -0.5 * intensity, "personal_connections": -1 * intensity},
            "中性": {"emotional_intelligence": 0.3 * intensity}
        },
        "学习": {
            "正面": {"intelligence": 0.5 * intensity, "emotional_intelligence": 0.3 * intensity},
            "负面": {"stress_level": 2 * intensity},
            "中性": {"intelligence": 0.2 * intensity}
        },
        "特殊": {
            "正面": {"luck": 2 * intensity, "assets": 1000 * intensity},
            "负面": {"luck": -2 * intensity, "assets": -500 * intensity},
            "中性": {"luck": 1 * intensity}
        }
    }

    # 应用效果
    if event_type in effects and sentiment in effects[event_type]:
        for attr, change in effects[event_type][sentiment].items():
            if hasattr(character, attr):
                # 特殊处理某些属性
                if attr in ["health", "happiness", "charm", "intelligence",
                            "emotional_intelligence", "financial_intelligence"]:
                    # 这些属性上限为100
                    current_value = getattr(character, attr)
                    setattr(character, attr, max(1, min(100, current_value + change)))
                elif attr == "stress_level":
                    # 压力下限为0
                    current_value = getattr(character, attr)
                    setattr(character, attr, max(0, current_value + change))
                else:
                    # 其他属性直接加减
                    current_value = getattr(character, attr)
                    setattr(character, attr, current_value + change)

    # 根据事件描述中的关键词额外应用效果
    for category, words in keywords.items():
        if category not in ["正面", "负面"]:  # 跳过情感判断类别
            for word in words:
                if word in event_description:
                    if category == "健康":
                        if sentiment == "正面":
                            character.health += random.randint(1, 3)
                        elif sentiment == "负面":
                            character.health -= random.randint(1, 5)
                    elif category == "金钱":
                        if sentiment == "正面":
                            bonus = random.randint(200, 1000) * (character.financial_intelligence / 50)
                            character.assets += bonus
                        elif sentiment == "负面":
                            loss = random.randint(100, 500) * (100 / character.financial_intelligence)
                            character.assets = max(0, character.assets - loss)
                    elif category == "社交":
                        if sentiment == "正面":
                            character.personal_connections += random.randint(1, 3)
                            # 随机提升一种人脉网络
                            if hasattr(character, "network"):
                                network_type = random.choice(list(character.network.keys()))
                                character.network[network_type] += random.randint(1, 3)
                    elif category == "工作":
                        if sentiment == "正面":
                            character.career_prestige += random.randint(1, 3)
                            if random.random() < 0.2:  # 20%概率加薪
                                raise_amount = character.salary * random.uniform(0.03, 0.1)
                                character.salary += raise_amount
                    elif category == "感情":
                        if sentiment == "正面":
                            character.happiness += random.randint(2, 5)
                            if hasattr(character, "relationship_satisfaction") and character.relationship_status in [
                                "恋爱中", "已婚"] and hasattr(character, "spouse") and character.spouse:
                                character.relationship_satisfaction += random.randint(3, 8)
                        elif sentiment == "负面":
                            character.happiness -= random.randint(2, 5)
                            if hasattr(character, "relationship_satisfaction") and character.relationship_status in [
                                "恋爱中", "已婚"] and hasattr(character, "spouse") and character.spouse:
                                character.relationship_satisfaction -= random.randint(3, 8)
                    break  # 只应用第一个匹配的关键词效果