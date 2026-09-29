"""宠物技能书与学习系统"""
import random
from dataclasses import dataclass, field

PET_TYPE_PHYSICAL = "physical"
PET_TYPE_MAGICAL = "magical"
PET_TYPE_SUPPORT = "support"

DEFAULT_SLOT_LIMIT = 4
DEFAULT_LEARN_RATE = 0.8

@dataclass
class Pet:
    pid: str
    name: str
    level: int = 1
    pet_type: str = PET_TYPE_PHYSICAL
    skills: list = field(default_factory=list)
    skill_slots: int = DEFAULT_SLOT_LIMIT  # 技能槽位上限，可扩展
    fragments: int = 0  # 遗忘返还的技能书碎片
    exp: int = 0  # 遗忘返还的经验

class SkillBookSystem:
    def __init__(self, seed=42):
        self.rng = random.Random(seed)
        self.pets: dict[str, Pet] = {}
        self.skill_types: dict[str, str] = {}  # skill -> physical/magical/support
        self.pet_type: dict[str, str] = {}  # pid -> physical/magical/support
        self.skill_level_reqs: dict[str, int] = {}  # skill -> 所需宠物等级
        self.learn_rate = DEFAULT_LEARN_RATE

    def register_pet(self, pet: Pet) -> None:
        self.pets[pet.pid] = pet
        self.pet_type[pet.pid] = pet.pet_type

    def learn_skill(self, pid: str, skill: str) -> tuple[bool, str]:
        pet = self.pets[pid]

        if not self.can_learn_again(pid, skill):
            return False, "already_learned"

        skill_type = self.skill_types.get(skill)
        if skill_type is not None and not self.can_learn_type(pid, skill_type):
            return False, "type_mismatch"

        required_level = self.skill_level_reqs.get(skill)
        if required_level is not None and not self.meets_level_req(pid, required_level):
            return False, "level_too_low"

        if self.rng.random() >= self.learn_rate:
            return False, "learn_failed"

        overwritten = None
        if len(pet.skills) >= self.get_slot_limit(pid):
            overwritten = self.rng.choice(pet.skills)
            pet.skills.remove(overwritten)
        pet.skills.append(skill)

        if overwritten is not None:
            return True, f"overwrite:{overwritten}"
        return True, "learned"

    def get_slot_limit(self, pid: str) -> int:
        pet = self.pets.get(pid)
        return pet.skill_slots if pet is not None else DEFAULT_SLOT_LIMIT

    def expand_slots(self, pid: str, count: int = 1) -> int:
        pet = self.pets[pid]
        pet.skill_slots += count
        return pet.skill_slots

    def can_learn_type(self, pid: str, skill_type: str) -> bool:
        pet_kind = self.pet_type.get(pid)
        if pet_kind is None:
            pet = self.pets.get(pid)
            pet_kind = pet.pet_type if pet is not None else None
        return pet_kind == skill_type

    def get_upgrade_rate(self, level: int) -> float:
        level = max(level, 1)
        return max(0.05, 0.8 - 0.1 * (level - 1))

    def forget_skill(self, pid: str, skill: str) -> dict:
        pet = self.pets[pid]
        if skill not in pet.skills:
            return {}
        pet.skills.remove(skill)
        fragments = 10
        exp = 20
        pet.fragments += fragments
        pet.exp += exp
        return {"skill": skill, "fragments": fragments, "exp": exp}

    def can_learn_again(self, pid: str, skill: str) -> bool:
        return skill not in self.pets[pid].skills

    def meets_level_req(self, pid: str, skill_level: int) -> bool:
        return self.pets[pid].level >= skill_level
