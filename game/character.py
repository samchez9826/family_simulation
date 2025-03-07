import random
from typing import Dict, List, Any, Optional
import json


class Character:
    def __init__(self, name, gender, age):
        # 基本信息
        self.name = name
        self.gender = gender
        self.age = age
        self.birthday = random.randint(1, 365)
        self.alive = True
        self.spouse = None
        self.children = []
        self.parents = []
        self.siblings = []
        self.relationships = {}  # {character_id: {"intimacy": 值, "trust": 值}}

        # 应用家族特质加成
        trait_bonus = self._apply_family_traits()

        # 基础属性 (1-100)
        self.energy = 100
        self.health = random.randint(60, 100) + trait_bonus.get("health", 0)
        self.appearance = random.randint(40, 90) + trait_bonus.get("appearance", 0)
        self.charm = random.randint(40, 90) + trait_bonus.get("charm", 0)
        self.intelligence = random.randint(40, 100) + trait_bonus.get("intelligence", 0)
        self.emotional_intelligence = random.randint(40, 90) + trait_bonus.get("emotional_intelligence", 0)
        self.financial_intelligence = random.randint(40, 90) + trait_bonus.get("financial_intelligence", 0)
        self.luck = random.randint(30, 100)

        # 新增：身高体重属性（厘米/千克）及其对健康和颜值的影响
        if gender == "男性":
            self.height = random.randint(165, 190)
            self.weight = random.randint(60, 90)
            # 理想BMI为22左右，过高过低都影响健康
            self.ideal_weight = (self.height / 100) ** 2 * 22
        else:
            self.height = random.randint(155, 175)
            self.weight = random.randint(45, 75)
            self.ideal_weight = (self.height / 100) ** 2 * 21

        # 计算身高对外貌的加成/减成
        if gender == "男性":
            if self.height > 180:  # 男性高个加分
                self.appearance += min(10, (self.height - 180) // 2)
            elif self.height < 170:  # 男性矮个减分
                self.appearance -= min(10, (170 - self.height) // 2)
        else:
            if self.height > 170:  # 女性高个加分（但不如男性明显）
                self.appearance += min(5, (self.height - 170) // 2)
            elif self.height < 160:  # 女性矮个略减分
                self.appearance -= min(5, (160 - self.height) // 3)

        # 计算体重对健康与外貌的影响
        bmi = self.weight / ((self.height / 100) ** 2)
        if bmi < 18.5:  # 偏瘦
            self.health -= min(10, int((18.5 - bmi) * 3))
            self.appearance -= min(5, int((18.5 - bmi) * 2))
        elif bmi > 25:  # 偏胖
            self.health -= min(15, int((bmi - 25) * 3))
            self.appearance -= min(15, int((bmi - 25) * 3))

        # 隐藏属性
        self.career_prestige = 10
        self.personal_connections = 10
        self.stress_level = 20
        self.happiness = 70
        self.sexual_orientation = random.choices(["异性恋", "同性恋", "双性恋"], weights=[0.9, 0.05, 0.05])[0]
        self.sex_drive = random.randint(30, 90)

        # 新增心理健康相关属性
        self.self_esteem = random.randint(50, 90)  # 自尊心
        self.trauma = 0  # 心理创伤累积
        self.depression_risk = 0  # 抑郁风险
        self.anxiety_risk = 0  # 焦虑风险

        # 新增婚姻关系相关属性
        self.relationship_satisfaction = 80  # 关系满意度
        self.loyalty = random.randint(70, 100)  # 忠诚度
        self.is_cheating = False  # 是否出轨
        self.has_forgiven_cheating = False  # 是否原谅过出轨
        self.cheating_partner = None  # 出轨对象

        # 新增家庭暴力相关属性
        self.violence_tendency = random.randint(0, 20)  # 暴力倾向
        self.has_abused = False  # 是否施暴过
        self.has_been_abused = False  # 是否被施暴过
        self.abuse_trauma = 0  # 受暴创伤

        # 状态
        self.job = "无业"
        self.salary = 0
        self.assets = 1000 + trait_bonus.get("assets", 0)
        self.debt = 0  # 债务
        self.education_level = "高中"
        self.relationship_status = "单身"
        self.mental_state = "正常"

        # 新增创业相关属性
        self.has_business = False
        self.business_name = ""
        self.business_type = ""
        self.business_scale = 0  # 0-100
        self.business_profit = 0
        self.business_value = 0
        self.business_employees = 0
        self.business_reputation = 50  # 0-100
        self.leadership = random.randint(40, 90)  # 领导能力
        self.business_vision = random.randint(40, 90)  # 商业眼光
        self.risk_management = random.randint(40, 90)  # 风险管理能力

        # 整容状态
        self.has_plastic_surgery = False  # 是否整过容
        self.original_appearance = self.appearance  # 原始外貌
        self.surgery_quality = 0  # 整容质量
        self.surgery_complications = False  # 整容并发症

        # 遗嘱系统
        self.has_will = False  # 是否立有遗嘱
        self.will_beneficiaries = {}  # {角色ID: 分配比例} - 默认为法定继承

        # 生育计划
        self.fertility_boosted = False  # 是否使用生育措施提高受孕几率
        self.contraception_active = False  # 是否在使用避孕措施

        # 投资组合
        self.investments = {
            "股票": 0,
            "基金": 0,
            "债券": 0,
            "房产": 0,
            "其他": 0
        }
        self.investment_returns = {}  # 记录投资回报情况

        # 人脉网络（增强型）
        self.network = {
            "商业": 0,  # 商业人脉
            "政界": 0,  # 政界人脉
            "学术": 0,  # 学术人脉
            "娱乐": 0,  # 娱乐圈人脉
            "医疗": 0  # 医疗圈人脉
        }

        # 新增特殊事件计数器
        self.special_event_cooldowns = {}

    def _apply_family_traits(self):
        """应用家族特质加成"""
        bonus = {}
        # 在 Web 版本中，家族特质会通过 API 传递
        return bonus

    def calculate_bmi(self):
        """计算BMI指数"""
        return self.weight / ((self.height / 100) ** 2)

    def update_appearance_from_physique(self):
        """根据身高体重更新外貌值"""
        # 重置外貌（消除之前的身高体重影响）
        self.appearance = self.original_appearance if not self.has_plastic_surgery else self.surgery_quality

        # 根据性别计算身高影响
        if self.gender == "男性":
            if self.height > 180:
                self.appearance += min(10, (self.height - 180) // 2)
            elif self.height < 170:
                self.appearance -= min(10, (170 - self.height) // 2)
        else:
            if self.height > 170:
                self.appearance += min(5, (self.height - 170) // 2)
            elif self.height < 160:
                self.appearance -= min(5, (160 - self.height) // 3)

        # 计算体重影响
        bmi = self.calculate_bmi()
        if bmi < 18.5:  # 偏瘦
            self.appearance -= min(5, int((18.5 - bmi) * 2))
        elif bmi > 25:  # 偏胖
            self.appearance -= min(15, int((bmi - 25) * 3))

    def get_weight_status(self):
        """获取体重状态描述"""
        bmi = self.calculate_bmi()
        if bmi < 18.5:
            return "偏瘦"
        elif bmi < 24:
            return "正常"
        elif bmi < 28:
            return "偏胖"
        else:
            return "肥胖"

    def get_status_display(self) -> str:
        """获取角色状态显示文本"""
        status = f"姓名: {self.name}  性别: {self.gender}  年龄: {self.age}岁\n"
        status += f"健康: {self.health}  精力: {self.energy}  外貌: {self.appearance}\n"
        status += f"魅力: {self.charm}  智商: {self.intelligence}  情商: {self.emotional_intelligence}\n"
        status += f"财商: {self.financial_intelligence}  幸运: {self.luck}\n"
        status += f"身高: {self.height}cm  体重: {self.weight}kg  体型: {self.get_weight_status()}\n"
        status += f"工作: {self.job}  月薪: ¥{self.salary}  资产: ¥{self.assets}\n"
        status += f"学历: {self.education_level}  情感状态: {self.relationship_status}\n"
        status += f"心理状态: {self.mental_state}  快乐指数: {self.happiness}\n"

        # 显示投资组合
        total_investments = sum(self.investments.values())
        if total_investments > 0:
            status += f"投资组合: 总计¥{total_investments} "
            for inv_type, amount in self.investments.items():
                if amount > 0:
                    status += f"[{inv_type}: ¥{amount}] "
            status += "\n"

        if self.has_business:
            status += f"创业状态: 拥有企业「{self.business_name}」 规模: {self.business_scale} 月利润: ¥{self.business_profit}\n"

        if self.has_plastic_surgery:
            status += f"整容状态: 已整容 (原始外貌: {self.original_appearance})"
            if self.surgery_complications:
                status += " [存在并发症]"
            status += "\n"

        if self.mental_state != "正常":
            status += f"注意: 当前处于「{self.mental_state}」状态，需要关注心理健康\n"

        # 人脉网络概览
        total_network = sum(self.network.values())
        if total_network > 20:  # 只有当人脉达到一定程度才显示
            status += f"人脉网络: 总体评分 {total_network} "
            top_networks = sorted(self.network.items(), key=lambda x: x[1], reverse=True)[:2]
            for net_type, value in top_networks:
                if value > 10:
                    status += f"[{net_type}圈: {value}] "
            status += "\n"

        return status

    def get_network_benefits(self, network_type):
        """获取特定人脉网络可能带来的好处"""
        if self.network[network_type] < 20:
            return "尚未建立有效人脉"

        benefits = {
            "商业": ["可获得更多投资机会", "企业估值提升", "商业合作邀请"],
            "政界": ["行政办事更顺利", "获取政策信息优先", "政府扶持项目"],
            "学术": ["学术进修机会", "研究合作邀请", "讲座机会"],
            "娱乐": ["获得明星资源", "参与活动优先", "广告代言机会"],
            "医疗": ["优质医疗资源", "健康咨询优惠", "紧急就医通道"]
        }

        level = "初级"
        if self.network[network_type] > 50:
            level = "中级"
        if self.network[network_type] > 80:
            level = "高级"

        return f"{level}{random.choice(benefits[network_type])}"

    def update_daily(self):
        """每日更新角色状态"""
        # 这里需要从外部传入game_state参数
        # 简化版本：仅处理基本属性更新

        # 精力自然恢复 (每天恢复一点)
        if self.energy < 100:
            self.energy = min(100, self.energy + 1)

        # 压力影响健康和快乐
        if self.stress_level > 70:
            self.happiness -= 1
            if random.random() < 0.1:
                self.health -= 1

        # 快乐度影响精神状态
        self.update_mental_state()

        # 创业业务每日更新
        if self.has_business:
            self.update_business()

        # 整容并发症检查
        if self.has_plastic_surgery and not self.surgery_complications:
            if random.random() < 0.001:  # 每天0.1%的并发症概率
                self.surgery_complications = True
                # 这里需要外部事件系统支持
                from family_simulation.game.events import add_event
                add_event(f"{self.name}的整容手术出现了并发症，外貌受到影响。")
                self.appearance -= random.randint(5, 15)

        # 更新身体状况对属性的影响
        self.update_appearance_from_physique()

        # 更新投资回报
        self.update_investments()

    def update_investments(self):
        """更新投资回报"""
        if sum(self.investments.values()) == 0:
            return

        # 获取当前经济环境影响 (默认为正常)
        economy_status = "正常"  # 这个值应该从游戏状态获取
        economy_multipliers = {
            "繁荣": 1.5,
            "正常": 1.0,
            "衰退": 0.6
        }
        economy_factor = economy_multipliers.get(economy_status, 1.0)

        # 计算每种投资类型的回报
        for inv_type, amount in self.investments.items():
            if amount <= 0:
                continue

            # 设置基础回报率和波动范围
            base_rates = {
                "股票": {"base": 0.12, "volatility": 0.15},
                "基金": {"base": 0.08, "volatility": 0.08},
                "债券": {"base": 0.05, "volatility": 0.03},
                "房产": {"base": 0.10, "volatility": 0.05},
                "其他": {"base": 0.15, "volatility": 0.20}
            }

            rate_info = base_rates.get(inv_type, {"base": 0.05, "volatility": 0.05})

            # 计算实际回报率
            base_rate = rate_info["base"] * economy_factor
            volatility = rate_info["volatility"]
            daily_rate = base_rate / 365  # 年化回报率转换为日回报率

            # 添加随机波动
            actual_rate = daily_rate + random.uniform(-volatility / 365, volatility / 365)

            # 应用财商修正
            fq_bonus = (self.financial_intelligence - 50) / 500  # -0.1 到 +0.1 的修正
            actual_rate += fq_bonus

            # 计算当日收益
            daily_return = amount * actual_rate

            # 更新资产
            self.assets += daily_return

            # 记录投资回报
            if inv_type not in self.investment_returns:
                self.investment_returns[inv_type] = 0
            self.investment_returns[inv_type] += daily_return

    def update_mental_state(self):
        """更新心理状态"""
        # 抑郁风险增加条件
        if self.happiness < 30 or self.stress_level > 70 or self.trauma > 30:
            self.depression_risk += random.randint(1, 3)
        else:
            self.depression_risk = max(0, self.depression_risk - 1)

        # 焦虑风险增加条件
        if self.stress_level > 60 or self.has_been_abused or self.trauma > 20:
            self.anxiety_risk += random.randint(1, 2)
        else:
            self.anxiety_risk = max(0, self.anxiety_risk - 1)

        # 根据风险值更新心理状态
        if self.mental_state == "正常":
            if self.anxiety_risk > 50:
                self.mental_state = "焦虑"
                # 需要外部事件系统
                from family_simulation.game.events import add_event
                add_event(f"{self.name}因长期压力过大而变得焦虑。")
            elif self.depression_risk > 70:
                self.mental_state = "抑郁"
                # 需要外部事件系统
                from family_simulation.game.events import add_event
                add_event(f"{self.name}陷入了抑郁状态。")
        elif self.mental_state == "焦虑":
            if self.anxiety_risk < 30:
                self.mental_state = "正常"
                # 需要外部事件系统
                from family_simulation.game.events import add_event
                add_event(f"{self.name}的焦虑状态有所缓解，恢复了正常。")
            elif self.depression_risk > 70:
                self.mental_state = "抑郁"
                # 需要外部事件系统
                from family_simulation.game.events import add_event
                add_event(f"{self.name}的焦虑加重为抑郁。")
        elif self.mental_state == "抑郁":
            if self.depression_risk < 40:
                self.mental_state = "焦虑"
                # 需要外部事件系统
                from family_simulation.game.events import add_event
                add_event(f"{self.name}的抑郁状态有所缓解，但仍然焦虑。")

    def update_business(self):
        """更新创业企业状态"""
        if not self.has_business:
            return

        # 基础每日收益
        base_profit = self.business_scale * 10 * (self.business_reputation / 50)

        # 根据经济环境调整 (默认为正常)
        economy_status = "正常"  # 应该从游戏状态获取
        economy_multipliers = {
            "繁荣": 1.5,
            "正常": 1.0,
            "衰退": 0.6
        }
        profit_multiplier = economy_multipliers.get(economy_status, 1.0)

        # 根据个人能力调整
        skill_factor = (
                (self.financial_intelligence + self.business_vision + self.leadership + self.risk_management) / 400)

        # 计算最终收益
        final_profit = base_profit * profit_multiplier * skill_factor

        # 随机波动 (-20% 到 +20%)
        fluctuation = random.uniform(0.8, 1.2)
        final_profit *= fluctuation

        # 更新数据
        self.business_profit = round(final_profit)
        self.assets += self.business_profit

        # 规模增长
        if final_profit > 0 and random.random() < 0.1:  # 10%概率增长
            growth = random.uniform(0.01, 0.05) * self.business_scale
            self.business_scale = min(100, self.business_scale + growth)
            self.business_employees = int(self.business_scale / 2)
            self.business_value = self.business_scale * 10000 * (self.business_reputation / 50)

    def to_dict(self):
        """将角色数据转换为字典，用于JSON序列化"""
        # 基本信息
        result = {
            "name": self.name,
            "gender": self.gender,
            "age": self.age,
            "alive": self.alive,
            "birthday": self.birthday,
            "job": self.job,
            "salary": self.salary,
            "assets": self.assets,
            "debt": self.debt,
            "education_level": self.education_level,
            "relationship_status": self.relationship_status,
            "mental_state": self.mental_state,

            # 基础属性
            "energy": self.energy,
            "health": self.health,
            "appearance": self.appearance,
            "charm": self.charm,
            "intelligence": self.intelligence,
            "emotional_intelligence": self.emotional_intelligence,
            "financial_intelligence": self.financial_intelligence,
            "luck": self.luck,

            # 身体属性
            "height": self.height,
            "weight": self.weight,
            "ideal_weight": self.ideal_weight,
            "weight_status": self.get_weight_status(),

            # 心理属性
            "happiness": self.happiness,
            "stress_level": self.stress_level,
            "self_esteem": self.self_esteem,
            "trauma": self.trauma,
            "depression_risk": self.depression_risk,
            "anxiety_risk": self.anxiety_risk,

            # 投资信息
            "investments": self.investments,
            "investment_returns": self.investment_returns,

            # 人脉网络
            "network": self.network,

            # 企业信息 (如果有)
            "has_business": self.has_business,
        }

        # 如果有企业，添加企业信息
        if self.has_business:
            result["business"] = {
                "name": self.business_name,
                "type": self.business_type,
                "scale": self.business_scale,
                "profit": self.business_profit,
                "value": self.business_value,
                "employees": self.business_employees,
                "reputation": self.business_reputation
            }

        # 如果已婚，添加配偶基本信息
        if self.spouse and hasattr(self.spouse, 'name'):
            result["spouse"] = {
                "name": self.spouse.name,
                "gender": self.spouse.gender,
                "age": self.spouse.age,
                "job": self.spouse.job
            }

        # 如果有子女，添加子女基本信息
        if self.children:
            result["children"] = []
            for child in self.children:
                if hasattr(child, 'name'):
                    result["children"].append({
                        "name": child.name,
                        "gender": child.gender,
                        "age": child.age
                    })

        return result