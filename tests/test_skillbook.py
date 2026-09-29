"""宠物技能书与学习系统 - 红态测试"""
import pytest, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pet.skillbook import SkillBookSystem, Pet

class TestLearnFailure:
    def test_learning_can_fail_and_overwrite(self):
        sbs = SkillBookSystem(seed=1)
        sbs.pets["p1"] = Pet("p1", "pet", skills=["s1", "s2", "s3", "s4"])
        ok, msg = sbs.learn_skill("p1", "new_skill")
        # 槽位满时应该有概率顶掉旧技能
        assert "overwrite" in msg or ok == False

class TestSlotLimit:
    def test_skill_slot_has_limit(self):
        sbs = SkillBookSystem()
        assert sbs.get_slot_limit("p1") <= 8

class TestSkillTypeRestriction:
    def test_physical_pet_cannot_learn_magic(self):
        sbs = SkillBookSystem()
        sbs.pets["p1"] = Pet("p1", "warrior")
        sbs.skill_types["fireball"] = "magical"
        # 应该有宠物类型属性
        assert hasattr(sbs, "pet_type")
        sbs.pet_type = {"p1": "physical"}
        assert sbs.can_learn_type("p1", "magical") == False

class TestUpgradeRate:
    def test_higher_skill_level_lower_upgrade_rate(self):
        sbs = SkillBookSystem()
        r1 = sbs.get_upgrade_rate(1)
        r5 = sbs.get_upgrade_rate(5)
        assert r5 < r1

class TestForgetRefund:
    def test_forgetting_returns_fragments(self):
        sbs = SkillBookSystem()
        sbs.pets["p1"] = Pet("p1", "pet", skills=["s1"])
        refund = sbs.forget_skill("p1", "s1")
        assert refund != {}

class TestNoDuplicateSkill:
    def test_cannot_learn_same_skill_twice(self):
        sbs = SkillBookSystem()
        sbs.pets["p1"] = Pet("p1", "pet", skills=["s1"])
        assert sbs.can_learn_again("p1", "s1") == False

class TestLevelRequirement:
    def test_low_level_pet_cannot_learn_high_skill(self):
        sbs = SkillBookSystem()
        sbs.pets["p1"] = Pet("p1", "pet", level=1)
        assert sbs.meets_level_req("p1", 50) == False
        sbs.pets["p1"].level = 60
        assert sbs.meets_level_req("p1", 50) == True
