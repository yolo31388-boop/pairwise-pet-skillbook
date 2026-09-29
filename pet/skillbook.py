"""宠物技能书与学习系统"""
import random
from dataclasses import dataclass, field

@dataclass
class Pet:
    pid: str
    name: str
    level: int = 1
    skills: list = field(default_factory=list)
    skill_slots: int = 4  # 技能槽上限，默认4，可通过道具扩展

class SkillBookSystem:
    DEFAULT_SKILL_SLOTS = 4
    BASE_LEARN_RATE = 0.8       # 技能书学习基础成功率
    BASE_UPGRADE_RATE = 0.8     # 技能升级基础成功率（当前等级1时）
    UPGRADE_RATE_DECAY = 0.1    # 每升一级成功率下降
    MIN_UPGRADE_RATE = 0.1      # 高级升级成功率下限
    REFUND_FRAGMENTS_PER_LEVEL = 5  # 遗忘时每级技能返还的技能书碎片（部分返还）

    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.pets: dict[str, Pet] = {}
        self.skill_types: dict[str, str] = {}  # skill -> physical/magical/support
        self.pet_type: dict[str, str] = {}     # pid -> physical/magical/support
        self.skill_levels: dict[str, dict[str, int]] = {}  # pid -> {skill: level}

    def learn_skill(self, pid: str, skill: str,
                    skill_level: int | None = None) -> tuple[bool, str]:
        pet = self.pets[pid]
        # 同一技能只能学一次，重复学习不叠加
        if not self.can_learn_again(pid, skill):
            return False, "already_learned"
        # 类型限制：物理/法术/辅助宠物只能学对应类型技能
        skill_type = self.skill_types.get(skill)
        if skill_type is not None and not self.can_learn_type(pid, skill_type):
            return False, "type_mismatch"
        # 等级要求：低级宠物不能学高级技能
        if skill_level is not None and not self.meets_level_req(pid, skill_level):
            return False, "level_too_low"
        # 学习有成功率，失败则技能书不生效
        if self.rng.random() >= self.BASE_LEARN_RATE:
            return False, "learn_failed"
        # 槽位已满：顶掉一个随机已有技能
        if len(pet.skills) >= self.get_slot_limit(pid):
            old_index = self.rng.randrange(len(pet.skills))
            old_skill = pet.skills.pop(old_index)
            pet.skills.append(skill)
            self.skill_levels.setdefault(pid, {}).pop(old_skill, None)
            self.skill_levels.setdefault(pid, {})[skill] = 1
            return True, f"overwrite:{old_skill}"
        pet.skills.append(skill)
        self.skill_levels.setdefault(pid, {})[skill] = 1
        return True, "learned"

    def get_slot_limit(self, pid: str) -> int:
        pet = self.pets.get(pid)
        if pet is not None:
            return pet.skill_slots
        return self.DEFAULT_SKILL_SLOTS

    def expand_skill_slots(self, pid: str, extra: int = 1) -> int:
        """扩展指定宠物的技能槽上限。"""
        pet = self.pets[pid]
        pet.skill_slots += extra
        return pet.skill_slots

    def can_learn_type(self, pid: str, skill_type: str) -> bool:
        pet_type = self.pet_type.get(pid)
        if pet_type is None:
            return True  # 未配置宠物类型时不作限制
        return pet_type == skill_type

    def get_upgrade_rate(self, level: int) -> float:
        # 技能升级概率随等级递减，高级升级更难
        rate = self.BASE_UPGRADE_RATE - (level - 1) * self.UPGRADE_RATE_DECAY
        return max(self.MIN_UPGRADE_RATE, rate)

    def upgrade_skill(self, pid: str, skill: str) -> tuple[bool, str]:
        pet = self.pets[pid]
        if skill not in pet.skills:
            return False, "not_learned"
        levels = self.skill_levels.setdefault(pid, {})
        current = levels.get(skill, 1)
        if self.rng.random() >= self.get_upgrade_rate(current):
            return False, "upgrade_failed"
        levels[skill] = current + 1
        return True, f"upgraded:{levels[skill]}"

    def forget_skill(self, pid: str, skill: str) -> dict:
        pet = self.pets[pid]
        if skill not in pet.skills:
            return {}
        pet.skills.remove(skill)
        level = self.skill_levels.get(pid, {}).pop(skill, 1)
        # 遗忘返还部分技能书碎片（按技能等级折算）
        return {"fragments": self.REFUND_FRAGMENTS_PER_LEVEL * level}

    def can_learn_again(self, pid: str, skill: str) -> bool:
        return skill not in self.pets[pid].skills

    def meets_level_req(self, pid: str, skill_level: int) -> bool:
        return self.pets[pid].level >= skill_level
