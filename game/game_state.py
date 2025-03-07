import os
import json
import pickle
import random
import datetime
from typing import Dict, List, Any, Tuple, Optional, Union

# Constants
SAVE_DIR = "saves"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)


class GameState:
    def __init__(self):
        self.current_day = 1
        self.player = None
        self.family_members = []
        self.events_history = []
        self.family_fortune = 10000  # 家族初始财富
        self.family_prestige = 50  # 家族初始声望
        self.current_season = "春季"  # 当前季节
        self.economy_status = "正常"  # 经济状况：繁荣、正常、衰退
        self.is_mobile_ui = True  # 默认使用移动UI
        self.achievements = {}  # 成就系统
        self.game_speed = 1  # 游戏速度：1=正常，2=快速，5=极速
        self.auto_skip = False  # 是否自动跳过平淡日

        # 家族传承特质
        self.family_traits = {
            "智慧传承": 0,  # 增加智商初始值和学习效率
            "商业头脑": 0,  # 增加财商初始值和创业成功率
            "健康基因": 0,  # 增加健康初始值和恢复速度
            "魅力风范": 0,  # 增加魅力和外貌初始值
            "富贵命格": 0  # 增加初始资产和赚钱能力
        }

    def save_game(self, filename="autosave"):
        """保存游戏状态"""
        save_path = os.path.join(SAVE_DIR, f"{filename}.sav")
        try:
            with open(save_path, 'wb') as f:
                pickle.dump(self, f)
            return True, f"游戏已保存至 {save_path}"
        except Exception as e:
            return False, f"保存失败: {e}"

    @staticmethod
    def load_game(filename="autosave"):
        """加载游戏状态"""
        save_path = os.path.join(SAVE_DIR, f"{filename}.sav")
        try:
            with open(save_path, 'rb') as f:
                loaded_game = pickle.load(f)
            return True, loaded_game
        except Exception as e:
            return False, f"加载失败: {e}"

    def get_save_files(self):
        """获取所有存档文件"""
        save_files = []
        for file in os.listdir(SAVE_DIR):
            if file.endswith(".sav"):
                save_files.append(file[:-4])  # 移除.sav后缀
        return save_files

    def update_achievement(self, achievement_id, progress=1):
        """更新成就进度"""
        if achievement_id not in self.achievements:
            self.achievements[achievement_id] = 0

        self.achievements[achievement_id] += progress

        # 成就完成检查和奖励
        self._check_achievement_completion(achievement_id)

    def _check_achievement_completion(self, achievement_id):
        """检查成就是否完成并发放奖励"""
        achievement_goals = {
            "富翁": {"target": 1000000, "reward": "家族财富增加10%"},
            "企业家": {"target": 3, "reward": "创业成功率提高15%"},
            "多子多福": {"target": 5, "reward": "家族声望+20"},
            "长寿家族": {"target": 90, "reward": "家族成员初始健康+10"},
            "名门望族": {"target": 100, "reward": "解锁家族特质'魅力风范'"}
        }

        if achievement_id in achievement_goals:
            goal = achievement_goals[achievement_id]
            if self.achievements[achievement_id] >= goal["target"]:
                if achievement_id + "_completed" not in self.achievements:
                    self.achievements[achievement_id + "_completed"] = True
                    self.add_event(f"成就解锁：【{achievement_id}】! 奖励: {goal['reward']}")
                    self._apply_achievement_reward(achievement_id, goal["reward"])

    def _apply_achievement_reward(self, achievement_id, reward):
        """应用成就奖励"""
        from family_simulation.game.events import add_event

        if "家族财富增加" in reward:
            percentage = int(reward.split("%")[0].split("+")[1])
            bonus = self.family_fortune * (percentage / 100)
            self.family_fortune += bonus
            add_event(self, f"家族财富增加了 {bonus:.0f}!")

        elif "创业成功率提高" in reward:
            # 在创业系统中实现
            add_event(self, "家族成员创业时将更容易成功!")

        elif "家族声望+" in reward:
            amount = int(reward.split("+")[1])
            self.family_prestige += amount
            add_event(self, f"家族声望增加了 {amount}!")

        elif "家族成员初始健康+" in reward:
            # 影响新角色创建
            add_event(self, "家族新成员将拥有更好的健康!")

        elif "解锁家族特质" in reward:
            trait = reward.split("'")[1]
            self.family_traits[trait] = 1
            add_event(self, f"家族特质【{trait}】已解锁!")

    def update_daily(self):
        """每日更新游戏状态"""
        # Import here to avoid circular imports
        import random
        from family_simulation.game.events import generate_random_event, add_event

        # 更新角色状态
        if self.player and hasattr(self.player, 'alive') and self.player.alive:
            self.player.update_daily()

        for member in self.family_members:
            if hasattr(member, 'alive') and member.alive:
                member.update_daily()

        # 随机事件
        if self.player and hasattr(self.player, 'alive') and self.player.alive and random.random() < 0.3:  # 30%概率触发随机事件
            event = generate_random_event(self, self.player)
            self.add_event(event)

        # 季节性事件 (春节、生日等)
        day_of_year = self.current_day % 365

        # 更新季节
        if 1 <= day_of_year <= 90:
            if self.current_season != "春季":
                self.current_season = "春季"
                self.add_event("春季来临，万物复苏。")
        elif 91 <= day_of_year <= 180:
            if self.current_season != "夏季":
                self.current_season = "夏季"
                self.add_event("夏季到来，天气炎热。")
        elif 181 <= day_of_year <= 270:
            if self.current_season != "秋季":
                self.current_season = "秋季"
                self.add_event("秋季到来，天高气爽。")
        else:
            if self.current_season != "冬季":
                self.current_season = "冬季"
                self.add_event("冬季来临，寒意渐浓。")

        # 经济状况变化 (每90天可能变化)
        if day_of_year % 90 == 0 and random.random() < 0.3:  # 30%概率经济状况变化
            old_status = self.economy_status
            status_options = ["繁荣", "正常", "衰退"]
            weights = {
                "繁荣": [0.3, 0.6, 0.1],  # 繁荣后继续繁荣30%，变为正常60%，变为衰退10%
                "正常": [0.3, 0.4, 0.3],  # 正常后变为繁荣30%，继续正常40%，变为衰退30%
                "衰退": [0.1, 0.6, 0.3]  # 衰退后变为繁荣10%，变为正常60%，继续衰退30%
            }

            self.economy_status = random.choices(
                status_options,
                weights=weights.get(old_status, [0.3, 0.4, 0.3])
            )[0]

            if self.economy_status != old_status:
                if self.economy_status == "繁荣":
                    self.add_event("经济形势好转，进入繁荣期！各行业迎来发展机遇。")
                elif self.economy_status == "衰退":
                    self.add_event("经济形势恶化，进入衰退期。就业和投资都变得更加困难。")
                else:
                    self.add_event("经济形势趋于平稳，进入正常发展期。")

        # 春节 (假设是第一天)
        if day_of_year == 1:
            bonus = random.randint(1000, 5000)
            self.player.assets += bonus
            self.add_event(f"春节到了！{self.player.name}收到了{bonus}元红包。")

        # 生日
        if hasattr(self.player, 'birthday') and self.player.birthday == day_of_year:
            self.player.age += 1
            self.player.happiness += random.randint(10, 20)
            self.add_event(f"今天是{self.player.name}的{self.player.age}岁生日!")

        # 更新家族财富和声望
        self.update_family_fortune_and_prestige()

        # 更新天数
        self.current_day += 1

    def update_family_fortune_and_prestige(self):
        """更新家族财富和声望"""
        # 计算总资产
        total_assets = 0
        if self.player:
            total_assets += getattr(self.player, 'assets', 0)

        for member in self.family_members:
            if hasattr(member, 'alive') and member.alive:
                total_assets += getattr(member, 'assets', 0)

        # 更新家族财富
        self.family_fortune = total_assets

        # 检查成就
        if self.family_fortune >= 1000000:
            self.update_achievement("富翁")
        if self.family_prestige >= 100:
            self.update_achievement("名门望族")

    def add_event(self, event_text):
        """添加事件到历史记录"""

        from family_simulation.game.events import add_event
        add_event(self, event_text)

    def to_dict(self):
        """将游戏状态转换为字典，用于JSON序列化"""
        result = {
            "current_day": self.current_day,
            "family_fortune": self.family_fortune,
            "family_prestige": self.family_prestige,
            "current_season": self.current_season,
            "economy_status": self.economy_status,
            "is_mobile_ui": self.is_mobile_ui,
            "game_speed": self.game_speed,
            "auto_skip": self.auto_skip,
            "family_traits": self.family_traits,
            "achievements": self.achievements,
            "events": self.events_history[-20:] if self.events_history else []  # 只返回最近20条事件
        }

        # 添加玩家信息
        if self.player:
            result["player"] = self.player.to_dict()

        # 添加家族成员信息
        result["family_members"] = [
            member.to_dict() for member in self.family_members
            if hasattr(member, 'to_dict')
        ]

        return result


# 为向后兼容导入random模块
import random