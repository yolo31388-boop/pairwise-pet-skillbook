"""宠物技能书与学习系统 - 含7个bug"""
import random
from dataclasses import dataclass, field

@dataclass
class Pet:
    pid: str
    name: str
    level: int = 1
    skills: list = field(default_factory=list)
    skill_slots: int = 4  # bug2: 无上限

class SkillBookSystem:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.pets: dict[str, Pet] = {}
        self.skill_types: dict[str, str] = {}  # skill -> physical/magical/support

    def learn_skill(self, pid: str, skill: str) -> tuple[bool, str]:
        # bug1: 100%成功不顶技能
        self.pets[pid].skills.append(skill)
        return True, "learned"

    def get_slot_limit(self, pid: str) -> int:
        # bug2: 无上限
        return 999

    def can_learn_type(self, pid: str, skill_type: str) -> bool:
        # bug3: 无类型限制
        return True

    def get_upgrade_rate(self, level: int) -> float:
        # bug4: 固定概率
        return 0.5

    def forget_skill(self, pid: str, skill: str) -> dict:
        # bug5: 不返还
        return {}

    def can_learn_again(self, pid: str, skill: str) -> bool:
        # bug6: 可重复学习叠加
        return True

    def meets_level_req(self, pid: str, skill_level: int) -> bool:
        # bug7: 无等级要求
        return True
