import random
from typing import Dict, List, Any, Optional


def generate_name(gender=None):
    """生成随机中文名字"""
    if gender is None:
        gender = random.choice(["男性", "女性"])

    surnames = ["张", "王", "李", "赵", "陈", "刘", "杨", "黄", "周", "吴", "徐", "孙", "马", "朱", "胡", "林", "郭",
                "何", "高", "罗"]

    male_names = ["伟", "强", "磊", "勇", "军", "杰", "涛", "斌", "超", "明", "刚", "平", "辉", "健", "俊", "雷", "鹏",
                  "浩", "波", "鑫", "江"]
    female_names = ["芳", "娟", "敏", "静", "秀", "丽", "艳", "娜", "萍", "玲", "琳", "燕", "红", "梅", "美", "英",
                    "颖", "华", "雪", "婷", "佳"]

    surname = random.choice(surnames)
    if gender == "男性":
        given_name = random.choice(male_names)
        if random.random() < 0.3:  # 30%概率双字名
            given_name += random.choice(male_names)
    else:
        given_name = random.choice(female_names)
        if random.random() < 0.3:  # 30%概率双字名
            given_name += random.choice(female_names)

    return surname + given_name


def get_available_activities(character):
    """获取角色可用的活动列表"""
    # 基础活动
    activities = {
        "基础活动": ["休息", "锻炼", "查看状态"],
        "工作与学习": ["学习"],
        "社交与关系": ["社交"],
        "财富与投资": []
    }

    # 根据状态添加可用活动
    if character.job != "无业":
        activities["工作与学习"].append("工作")

    activities["工作与学习"].append("求职")

    # 婚恋相关
    if character.relationship_status == "单身":
        activities["社交与关系"].append("寻找伴侣")
    elif character.relationship_status == "恋爱中":
        activities["社交与关系"].extend(["约会", "求婚"])
    elif character.relationship_status == "已婚" and character.spouse:
        activities["社交与关系"].extend(["陪伴伴侣", "生育计划"])

    # 心理健康
    activities["社交与关系"].append("心理健康")

    # 财富管理
    if character.assets >= 1000:
        activities["财富与投资"].append("投资")

    if character.assets >= 50000 and not character.has_business:
        activities["财富与投资"].append("创业")

    if character.has_business:
        activities["财富与投资"].append("管理企业")

    if character.assets >= 1000:
        activities["财富与投资"].append("慈善捐款")

    # 特殊活动
    special_activities = []

    if character.assets >= 20000:
        special_activities.append("整容")

    if character.age >= 60 and character.job != "退休" and character.job != "无业":
        special_activities.append("退休")

    if special_activities:
        activities["特殊活动"] = special_activities

    return activities


def format_money(amount):
    """将金额格式化为人民币形式"""
    if amount >= 100000000:  # 亿
        return f"{amount / 100000000:.2f}亿"
    elif amount >= 10000:  # 万
        return f"{amount / 10000:.2f}万"
    else:
        return f"{amount:.0f}"


def serialize_game_data(game_state):
    """将游戏状态序列化为可JSON格式化的数据"""
    data = {
        "current_day": game_state.current_day,
        "family_fortune": game_state.family_fortune,
        "family_prestige": game_state.family_prestige,
        "current_season": game_state.current_season,
        "economy_status": game_state.economy_status,
        "family_traits": game_state.family_traits,
        "events": [
                      {"date": event["date"], "event": event["event"]}
                      for event in game_state.events_history
                      if "hidden" not in event or not event["hidden"]
                  ][-20:]  # 只返回最近20条非隐藏事件
    }

    # 添加玩家信息
    if game_state.player:
        data["player"] = serialize_character(game_state.player)

    # 添加家族成员
    data["family_members"] = []
    for member in game_state.family_members:
        data["family_members"].append(serialize_character(member))

    return data


def serialize_character(character):
    """将角色对象序列化为可JSON格式化的数据"""
    data = {
        "name": character.name,
        "gender": character.gender,
        "age": character.age,
        "alive": character.alive,
        "job": character.job,
        "salary": character.salary,
        "assets": character.assets,
        "education_level": character.education_level,
        "relationship_status": character.relationship_status,
        "mental_state": character.mental_state,

        # 基础属性
        "energy": character.energy,
        "health": character.health,
        "appearance": character.appearance,
        "charm": character.charm,
        "intelligence": character.intelligence,
        "emotional_intelligence": character.emotional_intelligence,
        "financial_intelligence": character.financial_intelligence,
        "luck": character.luck,

        # 其他重要属性
        "happiness": character.happiness,
        "stress_level": character.stress_level,
        "network": character.network
    }

    # 添加企业信息(如果有)
    if character.has_business:
        data["business"] = {
            "name": character.business_name,
            "type": character.business_type,
            "scale": character.business_scale,
            "profit": character.business_profit,
            "value": character.business_value,
            "employees": character.business_employees,
            "reputation": character.business_reputation
        }

    # 添加投资信息(如果有)
    if hasattr(character, "investments") and sum(character.investments.values()) > 0:
        data["investments"] = character.investments

    return data