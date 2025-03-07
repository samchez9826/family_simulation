import json
import random
from typing import Dict, List, Any, Optional

from family_simulation.game.events import add_event, ai_interaction
from family_simulation.game.utils import generate_name
from family_simulation.game.character import Character

def process_activity(game_state, activity_type, params=None):
    """
    处理各种活动

    Args:
        game_state: 游戏状态对象
        activity_type: 活动类型
        params: 活动参数

    Returns:
        Dict: 活动结果
    """
    if params is None:
        params = {}

    character = game_state.player

    # 检查活动类型并调用相应的处理函数
    if activity_type == "rest":
        return activity_rest(game_state, character)
    elif activity_type == "work":
        return activity_work(game_state, character)
    elif activity_type == "exercise":
        return activity_exercise(game_state, character)
    elif activity_type == "study":
        return activity_study(game_state, character, params)
    elif activity_type == "job_hunting":
        return activity_job_hunting(game_state, character)
    elif activity_type == "socialize":
        return activity_socialize(game_state, character)
    elif activity_type == "investment":
        return activity_investment(game_state, character, params)
    elif activity_type == "start_business":
        return activity_start_business(game_state, character, params)
    elif activity_type == "manage_business":
        return activity_manage_business(game_state, character, params)
    elif activity_type == "date":
        return activity_date(game_state, character)
    elif activity_type == "marriage":
        return activity_marriage(game_state, character)
    elif activity_type == "have_child":
        return activity_have_child(game_state, character)
    elif activity_type == "plastic_surgery":
        return activity_plastic_surgery(game_state, character, params)
    elif activity_type == "mental_health":
        return activity_mental_health(game_state, character, params)
    elif activity_type == "charity":
        return activity_charity(game_state, character, params)
    else:
        return {"success": False, "message": f"未知活动类型: {activity_type}"}


def activity_rest(game_state, character):
    """休息活动"""
    energy_recovery = random.randint(20, 40)
    character.energy = min(100, character.energy + energy_recovery)
    add_event(game_state, f"{character.name}进行了休息，恢复了{energy_recovery}点精力。")

    return {
        "success": True,
        "message": f"休息恢复了{energy_recovery}点精力",
        "energy_gain": energy_recovery
    }


def activity_work(game_state, character):
    """工作活动"""
    if character.job == "无业":
        add_event(game_state, f"{character.name}没有工作，无法工作。")
        return {"success": False, "message": "没有工作"}

    energy_cost = random.randint(10, 20)
    if character.energy < energy_cost:
        add_event(game_state, f"{character.name}太累了，无法工作。")
        return {"success": False, "message": "精力不足", "required_energy": energy_cost}

    character.energy -= energy_cost
    work_income = character.salary / 30  # 日薪
    character.assets += work_income

    # 随机工作表现
    performance = random.random()
    if performance > 0.9:  # 出色表现
        bonus = work_income * 0.5
        character.assets += bonus
        character.career_prestige += 1
        add_event(game_state, f"{character.name}工作表现出色，获得了{bonus:.2f}额外奖金！")
        return {
            "success": True,
            "message": "工作表现出色",
            "income": work_income,
            "bonus": bonus,
            "prestige_gain": 1
        }
    elif performance < 0.1:  # 糟糕表现
        character.career_prestige -= 1
        character.stress_level += random.randint(5, 15)
        add_event(game_state, f"{character.name}工作表现不佳，压力增加。")
        return {
            "success": True,
            "message": "工作表现不佳",
            "income": work_income,
            "prestige_loss": 1,
            "stress_increase": character.stress_level
        }
    else:
        add_event(game_state, f"{character.name}完成了一天的工作，赚取了{work_income:.2f}。")
        return {
            "success": True,
            "message": "正常工作",
            "income": work_income
        }


def activity_exercise(game_state, character):
    """锻炼活动"""
    energy_cost = random.randint(15, 25)
    if character.energy < energy_cost:
        add_event(game_state, f"{character.name}太累了，无法锻炼。")
        return {"success": False, "message": "精力不足", "required_energy": energy_cost}

    character.energy -= energy_cost
    health_gain = random.randint(1, 3)
    character.health += health_gain

    # 调整体重
    if character.weight > character.ideal_weight:
        # 超重的人减重更明显
        weight_loss = random.uniform(0.1, 0.3)
        character.weight -= weight_loss
    elif character.weight < character.ideal_weight - 5:
        # 过轻的人增重
        weight_gain = random.uniform(0.05, 0.15)
        character.weight += weight_gain

    # 锻炼对心理健康的积极影响
    happiness_gain = random.randint(2, 5)
    character.happiness += happiness_gain

    stress_reduction = random.randint(3, 8)
    character.stress_level = max(0, character.stress_level - stress_reduction)

    # 如果有抑郁或焦虑，有助于恢复
    mental_health_improvement = 0
    if character.mental_state in ["抑郁", "焦虑"]:
        mental_health_improvement = random.randint(1, 3)
        character.depression_risk = max(0, character.depression_risk - mental_health_improvement)
        character.anxiety_risk = max(0, character.anxiety_risk - mental_health_improvement)

    add_event(game_state, f"{character.name}进行了锻炼，健康和心情都有所提升。体重现在是{character.weight:.1f}kg。")
    character.update_appearance_from_physique()

    return {
        "success": True,
        "message": "锻炼成功",
        "health_gain": health_gain,
        "happiness_gain": happiness_gain,
        "stress_reduction": stress_reduction,
        "mental_health_improvement": mental_health_improvement,
        "weight": character.weight,
        "weight_status": character.get_weight_status()
    }


def activity_study(game_state, character, params):
    """学习活动"""
    energy_cost = random.randint(15, 25)
    if character.energy < energy_cost:
        add_event(game_state, f"{character.name}太累了，无法学习。")
        return {"success": False, "message": "精力不足", "required_energy": energy_cost}

    character.energy -= energy_cost

    # 获取学习内容
    study_focus = params.get("focus", "专业知识")

    # 基础智力提升
    intelligence_gain = 0.1

    # 家族特质"智慧传承"影响
    if hasattr(game_state, 'family_traits') and game_state.family_traits.get("智慧传承", 0) > 0:
        intelligence_gain *= 1.5

    character.intelligence += intelligence_gain

    # 基础学习效率 (增加随机因素)
    base_efficiency = 1.0 + (random.random() * 0.5)  # 1.0-1.5的随机效率

    # 人脉影响学习效率
    if character.network["学术"] > 30:
        academic_bonus = character.network["学术"] / 100  # 最多50%额外提升
        base_efficiency += academic_bonus
        if academic_bonus > 0.2:  # 只在效果明显时提示
            add_event(game_state, f"{character.name}通过学术圈人脉获得了更高效的学习资源。")

    # 心理状态影响学习效率
    if character.mental_state == "抑郁":
        base_efficiency *= 0.6  # 抑郁状态学习效率降低
    elif character.mental_state == "焦虑":
        base_efficiency *= 0.8  # 焦虑状态学习效率轻微降低

    # 基础增长值
    base_gain = random.randint(1, 2) / 10 * base_efficiency

    # 学习结果
    result = {
        "success": True,
        "message": "学习成功",
        "focus": study_focus,
        "intelligence_gain": intelligence_gain,
        "efficiency": base_efficiency
    }

    if "财商" in study_focus:
        financial_gain = base_gain
        character.financial_intelligence += financial_gain
        add_event(game_state, f"{character.name}学习了财务知识，财商提升了{financial_gain:.2f}点。")
        result["financial_intelligence_gain"] = financial_gain

        # 财商学习特殊奖励
        if random.random() < 0.1:  # 10%概率获得投资见解
            investment_tip = random.choice([
                "发现了一个潜在的投资机会",
                "掌握了一种新的理财技巧",
                "了解到一个重要的市场趋势"
            ])
            add_event(game_state, f"{character.name}在学习中{investment_tip}，财商额外提升!")
            investment_bonus = base_gain * 0.5
            character.financial_intelligence += investment_bonus
            result["investment_bonus"] = investment_bonus

    elif "情商" in study_focus:
        emotional_gain = base_gain
        character.emotional_intelligence += emotional_gain
        add_event(game_state, f"{character.name}学习了情绪管理和人际交往，情商提升了{emotional_gain:.2f}点。")
        result["emotional_intelligence_gain"] = emotional_gain

        # 情商学习提升魅力
        if random.random() < 0.3:  # 30%概率提升魅力
            charm_gain = base_gain * 0.7
            character.charm += charm_gain
            add_event(game_state, f"{character.name}的社交技巧有所提升，魅力增加了{charm_gain:.2f}点。")
            result["charm_gain"] = charm_gain

    elif "领导" in study_focus:
        leadership_gain = base_gain
        if hasattr(character, "leadership"):
            character.leadership += leadership_gain
        add_event(game_state, f"{character.name}学习了团队管理和领导技能，领导能力提升了{leadership_gain:.2f}点。")
        result["leadership_gain"] = leadership_gain

        # 领导力学习可能提升职场声望
        if random.random() < 0.2 and character.job != "无业":  # 20%概率
            prestige_gain = random.randint(1, 3)
            character.career_prestige += prestige_gain
            add_event(game_state, f"{character.name}在工作中展示了领导才能，职场声望增加了{prestige_gain}点。")
            result["prestige_gain"] = prestige_gain

    elif "商业" in study_focus:
        business_gain = base_gain
        if hasattr(character, "business_vision"):
            character.business_vision += business_gain
        add_event(game_state, f"{character.name}学习了市场分析和商业策略，商业眼光提升了{business_gain:.2f}点。")
        result["business_vision_gain"] = business_gain

        # 商业眼光学习可能产生创业想法
        if random.random() < 0.1 and not character.has_business:  # 10%概率
            add_event(game_state, f"{character.name}在学习中产生了一个有潜力的创业点子。")
            # 为未来创业增加成功率加成
            if not hasattr(character, "business_idea_bonus"):
                character.business_idea_bonus = 0
            character.business_idea_bonus += 0.05  # 5%的创业成功率加成
            result["business_idea"] = True

    else:  # 专业知识
        knowledge_gain = base_gain
        character.intelligence += knowledge_gain
        add_event(game_state, f"{character.name}学习了专业知识，智商提升了{knowledge_gain:.2f}点。")
        result["knowledge_gain"] = knowledge_gain

    # 学习对心理健康的积极影响
    stress_reduction = random.randint(1, 3)
    character.stress_level = max(0, character.stress_level - stress_reduction)
    result["stress_reduction"] = stress_reduction

    # 每次学习都提升一点快乐度（成就感）
    character.happiness = min(100, character.happiness + 1)
    result["happiness_gain"] = 1

    return result


def activity_job_hunting(game_state, character):
    """求职活动"""
    energy_cost = random.randint(15, 25)
    if character.energy < energy_cost:
        add_event(game_state, f"{character.name}太累了，无法求职。")
        return {"success": False, "message": "精力不足", "required_energy": energy_cost}

    character.energy -= energy_cost

    # 求职成功率
    success_chance = (character.intelligence + character.charm) / 200

    # 根据学历调整
    education_bonus = {
        "初中": 0,
        "高中": 0.1,
        "大专": 0.2,
        "本科": 0.3,
        "硕士": 0.4,
        "博士": 0.5
    }
    success_chance += education_bonus.get(character.education_level, 0)

    # 整容可能影响求职
    if character.has_plastic_surgery:
        if character.surgery_complications:
            success_chance *= 0.9  # 整容并发症可能降低成功率
        else:
            if character.appearance > 80:
                success_chance *= 1.1  # 高颜值提高成功率

    # 心理状态影响
    if character.mental_state != "正常":
        success_chance *= 0.8

    # 人脉网络影响
    if character.network["商业"] > 30:
        business_network_bonus = character.network["商业"] / 100
        success_chance += business_network_bonus

    if character.network["政界"] > 20 and random.random() < 0.3:
        # 政界人脉可能直接提供工作机会
        success_chance += 0.2
        add_event(game_state, f"{character.name}通过政界人脉获得了一个不错的工作机会。")

    # 确保概率在合理范围内
    success_chance = max(0.1, min(0.9, success_chance))

    result = {
        "success": True,
        "message": "求职尝试",
        "chance": success_chance
    }

    if random.random() < success_chance:
        # 求职成功
        old_job = character.job
        old_salary = character.salary

        # 可能的工作和薪资
        potential_jobs = [
            {"title": "销售员", "salary": random.randint(4000, 6000), "min_education": "高中"},
            {"title": "行政助理", "salary": random.randint(4500, 7000), "min_education": "大专"},
            {"title": "客服专员", "salary": random.randint(4000, 6000), "min_education": "高中"},
            {"title": "程序员", "salary": random.randint(10000, 18000), "min_education": "本科"},
            {"title": "市场专员", "salary": random.randint(6000, 9000), "min_education": "大专"},
            {"title": "教师", "salary": random.randint(6000, 10000), "min_education": "本科"},
            {"title": "设计师", "salary": random.randint(7000, 12000), "min_education": "大专"},
            {"title": "会计", "salary": random.randint(6000, 10000), "min_education": "本科"}
        ]

        # 根据学历筛选工作
        education_ranks = ["初中", "高中", "大专", "本科", "硕士", "博士"]
        character_edu_rank = education_ranks.index(character.education_level)
        eligible_jobs = []

        for job in potential_jobs:
            job_min_edu_rank = education_ranks.index(job["min_education"])
            if character_edu_rank >= job_min_edu_rank:
                eligible_jobs.append(job)

        # 高学历的高级工作
        if character.education_level in ["本科", "硕士", "博士"]:
            advanced_jobs = [
                {"title": "高级工程师", "salary": random.randint(15000, 25000), "min_education": "本科"},
                {"title": "项目经理", "salary": random.randint(15000, 25000), "min_education": "本科"},
                {"title": "研究员", "salary": random.randint(12000, 20000), "min_education": "硕士"},
                {"title": "医生", "salary": random.randint(15000, 30000), "min_education": "硕士"},
                {"title": "律师", "salary": random.randint(15000, 30000), "min_education": "硕士"},
                {"title": "金融分析师", "salary": random.randint(15000, 25000), "min_education": "本科"},
                {"title": "大学教授", "salary": random.randint(15000, 25000), "min_education": "博士"},
                {"title": "高级管理人员", "salary": random.randint(25000, 40000), "min_education": "硕士"}
            ]
            eligible_jobs.extend(advanced_jobs)

        # 如果没有符合条件的工作，提供一些基础工作
        if not eligible_jobs:
            eligible_jobs = [
                {"title": "快递员", "salary": random.randint(3000, 5000), "min_education": "初中"},
                {"title": "服务员", "salary": random.randint(3000, 4500), "min_education": "初中"},
                {"title": "保安", "salary": random.randint(3500, 5000), "min_education": "初中"},
                {"title": "工厂工人", "salary": random.randint(4000, 6000), "min_education": "初中"}
            ]

        # 选择工作
        new_job = random.choice(eligible_jobs)

        # 应用职场声望和人脉网络加成到薪资
        reputation_bonus = character.career_prestige / 50  # 最多20%的加成
        network_bonus = character.network["商业"] / 100  # 最多50%的加成

        salary_multiplier = 1.0 + reputation_bonus + network_bonus
        new_job["salary"] = int(new_job["salary"] * salary_multiplier)

        # 更新角色状态
        character.job = new_job["title"]
        character.salary = new_job["salary"]
        character.career_prestige += random.randint(1, 5)

        if old_job == "无业":
            add_event(game_state, f"{character.name}找到了工作：{character.job}，月薪{character.salary}元。")
            result["message"] = "求职成功"
            result["new_job"] = character.job
            result["salary"] = character.salary
        else:
            salary_change = character.salary - old_salary
            if salary_change > 0:
                add_event(game_state,
                          f"{character.name}换了新工作：从{old_job}变为{character.job}，月薪增加了{salary_change}元，现在为{character.salary}元。")
                result["message"] = "换工作成功，薪资提升"
            else:
                add_event(game_state,
                          f"{character.name}换了新工作：从{old_job}变为{character.job}，月薪现在为{character.salary}元。")
                result["message"] = "换工作成功"

            result["old_job"] = old_job
            result["new_job"] = character.job
            result["old_salary"] = old_salary
            result["new_salary"] = character.salary

        # 家族声望可能提升
        if character.salary > 20000:
            prestige_gain = random.randint(1, 3)
            game_state.family_prestige += prestige_gain
            add_event(game_state, f"{character.name}获得高薪工作，家族声望提升。")
            result["prestige_gain"] = prestige_gain
    else:
        # 求职失败
        happiness_loss = random.randint(2, 8)
        stress_increase = random.randint(5, 15)
        character.happiness -= happiness_loss
        character.stress_level += stress_increase
        add_event(game_state, f"{character.name}求职失败，有些沮丧。")

        result["message"] = "求职失败"
        result["happiness_loss"] = happiness_loss
        result["stress_increase"] = stress_increase

    return result


def activity_socialize(game_state, character):
    """社交活动"""
    energy_cost = random.randint(10, 20)
    if character.energy < energy_cost:
        add_event(game_state, f"{character.name}太累了，无法社交。")
        return {"success": False, "message": "精力不足", "required_energy": energy_cost}

    character.energy -= energy_cost

    # 社交结果
    context = [
        {
            "role": "system",
            "content": json.dumps({
                "角色": {
                    "姓名": character.name,
                    "性别": character.gender,
                    "年龄": character.age,
                    "魅力": character.charm,
                    "外貌": character.appearance,
                    "情商": character.emotional_intelligence,
                    "关系状态": character.relationship_status
                }
            }, ensure_ascii=False)
        }
    ]

    prompt = "请描述这个角色的一次社交活动经历（50字以内），可能结识新朋友或潜在恋爱对象。"

    social_result = ai_interaction(prompt, context)
    add_event(game_state, social_result)

    # 调整属性
    happiness_gain = random.randint(2, 8)
    connections_gain = random.randint(1, 2)
    stress_reduction = random.randint(1, 5)

    character.happiness += happiness_gain
    character.personal_connections += connections_gain
    character.stress_level = max(0, character.stress_level - stress_reduction)

    result = {
        "success": True,
        "message": "社交成功",
        "event": social_result,
        "happiness_gain": happiness_gain,
        "connections_gain": connections_gain,
        "stress_reduction": stress_reduction
    }

    # 提升随机一种人脉网络
    if random.random() < 0.3:  # 30%概率提升人脉
        network_type = random.choice(list(character.network.keys()))
        network_gain = random.randint(1, 3)
        character.network[network_type] += network_gain
        if network_gain >= 2 and character.network[network_type] > 30:
            add_event(game_state, f"{character.name}在社交活动中拓展了{network_type}圈人脉。")
            result["network_type"] = network_type
            result["network_gain"] = network_gain

    # 可能遇到恋爱对象
    if (character.relationship_status == "单身" and
            random.random() < 0.1 * (character.charm + character.appearance) / 150):
        potential_partner = generate_potential_partner(character)
        add_event(game_state, f"{character.name}在社交活动中遇到了一个有好感的对象：{potential_partner['name']}。")
        result["met_partner"] = True
        result["partner"] = potential_partner

        context.append({
            "role": "system",
            "content": json.dumps({
                "潜在对象": {
                    "姓名": potential_partner['name'],
                    "性别": potential_partner['gender'],
                    "年龄": potential_partner['age'],
                    "职业": potential_partner['job']
                }
            }, ensure_ascii=False)
        })

        prompt = "这位角色在社交活动中遇到了潜在恋爱对象，请描述他们的第一次接触（100字以内）。"
        meeting_description = ai_interaction(prompt, context)
        add_event(game_state, meeting_description)
        result["meeting_description"] = meeting_description

    return result


def generate_potential_partner(character):
    """生成潜在伴侣"""
    if character.sexual_orientation == "异性恋":
        gender = "女性" if character.gender == "男性" else "男性"
    elif character.sexual_orientation == "同性恋":
        gender = character.gender
    else:  # 双性恋
        gender = random.choice(["男性", "女性"])

    age_min = max(18, character.age - 10)
    age_max = character.age + 5
    age = random.randint(age_min, age_max)

    jobs = ["教师", "医生", "工程师", "设计师", "销售", "会计", "程序员", "自由职业者", "学生", "艺术家",
            "律师", "记者", "厨师", "健身教练", "护士", "公务员", "银行职员", "保险业务", "房产经纪", "演员"]

    # 根据角色的社会地位和职业匹配伴侣
    if character.career_prestige > 50 or character.assets > 100000:
        high_status_jobs = ["医生", "律师", "工程师", "设计师", "公务员", "银行职员"]
        jobs = high_status_jobs + [job for job in jobs if job not in high_status_jobs]

    # 随机生成伴侣
    partner = {
        "name": generate_name(gender),
        "gender": gender,
        "age": age,
        "job": random.choice(jobs),
        "charm": random.randint(60, 95),
        "appearance": random.randint(60, 95),
        "intelligence": random.randint(60, 95),
        "family_background": random.choice(["普通", "富裕", "贫困", "显赫"])
    }

    # 如果玩家很富有，增加遇到金钱目的伴侣的概率
    if character.assets > 500000 and random.random() < 0.2:
        partner["hidden_trait"] = "拜金"
        partner["charm"] += 10  # 拜金者通常更会讨好人

    # 如果玩家外貌很高，增加遇到颜控伴侣的概率
    if character.appearance > 85 and random.random() < 0.3:
        partner["hidden_trait"] = "颜控"
        partner["affection"] = character.appearance * 1.2  # 好感度与玩家外貌挂钩

    return partner


def activity_investment(game_state, character, params):
    """投资活动"""
    if character.assets < 1000:
        add_event(game_state, f"{character.name}资金不足，无法进行投资。至少需要1000元。")
        return {"success": False, "message": "资金不足"}

    # 获取投资类型和金额
    investment_type = params.get("type", "股票")
    amount = params.get("amount", 1000)

    # 检查金额是否合法
    if amount < 1000:
        add_event(game_state, "最低投资额为1000元。")
        return {"success": False, "message": "投资金额过低"}

    if amount > character.assets:
        add_event(game_state, f"{character.name}资金不足，无法投资{amount}元。")
        return {"success": False, "message": "资金不足"}

    # 扣除投资金额
    character.assets -= amount

    # 更新投资组合
    if investment_type not in character.investments:
        character.investments[investment_type] = 0
    character.investments[investment_type] += amount

    # 根据投资类型设置风险收益参数
    risk_return_params = {
        "股票": {"base_return": 0.15, "risk": 0.25, "period": 30},
        "基金": {"base_return": 0.08, "risk": 0.15, "period": 60},
        "债券": {"base_return": 0.05, "risk": 0.05, "period": 90},
        "房产": {"base_return": 0.2, "risk": 0.1, "period": 180},
        "创业": {"base_return": 0.3, "risk": 0.4, "period": 90}
    }

    params = risk_return_params.get(investment_type, risk_return_params["基金"])

    # 投资结果受财商影响
    success_chance = 0.5 + (character.financial_intelligence - 50) / 100
    success_chance = max(0.1, min(0.9, success_chance))

    # 经济环境影响
    economy_multipliers = {
        "繁荣": 1.2,
        "正常": 1.0,
        "衰退": 0.7
    }
    economy_multiplier = economy_multipliers.get(game_state.economy_status, 1.0)

    # 人脉网络影响
    network_multiplier = 1.0
    if character.network["商业"] > 40:
        network_multiplier += character.network["商业"] / 200  # 最多+25%收益
        if network_multiplier > 1.1:
            add_event(game_state, f"{character.name}的商业人脉为投资提供了有价值的信息。")

    # 家族特质影响
    trait_multiplier = 1.0
    if hasattr(game_state, 'family_traits') and game_state.family_traits.get("富贵命格", 0) > 0:
        trait_multiplier = 1.1

    # 基于当前时期的市场热点
    # 模拟某些投资类型在特定时期表现更好
    current_hot_market = None
    if random.random() < 0.3:  # 30%概率有市场热点
        current_hot_market = random.choice(list(risk_return_params.keys()))
        if current_hot_market == investment_type:
            add_event(game_state, f"当前{investment_type}市场正处于上升期，投资机会良好。")
            success_chance += 0.1

    # 最终投资结果
    final_success_chance = success_chance * economy_multiplier * network_multiplier * trait_multiplier
    final_success_chance = max(0.1, min(0.9, final_success_chance))

    result = {
        "success": True,
        "message": f"投资{investment_type}",
        "amount": amount,
        "type": investment_type,
        "success_chance": final_success_chance,
    }

    if random.random() < final_success_chance:
        # 投资成功
        base_return_rate = params["base_return"]

        # 投资热点额外收益
        if current_hot_market == investment_type:
            base_return_rate *= 1.5

        return_rate = random.uniform(0.05,
                                     base_return_rate * 2) * economy_multiplier * network_multiplier * trait_multiplier
        profit = amount * return_rate
        character.assets += amount + profit
        character.financial_intelligence += 0.5

        # 记录投资回报
        if investment_type not in character.investment_returns:
            character.investment_returns[investment_type] = 0
        character.investment_returns[investment_type] += profit

        add_event(game_state,
                  f"{character.name}投资{investment_type}{amount}元获得了{profit:.2f}元的收益！总回报率{return_rate * 100:.1f}%")

        result["outcome"] = "success"
        result["profit"] = profit
        result["return_rate"] = return_rate
        result["financial_intelligence_gain"] = 0.5

        # 投资成功增加商业人脉
        if random.random() < 0.3:
            network_gain = random.randint(1, 3)
            character.network["商业"] += network_gain
            result["network_gain"] = network_gain
    else:
        # 投资失败
        loss_rate = random.uniform(0.1, params["risk"] * 1.5) / economy_multiplier
        loss = amount * loss_rate
        character.assets += amount - loss

        # 记录投资损失
        if investment_type not in character.investment_returns:
            character.investment_returns[investment_type] = 0
        character.investment_returns[investment_type] -= loss

        add_event(game_state,
                  f"{character.name}投资{investment_type}{amount}元损失了{loss:.2f}元。损失率{loss_rate * 100:.1f}%")

        result["outcome"] = "loss"
        result["loss"] = loss
        result["loss_rate"] = loss_rate

    # 成就检查
    if sum(character.investments.values()) > 1000000:
        game_state.update_achievement("投资大亨")
        result["achievement"] = "投资大亨"

    return result


def activity_start_business(game_state, character, params):
    """创业活动"""
    if character.has_business:
        add_event(game_state, f"{character.name}已经拥有企业「{character.business_name}」，无法再次创业。")
        return {"success": False, "message": "已有企业"}

    # 创业所需资金
    initial_investment = 50000
    if character.assets < initial_investment:
        add_event(game_state, f"{character.name}资金不足，创业需要至少{initial_investment}元。")
        return {"success": False, "message": "资金不足", "required": initial_investment}

    # 获取创业类型和企业名称
    business_type = params.get("type", "科技")
    business_name = params.get("name", f"{character.name}的{business_type}公司")

    character.assets -= initial_investment
    character.has_business = True
    character.business_name = business_name
    character.business_type = business_type

    # 初始企业数据
    character.business_scale = 10  # 初始规模
    character.business_employees = 3  # 初始员工
    character.business_reputation = 50  # 初始声誉
    character.business_value = initial_investment  # 初始价值

    # 创业成功率依赖于角色能力
    base_success_chance = (character.financial_intelligence + character.business_vision + character.leadership) / 300

    # 增加创业点子奖励
    idea_bonus = 0
    if hasattr(character, "business_idea_bonus"):
        idea_bonus = character.business_idea_bonus
        character.business_idea_bonus = 0  # 使用后重置

    # 增加教育水平影响
    education_bonus = {
        "初中": 0,
        "高中": 0.05,
        "大专": 0.1,
        "本科": 0.15,
        "硕士": 0.2,
        "博士": 0.25
    }
    edu_bonus = education_bonus.get(character.education_level, 0)

    # 人脉网络影响
    network_bonus = character.network["商业"] / 200  # 最多+25%

    # 家族特质影响
    trait_bonus = 0
    if hasattr(game_state, 'family_traits') and game_state.family_traits.get("商业头脑", 0) > 0:
        trait_bonus = 0.1

    # 成就奖励
    achievement_bonus = 0
    if hasattr(game_state, 'achievements') and game_state.achievements.get("企业家_completed", False):
        achievement_bonus = 0.15

    # 总成功率计算
    success_chance = base_success_chance + idea_bonus + edu_bonus + network_bonus + trait_bonus + achievement_bonus

    # 根据经济环境调整
    economy_multipliers = {
        "繁荣": 1.3,
        "正常": 1.0,
        "衰退": 0.7
    }
    economy_multiplier = economy_multipliers.get(game_state.economy_status, 1.0)

    # 最终成功率
    final_success_chance = success_chance * economy_multiplier
    final_success_chance = max(0.2, min(0.9, final_success_chance))  # 确保在合理范围内

    result = {
        "success": True,
        "message": "创业",
        "business_name": business_name,
        "business_type": business_type,
        "investment": initial_investment,
        "success_chance": final_success_chance
    }

    # 初始利润
    if random.random() < final_success_chance:
        # 成功起步
        character.business_profit = random.randint(1000, 3000)
        add_event(game_state,
                  f"{character.name}成功创立了「{business_name}」！企业初期运营良好，月利润约{character.business_profit}元。")

        result["outcome"] = "success"
        result["profit"] = character.business_profit

        # 企业类型特殊效果
        if business_type == "科技":
            add_event(game_state, f"作为科技企业，「{business_name}」具有较高的增长潜力和技术壁垒。")
            character.business_value *= 1.2  # 科技企业估值更高
        elif business_type == "餐饮":
            add_event(game_state, f"「{business_name}」的位置很好，很快获得了固定的客户群。")
            character.business_reputation += 10  # 餐饮企业更容易获得声誉
        elif business_type == "零售":
            add_event(game_state, f"「{business_name}」的经营模式灵活，现金流稳定。")
            character.business_profit *= 1.1  # 零售企业初期现金流更好
        elif business_type == "教育":
            add_event(game_state, f"「{business_name}」以高质量的教育服务赢得了口碑。")
            character.business_reputation += 15  # 教育企业声誉加成
            character.intelligence += 2  # 经营教育机构也提升自身智力
    else:
        # 起步困难
        character.business_profit = random.randint(-1000, 500)
        add_event(game_state, f"{character.name}创立了「{business_name}」，但初期面临一些挑战，需要耐心经营。")

        result["outcome"] = "challenge"
        result["profit"] = character.business_profit

        # 困难的具体描述
        challenge = random.choice([
            "市场竞争激烈，获客成本高",
            "团队协作存在问题",
            "产品/服务尚需完善",
            "现金流紧张",
            "政策法规限制"
        ])
        add_event(game_state, f"主要挑战是: {challenge}。")
        result["challenge"] = challenge

    # AI生成创业描述
    context = [
        {
            "role": "system",
            "content": json.dumps({
                "企业家": {
                    "姓名": character.name,
                    "性别": character.gender,
                    "年龄": character.age,
                    "领导力": character.leadership,
                    "财商": character.financial_intelligence
                },
                "企业": {
                    "名称": business_name,
                    "类型": business_type,
                    "初始资金": initial_investment,
                    "起步情况": "良好" if character.business_profit > 0 else "困难"
                }
            }, ensure_ascii=False)
        }
    ]

    prompt = "请描述这位角色的创业故事开端（100字以内）。"
    business_story = ai_interaction(prompt, context)
    add_event(game_state, business_story)
    result["business_story"] = business_story

    # 创业对人脉的影响
    network_gain = random.randint(5, 15)
    character.network["商业"] += network_gain
    result["network_gain"] = network_gain

    # 成就更新
    game_state.update_achievement("企业家")
    result["achievement"] = "企业家"

    return result


def activity_manage_business(game_state, character, params):
    """管理企业活动"""
    if not character.has_business:
        add_event(game_state, f"{character.name}没有企业可以管理。")
        return {"success": False, "message": "没有企业"}

    energy_cost = random.randint(15, 25)
    if character.energy < energy_cost:
        add_event(game_state, f"{character.name}太累了，无法管理企业。")
        return {"success": False, "message": "精力不足", "required_energy": energy_cost}

    character.energy -= energy_cost

    # 获取管理重点
    focus = params.get("focus", "成本控制")

    # 管理效果受角色能力影响
    management_skill = (character.leadership + character.business_vision + character.financial_intelligence) / 3

    # 基础成功率
    base_success_chance = management_skill / 100

    # 学历加成
    education_bonus = {
        "初中": 0,
        "高中": 0.05,
        "大专": 0.1,
        "本科": 0.15,
        "硕士": 0.2,
        "博士": 0.25
    }
    edu_bonus = education_bonus.get(character.education_level, 0)

    # 人脉网络影响
    network_bonus = character.network["商业"] / 200  # 最多+25%
    if focus == "融资" and character.network["商业"] > 60:
        network_bonus *= 1.5  # 融资特别依赖商业人脉

    # 经济环境影响
    economy_multipliers = {
        "繁荣": 1.2,
        "正常": 1.0,
        "衰退": 0.8
    }
    economy_multiplier = economy_multipliers.get(game_state.economy_status, 1.0)

    # 企业规模影响 (大企业更稳定)
    scale_factor = 1.0
    if character.business_scale > 50:
        scale_factor = 1.1
    elif character.business_scale > 80:
        scale_factor = 1.2

    # 最终成功率
    success_chance = (base_success_chance + edu_bonus + network_bonus) * economy_multiplier * scale_factor
    success_chance = max(0.2, min(0.9, success_chance))

    result = {
        "success": True,
        "message": "企业管理",
        "focus": focus,
        "business_name": character.business_name,
        "success_chance": success_chance
    }

    # 管理结果
    if random.random() < success_chance:
        outcome = "success"
        if focus == "市场推广":
            reputation_gain = random.randint(5, 15)
            old_reputation = character.business_reputation
            character.business_reputation = max(10, min(100, character.business_reputation + reputation_gain))
            add_event(game_state, f"企业声誉从{old_reputation}上升到{character.business_reputation}。")
            profit_adjustment = (character.business_reputation - old_reputation) * 100
            character.business_profit += profit_adjustment
            result["reputation_gain"] = reputation_gain
            result["profit_adjustment"] = profit_adjustment

        elif focus == "人才招聘":
            scale_gain = random.uniform(2, 5)
            old_scale = character.business_scale
            character.business_scale = max(5, min(100, character.business_scale + scale_gain))
            character.business_employees = int(character.business_scale / 2)
            character.business_value = character.business_scale * 10000 * (character.business_reputation / 50)
            add_event(game_state,
                      f"企业规模从{old_scale:.1f}上升到{character.business_scale:.1f}，员工人数达到{character.business_employees}人。")
            result["scale_gain"] = scale_gain

        elif focus == "产品研发":
            profit_gain = random.randint(500, 2000)
            old_profit = character.business_profit
            character.business_profit += profit_gain
            add_event(game_state, f"企业月利润增加了{profit_gain}元，达到{character.business_profit}元。")
            result["profit_gain"] = profit_gain

        elif focus == "成本控制":
            value_adjustment = character.business_value * random.randint(5, 15) / 100
            character.business_value += value_adjustment
            add_event(game_state, f"企业经营更加稳定，企业估值增加了{value_adjustment:.0f}元。")
            result["value_adjustment"] = value_adjustment

        elif focus == "战略调整":
            reputation_gain = random.randint(10, 30) / 3
            character.business_reputation = max(10, min(100, character.business_reputation + reputation_gain))
            profit_adjustment = random.randint(10, 30) * 50
            character.business_profit += profit_adjustment
            value_adjustment = random.randint(10, 30) * 1000
            character.business_value += value_adjustment
            add_event(game_state, f"企业战略调整成功，长期发展前景更加光明，企业估值提升。")
            result["reputation_gain"] = reputation_gain
            result["profit_adjustment"] = profit_adjustment
            result["value_adjustment"] = value_adjustment

        elif focus == "融资扩张":
            financing_amount = character.business_value * random.randint(20, 50) / 100
            dilution = random.randint(20, 50) / 200  # 股权稀释程度
            character.assets += financing_amount * 0.1  # 10%进入个人腰包
            character.business_scale += random.randint(20, 50) / 5  # 规模增长
            character.business_profit += financing_amount * 0.02  # 月利润增长
            character.business_value += financing_amount  # 估值增长
            add_event(game_state,
                      f"企业成功融资{financing_amount:.0f}元，规模快速扩张，但稀释了{dilution * 100:.1f}%的股权。")
            result["financing_amount"] = financing_amount
            result["dilution"] = dilution

            # 大额融资提升家族声望
            if financing_amount > 1000000:
                prestige_gain = random.randint(3, 8)
                game_state.family_prestige += prestige_gain
                add_event(game_state, f"「{character.business_name}」的大额融资提升了家族声望。")
                result["prestige_gain"] = prestige_gain

        add_event(game_state, f"{character.name}的{focus}策略取得了成功，企业「{character.business_name}」有所提升。")
    else:
        outcome = "failure"
        if focus == "市场推广":
            reputation_change = random.randint(-5, 5)
            old_reputation = character.business_reputation
            character.business_reputation = max(10, min(100, character.business_reputation + reputation_change))
            if reputation_change > 0:
                add_event(game_state, f"企业声誉从{old_reputation}小幅上升到{character.business_reputation}。")
            elif reputation_change < 0:
                add_event(game_state, f"企业声誉从{old_reputation}下降到{character.business_reputation}。")
            result["reputation_change"] = reputation_change

        elif focus == "人才招聘":
            scale_change = random.uniform(-1, 2)
            old_scale = character.business_scale
            character.business_scale = max(5, min(100, character.business_scale + scale_change))
            character.business_employees = int(character.business_scale / 2)
            character.business_value = character.business_scale * 10000 * (character.business_reputation / 50)
            if scale_change > 0:
                add_event(game_state, f"企业规模从{old_scale:.1f}小幅上升到{character.business_scale:.1f}。")
            elif scale_change < 0:
                add_event(game_state, f"企业规模从{old_scale:.1f}下降到{character.business_scale:.1f}。")
            result["scale_change"] = scale_change

        elif focus == "产品研发":
            profit_change = random.randint(-500, 500)
            old_profit = character.business_profit
            character.business_profit += profit_change
            if profit_change > 0:
                add_event(game_state, f"企业月利润小幅增加了{profit_change}元，达到{character.business_profit}元。")
            elif profit_change < 0:
                add_event(game_state, f"企业月利润减少了{abs(profit_change)}元，降至{character.business_profit}元。")
            result["profit_change"] = profit_change

        elif focus == "成本控制":
            value_change = character.business_value * random.randint(-10, 5) / 100
            character.business_value += value_change
            if value_change > 0:
                add_event(game_state, f"企业经营略有改善，企业估值增加了{value_change:.0f}元。")
            elif value_change < 0:
                add_event(game_state, f"企业经营略显不稳，企业估值减少了{abs(value_change):.0f}元。")
            result["value_change"] = value_change

        elif focus == "战略调整":
            reputation_change = random.randint(-15, 5) / 3
            character.business_reputation = max(10, min(100, character.business_reputation + reputation_change))
            profit_change = random.randint(-15, 5) * 50
            character.business_profit += profit_change
            value_change = random.randint(-15, 5) * 1000
            character.business_value += value_change
            if value_change > 0:
                add_event(game_state, f"企业战略调整有一些积极效果，但未达预期。")
            else:
                add_event(game_state, f"企业战略调整不当，长期发展受阻，企业估值下降。")
            result["reputation_change"] = reputation_change
            result["profit_change"] = profit_change
            result["value_change"] = value_change

        elif focus == "融资扩张":
            # 融资失败
            reputation_loss = abs(random.randint(-10, 0)) / 2
            character.business_reputation -= reputation_loss
            stress_increase = random.randint(10, 20)
            character.stress_level += stress_increase
            add_event(game_state, f"企业融资失败，声誉受损，{character.name}承受了不小的压力。")

            # 随机融资失败的原因
            reasons = [
                "投资者认为估值过高",
                "市场前景不明朗",
                "竞争对手同时在融资",
                "商业模式缺乏可持续性",
                "财务数据不够透明"
            ]
            failure_reason = random.choice(reasons)
            add_event(game_state, f"融资失败的主要原因是: {failure_reason}。")
            result["reputation_loss"] = reputation_loss
            result["stress_increase"] = stress_increase
            result["failure_reason"] = failure_reason

        add_event(game_state, f"{character.name}的{focus}策略效果一般，企业「{character.business_name}」变化不大。")

    # 更新企业员工数
    character.business_employees = int(character.business_scale / 2)

    # 管理活动增加领导力经验
    if random.random() < 0.3:  # 30%概率提升领导力
        leadership_gain = 0.2
        character.leadership += leadership_gain
        result["leadership_gain"] = leadership_gain

    # 管理活动增加相关人脉
    if random.random() < 0.2:  # 20%概率提升人脉
        network_gain = random.randint(1, 2)
        character.network["商业"] += network_gain
        result["network_gain"] = network_gain

    result["outcome"] = outcome
    result["business_profit"] = character.business_profit
    result["business_scale"] = character.business_scale
    result["business_value"] = character.business_value
    result["business_reputation"] = character.business_reputation

    return result


def activity_date(game_state, character):
    """约会或寻找伴侣活动"""
    energy_cost = random.randint(10, 20)
    if character.energy < energy_cost:
        add_event(game_state, f"{character.name}太累了，无法进行社交活动。")
        return {"success": False, "message": "精力不足", "required_energy": energy_cost}

    character.energy -= energy_cost

    result = {
        "success": True,
        "message": "约会活动",
        "relationship_status": character.relationship_status
    }

    # 根据角色关系状态处理不同情况
    if character.relationship_status == "单身":
        # 寻找伴侣 - 简化版本，实际应该使用更复杂的匹配逻辑
        context = [
            {
                "role": "system",
                "content": json.dumps({
                    "角色": {
                        "姓名": character.name,
                        "性别": character.gender,
                        "年龄": character.age,
                        "魅力": character.charm,
                        "外貌": character.appearance,
                        "情商": character.emotional_intelligence,
                        "职业": character.job
                    }
                }, ensure_ascii=False)
            }
        ]

        prompt = "请描述这个单身角色主动寻找恋爱对象的经历（100字以内）。"
        date_result = ai_interaction(prompt, context)
        add_event(game_state, date_result)

        result["event"] = date_result
        result["activity"] = "寻找伴侣"

        # 遇到潜在伴侣的概率取决于魅力和外貌
        find_partner_chance = (character.charm + character.appearance) / 300  # 最高约33%

        if random.random() < find_partner_chance:
            potential_partner = generate_potential_partner(character)
            add_event(game_state,
                      f"{character.name}遇到了一个有好感的对象：{potential_partner['name']}，{potential_partner['age']}岁，{potential_partner['job']}。")

            result["met_partner"] = True
            result["partner"] = potential_partner

            # 追求成功的概率
            pursue_chance = (character.charm + character.appearance) / 200  # 最高约50%

            if random.random() < pursue_chance:
                # 成功建立关系
                character.relationship_status = "恋爱中"
                character.happiness += random.randint(10, 30)

                context.append({
                    "role": "system",
                    "content": json.dumps({
                        "对象": {
                            "姓名": potential_partner['name'],
                            "性别": potential_partner['gender'],
                            "年龄": potential_partner['age'],
                            "职业": potential_partner['job']
                        }
                    }, ensure_ascii=False)
                })

                prompt = "请描述这个角色成功追求对象的过程和初期恋爱关系（100字以内）。"
                relationship_description = ai_interaction(prompt, context)
                add_event(game_state, relationship_description)

                result["relationship"] = "恋爱中"
                result["relationship_description"] = relationship_description
                result["happiness_gain"] = character.happiness
            else:
                # 表白失败
                happiness_loss = random.randint(5, 15)
                character.happiness -= happiness_loss
                add_event(game_state, f"{character.name}向{potential_partner['name']}表白失败，感到有些失落。")

                result["relationship"] = "单身"
                result["outcome"] = "rejection"
                result["happiness_loss"] = happiness_loss
        elif character.relationship_status == "恋爱中":
            # 约会
            happiness_gain = random.randint(5, 15)
            character.happiness += happiness_gain

            # 随机约会场景
            date_scenarios = [
                "共进晚餐",
                "看电影",
                "公园散步",
                "咖啡馆聊天",
                "逛街购物",
                "游乐场玩耍",
                "博物馆参观",
                "听音乐会"
            ]

            scenario = random.choice(date_scenarios)
            add_event(game_state, f"{character.name}与伴侣{scenario}，度过了愉快的时光。")

            result["activity"] = "约会"
            result["scenario"] = scenario
            result["happiness_gain"] = happiness_gain

            # 特殊事件：求婚提示
            if random.random() < 0.1:  # 10%概率
                add_event(game_state, "这次约会非常成功，感情更进一步。也许是时候考虑求婚了？")
                result["marriage_hint"] = True

        elif character.relationship_status == "已婚" and character.spouse:
            # 陪伴配偶
            happiness_gain = random.randint(3, 10)
            character.happiness += happiness_gain
            character.spouse.happiness += happiness_gain

            # 增加关系满意度
            relationship_improvement = random.randint(2, 5)
            if hasattr(character, "relationship_satisfaction"):
                character.relationship_satisfaction += relationship_improvement
            if hasattr(character.spouse, "relationship_satisfaction"):
                character.spouse.relationship_satisfaction += relationship_improvement

            # 随机活动
            activities = [
                "共进晚餐",
                "一起看电影",
                "在家闲聊",
                "规划未来",
                "回忆往事",
                "一起做家务",
                "探讨共同爱好"
            ]

            activity_done = random.choice(activities)
            add_event(game_state, f"{character.name}与{character.spouse.name}{activity_done}，增进了夫妻感情。")

            result["activity"] = "陪伴配偶"
            result["scenario"] = activity_done
            result["happiness_gain"] = happiness_gain
            result["relationship_improvement"] = relationship_improvement

            # 关系改善
            if hasattr(character, "is_cheating") and character.is_cheating:
                if random.random() < 0.1:  # 10%概率反思出轨
                    add_event(game_state, f"{character.name}因为与{character.spouse.name}共度美好时光，开始反思婚外情。")
                    if random.random() < 0.5:  # 50%概率结束出轨
                        if hasattr(character, "cheating_partner"):
                            add_event(game_state, f"{character.name}决定结束与{character.cheating_partner}的婚外情。")
                        else:
                            add_event(game_state, f"{character.name}决定结束婚外情。")

                        character.is_cheating = False
                        result["end_cheating"] = True

        return result


def activity_marriage(game_state, character):
    """婚姻相关活动（求婚或生育）"""
    if character.relationship_status != "恋爱中" and character.relationship_status != "已婚":
        add_event(game_state, f"{character.name}目前没有合适的对象。")
        return {"success": False, "message": "无合适对象"}

    if character.relationship_status == "恋爱中":
        return activity_propose(game_state, character)
    else:  # 已婚
        return activity_have_child(game_state, character)


def activity_propose(game_state, character):
    """求婚活动"""
    energy_cost = 15
    if character.energy < energy_cost:
        add_event(game_state, f"{character.name}太累了，无法求婚。")
        return {"success": False, "message": "精力不足", "required_energy": energy_cost}

    character.energy -= energy_cost

    # 生成伴侣信息
    partner_info = {
        "name": generate_name("女性" if character.gender == "男性" else "男性"),
        "gender": "女性" if character.gender == "男性" else "男性",
        "age": character.age - random.randint(-5, 5),
        "job": random.choice(["教师", "医生", "工程师", "设计师", "销售", "程序员", "会计"])
    }

    # 求婚成功率
    success_chance = 0.7  # 基础70%成功率

    # 调整几率
    if character.assets < 50000:
        success_chance -= 0.1
    if character.mental_state != "正常":
        success_chance -= 0.2
    if character.charm > 80:
        success_chance += 0.1

    result = {
        "success": True,
        "message": "求婚",
        "partner": partner_info,
        "success_chance": success_chance
    }

    if random.random() < success_chance:
        # 创建配偶角色并添加到家族
        spouse = Character(partner_info["name"], partner_info["gender"], partner_info["age"])
        spouse.job = partner_info["job"]
        spouse.salary = random.randint(3000, 10000)

        # 更新关系状态
        character.relationship_status = "已婚"
        spouse.relationship_status = "已婚"

        # 建立配偶关系
        character.spouse = spouse
        spouse.spouse = character

        # 添加到家族成员
        game_state.family_members.append(spouse)

        # 婚礼消费
        wedding_cost = random.randint(30000, 100000)
        character.assets -= min(character.assets * 0.7, wedding_cost)

        add_event(game_state, f"{character.name}向{spouse.name}求婚成功！举办了一场花费{wedding_cost}元的婚礼。")

        # 婚礼带来的变化
        happiness_gain = random.randint(20, 40)
        stress_reduction = random.randint(10, 20)
        character.happiness += happiness_gain
        character.stress_level -= stress_reduction

        result["outcome"] = "success"
        result["spouse"] = spouse.to_dict() if hasattr(spouse, 'to_dict') else {"name": spouse.name}
        result["wedding_cost"] = wedding_cost
        result["happiness_gain"] = happiness_gain
        result["stress_reduction"] = stress_reduction

        # AI生成婚礼描述
        context = [
            {
                "role": "system",
                "content": json.dumps({
                    "新郎": {
                        "姓名": character.name if character.gender == "男性" else spouse.name,
                        "年龄": character.age if character.gender == "男性" else spouse.age,
                        "职业": character.job if character.gender == "男性" else spouse.job
                    },
                    "新娘": {
                        "姓名": spouse.name if character.gender == "男性" else character.name,
                        "年龄": spouse.age if character.gender == "男性" else character.age,
                        "职业": spouse.job if character.gender == "男性" else character.job
                    },
                    "婚礼预算": wedding_cost
                }, ensure_ascii=False)
            }
        ]

        prompt = "请简短描述这对新人的婚礼场景和新婚生活（100字以内）。"
        wedding_description = ai_interaction(prompt, context)
        add_event(game_state, wedding_description)

        result["wedding_description"] = wedding_description

        return result
    else:
        # 求婚失败
        happiness_loss = random.randint(20, 40)
        stress_increase = random.randint(20, 40)
        character.happiness -= happiness_loss
        character.stress_level += stress_increase
        character.relationship_status = "单身"

        add_event(game_state, f"{character.name}的求婚被拒绝了，感到非常难过。")

        result["outcome"] = "rejection"
        result["happiness_loss"] = happiness_loss
        result["stress_increase"] = stress_increase

        return result


def activity_have_child(game_state, character):
    """尝试生育子女"""
    if not character.spouse:
        add_event(game_state, f"{character.name}需要有配偶才能尝试生育。")
        return {"success": False, "message": "无配偶"}

    if character.gender == character.spouse.gender:
        add_event(game_state, f"同性伴侣无法自然生育，请考虑领养。")
        return {"success": False, "message": "同性伴侣无法自然生育"}

    # 确定女方
    female = character if character.gender == "女性" else character.spouse

    # 检查女方年龄是否适合生育
    if female.age < 18 or female.age > 45:
        add_event(game_state, f"女方年龄{female.age}岁，不适合生育。")
        return {"success": False, "message": "年龄不适合生育", "female_age": female.age}

    # 生育成功率
    success_chance = 0.6  # 基础成功率

    # 年龄影响
    if female.age < 30:
        age_factor = 1.0
    elif female.age < 35:
        age_factor = 0.8
    elif female.age < 40:
        age_factor = 0.5
    else:
        age_factor = 0.2

    success_chance *= age_factor

    # 健康影响
    health_factor = (female.health + character.spouse.health) / 200  # 0.5-1.0范围
    success_chance *= health_factor

    # 是否主动尝试生育
    if hasattr(female, "fertility_boosted") and female.fertility_boosted:
        success_chance *= 2.0

    # 避孕措施
    if hasattr(female, "contraception_active") and female.contraception_active:
        success_chance *= 0.1

    result = {
        "success": True,
        "message": "尝试生育",
        "female": female.name,
        "success_chance": success_chance,
        "age_factor": age_factor,
        "health_factor": health_factor
    }

    if random.random() < success_chance:
        # 生育成功
        child_gender = random.choice(["男性", "女性"])
        child_name = generate_name(child_gender)

        # 创建子女角色
        child = Character(child_name, child_gender, 0)

        # 设置家族关系
        child.parents = [character, character.spouse]
        character.children.append(child)
        character.spouse.children.append(child)

        # 添加到家族
        game_state.family_members.append(child)

        # 生育带来的变化
        health_impact = random.randint(5, 15)
        female.health -= health_impact  # 生育对健康的影响

        happiness_gain = random.randint(20, 40)
        character.happiness += happiness_gain
        character.spouse.happiness += happiness_gain

        add_event(game_state, f"喜讯！{female.name}生下了一个健康的{child_gender}婴儿，取名为{child_name}。")

        # 生育费用
        birth_cost = random.randint(5000, 20000)
        character.assets -= min(character.assets * 0.5, birth_cost)

        result["outcome"] = "success"
        result["child_name"] = child_name
        result["child_gender"] = child_gender
        result["health_impact"] = health_impact
        result["happiness_gain"] = happiness_gain
        result["birth_cost"] = birth_cost

        # 更新成就
        game_state.update_achievement("多子多福")

        # AI生成描述
        context = [
            {
                "role": "system",
                "content": json.dumps({
                    "父亲": {
                        "姓名": character.name if character.gender == "男性" else character.spouse.name
                    },
                    "母亲": {
                        "姓名": character.spouse.name if character.gender == "男性" else character.name
                    },
                    "新生儿": {
                        "姓名": child_name,
                        "性别": child_gender
                    }
                }, ensure_ascii=False)
            }
        ]

        prompt = "请简短描述这对夫妻迎接新生儿的温馨场景（100字以内）。"
        birth_description = ai_interaction(prompt, context)
        add_event(game_state, birth_description)

        result["birth_description"] = birth_description
    else:
        # 生育失败
        add_event(game_state, f"尝试生育未成功，可以继续尝试或考虑其他选择。")
        result["outcome"] = "failure"

    return result


def activity_plastic_surgery(game_state, character, params):
    """整容活动"""
    if character.assets < 20000:
        add_event(game_state, f"{character.name}资金不足，无法进行整容手术。至少需要20000元。")
        return {"success": False, "message": "资金不足", "required_assets": 20000}

    # 获取整容类型
    surgery_type = params.get("type", "微整形")

    # 整容费用和效果
    surgery_options = {
        "微整形": {"cost": 20000, "risk": 0.05, "min_effect": 5, "max_effect": 15},
        "面部整形": {"cost": 50000, "risk": 0.15, "min_effect": 10, "max_effect": 25},
        "全面改造": {"cost": 150000, "risk": 0.3, "min_effect": 20, "max_effect": 40}
    }

    selected_surgery = surgery_options.get(surgery_type, surgery_options["微整形"])

    # 检查资金
    if character.assets < selected_surgery["cost"]:
        add_event(game_state, f"{character.name}资金不足，无法支付¥{selected_surgery['cost']}的整容费用。")
        return {"success": False, "message": "资金不足", "required_assets": selected_surgery["cost"]}

    # 扣除费用
    character.assets -= selected_surgery["cost"]

    # 手术结果
    complications = random.random() < selected_surgery["risk"]

    result = {
        "success": True,
        "message": "整容手术",
        "surgery_type": surgery_type,
        "cost": selected_surgery["cost"],
        "risk": selected_surgery["risk"]
    }

    # 应用效果
    if not character.has_plastic_surgery:
        # 首次整容，记录原始外貌
        character.original_appearance = character.appearance
        character.has_plastic_surgery = True

    # 整容效果
    if complications:
        # 手术并发症
        effect = random.randint(-10, selected_surgery["min_effect"] // 2)
        character.surgery_quality = character.appearance + effect
        character.surgery_complications = True
        character.appearance += effect

        add_event(game_state, f"{character.name}的整容手术出现了并发症，外貌{'+' if effect >= 0 else ''}{effect}。")

        # 健康影响
        health_impact = random.randint(5, 15)
        happiness_loss = random.randint(10, 30)
        stress_increase = random.randint(10, 30)

        character.health -= health_impact
        character.happiness -= happiness_loss
        character.stress_level += stress_increase

        result["outcome"] = "complications"
        result["effect"] = effect
        result["health_impact"] = health_impact
        result["happiness_loss"] = happiness_loss
        result["stress_increase"] = stress_increase
    else:
        # 手术成功
        effect = random.randint(selected_surgery["min_effect"], selected_surgery["max_effect"])
        character.surgery_quality = character.appearance + effect
        character.surgery_complications = False
        character.appearance += effect

        add_event(game_state, f"{character.name}的整容手术非常成功，外貌+{effect}。")

        happiness_gain = random.randint(10, 30)
        character.happiness += happiness_gain

        result["outcome"] = "success"
        result["effect"] = effect
        result["happiness_gain"] = happiness_gain

    # 社会反应
    if character.appearance > 85:
        add_event(game_state, f"整容后的{character.name}吸引了更多关注，社交活动更加顺利。")

        charm_gain = random.randint(1, 5)
        character.charm += charm_gain
        result["charm_gain"] = charm_gain

    return result


def activity_mental_health(game_state, character, params):
    """心理健康护理活动"""
    energy_cost = random.randint(10, 20)
    if character.energy < energy_cost:
        add_event(game_state, f"{character.name}太累了，无法进行心理护理。")
        return {"success": False, "message": "精力不足", "required_energy": energy_cost}

    character.energy -= energy_cost

    # 获取心理治疗类型
    treatment_type = params.get("type", "自我调节")

    result = {
        "success": True,
        "message": "心理健康护理",
        "treatment_type": treatment_type,
        "mental_state": character.mental_state,
        "stress_level": character.stress_level,
        "happiness": character.happiness
    }

    if character.mental_state == "正常" and character.happiness > 50 and character.stress_level < 40:
        # 普通的放松活动
        activities = [
            "看电影",
            "听音乐",
            "读书",
            "冥想",
            "散步",
            "做瑜伽"
        ]

        activity = random.choice(activities)

        happiness_gain = random.randint(5, 10)
        stress_reduction = random.randint(5, 15)

        character.happiness += happiness_gain
        character.stress_level = max(0, character.stress_level - stress_reduction)

        add_event(game_state, f"{character.name}{activity}放松身心，感到心情愉悦。")

        result["activity"] = activity
        result["happiness_gain"] = happiness_gain
        result["stress_reduction"] = stress_reduction

        return result

    # 心理健康护理效果
    treatment_effects = {
        "自我调节": {"effect_level": 0.3, "cost": 0},
        "朋友倾诉": {"effect_level": 0.5, "cost": 0},
        "专业心理咨询": {"effect_level": 0.8, "cost": 3000}
    }

    selected_treatment = treatment_effects.get(treatment_type, treatment_effects["自我调节"])

    # 专业咨询需要费用
    if selected_treatment["cost"] > 0:
        if character.assets < selected_treatment["cost"]:
            add_event(game_state, f"{character.name}资金不足，无法支付专业心理咨询费用。")
            return {"success": False, "message": "资金不足", "required_assets": selected_treatment["cost"]}
        character.assets -= selected_treatment["cost"]
        result["cost"] = selected_treatment["cost"]

    effect_level = selected_treatment["effect_level"]

    # 压力缓解
    stress_reduction = int(character.stress_level * effect_level * 0.5)
    character.stress_level = max(0, character.stress_level - stress_reduction)
    result["stress_reduction"] = stress_reduction

    # 幸福感提升
    happiness_gain = int((100 - character.happiness) * effect_level * 0.3)
    character.happiness = min(100, character.happiness + happiness_gain)
    result["happiness_gain"] = happiness_gain

    # 心理状态改善
    if character.mental_state != "正常":
        if character.mental_state == "抑郁":
            depression_reduction = int(70 * effect_level)
            character.depression_risk = max(0, character.depression_risk - depression_reduction)
            result["depression_reduction"] = depression_reduction

            if character.depression_risk < 50:
                character.mental_state = "正常"
                add_event(game_state, f"{character.name}的抑郁症状得到了缓解，恢复了正常状态。")
                result["outcome"] = "recovered"
            else:
                add_event(game_state, f"{character.name}的抑郁症状有所缓解，但仍需继续治疗。")
                result["outcome"] = "improved"
        elif character.mental_state == "焦虑":
            anxiety_reduction = int(60 * effect_level)
            character.anxiety_risk = max(0, character.anxiety_risk - anxiety_reduction)
            result["anxiety_reduction"] = anxiety_reduction

            if character.anxiety_risk < 40:
                character.mental_state = "正常"
                add_event(game_state, f"{character.name}的焦虑症状得到了缓解，恢复了正常状态。")
                result["outcome"] = "recovered"
            else:
                add_event(game_state, f"{character.name}的焦虑症状有所缓解，但仍需继续治疗。")
                result["outcome"] = "improved"
    else:
        if treatment_type == "自我调节":
            add_event(game_state, f"{character.name}通过自我调节，压力减少，心情变好。")
        elif treatment_type == "朋友倾诉":
            add_event(game_state, f"{character.name}向朋友倾诉了烦恼，感到轻松了许多。")
        else:
            add_event(game_state, f"{character.name}接受了专业心理咨询，获得了很好的心理指导。")

        result["outcome"] = "maintained"

    return result


def activity_charity(game_state, character, params):
    """慈善捐款活动"""
    # 检查资金
    if character.assets < 1000:
        add_event(game_state, f"{character.name}资金不足，无法进行慈善捐款。")
        return {"success": False, "message": "资金不足", "minimum_assets": 1000}

    # 获取捐款信息
    charity_type = params.get("type", "教育基金会")
    amount = params.get("amount", 1000)

    if amount < 1000:
        add_event(game_state, "最低捐款额为1000元。")
        return {"success": False, "message": "捐款金额过低", "minimum_amount": 1000}

    if amount > character.assets:
        add_event(game_state, f"{character.name}资金不足，无法捐款{amount}元。")
        return {"success": False, "message": "资金不足", "available_assets": character.assets}

    # 捐款效果
    charity_effects = {
        "教育基金会": {"prestige_gain": 0.2, "happiness_gain": 5},
        "医疗救助": {"prestige_gain": 0.5, "happiness_gain": 10},
        "扶贫项目": {"prestige_gain": 1.0, "happiness_gain": 15},
        "环保组织": {"prestige_gain": 0.3, "happiness_gain": 8}
    }

    selected_charity = charity_effects.get(charity_type, charity_effects["教育基金会"])

    # 扣除资金
    character.assets -= amount

    # 计算获得的声望和幸福感
    amount_factor = amount / 1000  # 基准为1000元
    prestige_gain = selected_charity["prestige_gain"] * amount_factor
    happiness_gain = selected_charity["happiness_gain"]

    # 应用效果
    game_state.family_prestige += prestige_gain
    character.happiness = min(100, character.happiness + happiness_gain)

    add_event(game_state, f"{character.name}向{charity_type}捐款¥{amount:.0f}，")
    add_event(game_state, f"家族声望增加{prestige_gain:.1f}点，个人幸福感提升。")

    result = {
        "success": True,
        "message": "慈善捐款",
        "charity_type": charity_type,
        "amount": amount,
        "prestige_gain": prestige_gain,
        "happiness_gain": happiness_gain
    }

    # 大额捐款特殊效果
    if amount >= 100000:
        add_event(game_state, f"这笔巨额捐款获得了社会广泛关注，{character.name}的慈善形象得到提升。")

        career_prestige_gain = random.randint(5, 10)
        character.career_prestige += career_prestige_gain
        result["career_prestige_gain"] = career_prestige_gain

        # 可能获得荣誉称号
        if random.random() < 0.5:
            title = random.choice(["爱心大使", "慈善之星", "公益楷模"])
            add_event(game_state, f"{character.name}被授予\"{title}\"称号。")
            result["honorary_title"] = title

        # 记录捐款历史
        if not hasattr(character, "charity_history"):
            character.charity_history = []

        character.charity_history.append({
            "charity": charity_type,
            "amount": amount,
            "day": game_state.current_day
        })

        # 累计捐款成就
        if not hasattr(character, "total_donations"):
            character.total_donations = 0

        character.total_donations += amount

        if character.total_donations >= 1000000:
            add_event(game_state, "累计慈善捐款突破百万，获得\"慈善家\"称号！")
            game_state.family_prestige += 10
            result["achievement"] = "慈善家"
            result["extra_prestige"] = 10

    return result


# 实用函数
def generate_name(gender):
    """生成随机中文名字"""
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


# 添加实用工具函数
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


