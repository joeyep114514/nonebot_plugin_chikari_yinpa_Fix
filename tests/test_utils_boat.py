import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


class _StoreStub(types.ModuleType):
    @staticmethod
    def get_data_file(name, filename):
        return Path(__file__).resolve().parent / filename

    @staticmethod
    def get_config_file(name, filename):
        return Path(__file__).resolve().parent / filename


sys.modules.setdefault("nonebot_plugin_localstore", _StoreStub("nonebot_plugin_localstore"))

nonebot_module = types.ModuleType("nonebot")
nonebot_module.on_command = lambda *args, **kwargs: None
nonebot_module.get_plugin_config = lambda *args, **kwargs: None
nonebot_module.get_bots = lambda: {}
sys.modules["nonebot"] = nonebot_module

adapters_module = types.ModuleType("nonebot.adapters")
onebot_module = types.ModuleType("nonebot.adapters.onebot")
onebot_v11_module = types.ModuleType("nonebot.adapters.onebot.v11")

class GroupMessageEvent:  # pragma: no cover - stub for import
    pass

class Message:  # pragma: no cover - stub for import
    def extract_plain_text(self):
        return ""

class MessageSegment:  # pragma: no cover - stub for import
    pass

onebot_v11_module.GroupMessageEvent = GroupMessageEvent
onebot_v11_module.Message = Message
onebot_v11_module.MessageSegment = MessageSegment
sys.modules["nonebot.adapters"] = adapters_module
sys.modules["nonebot.adapters.onebot"] = onebot_module
sys.modules["nonebot.adapters.onebot.v11"] = onebot_v11_module

plugin_module = types.ModuleType("nonebot.plugin")
class PluginMetadata:  # pragma: no cover - stub for import
    def __init__(self, *args, **kwargs):
        pass
plugin_module.PluginMetadata = PluginMetadata
sys.modules["nonebot.plugin"] = plugin_module

class _PermissionStub(int):
    def __or__(self, other):
        return self

permission_module = types.ModuleType("nonebot.permission")
permission_module.SUPERUSER = _PermissionStub(1)
sys.modules["nonebot.permission"] = permission_module

permission_v11_module = types.ModuleType("nonebot.adapters.onebot.v11.permission")
permission_v11_module.GROUP_ADMIN = _PermissionStub(2)
permission_v11_module.GROUP_OWNER = _PermissionStub(4)
sys.modules["nonebot.adapters.onebot.v11.permission"] = permission_v11_module

matcher_module = types.ModuleType("nonebot.matcher")
class Matcher:  # pragma: no cover - stub for import
    pass
matcher_module.Matcher = Matcher
sys.modules["nonebot.matcher"] = matcher_module

params_module = types.ModuleType("nonebot.params")
class CommandArg:  # pragma: no cover - stub for import
    def __init__(self, *args, **kwargs):
        pass
params_module.CommandArg = CommandArg
sys.modules["nonebot.params"] = params_module

from math import sqrt

from nonebot_plugin_chikari_yinpa.data_handles import data
from nonebot_plugin_chikari_yinpa.utils import Utils


class BoatTests(unittest.TestCase):
    def test_boat_is_active_without_cooldown(self):
        with patch.object(Utils, "get_skill", return_value=[6, None, 3]):
            self.assertEqual(Utils.boat("123"), [6, None, 3])

    def test_boat_is_inactive_while_cooling_down(self):
        with patch.object(Utils, "get_skill", return_value=[6, 9999999999, 3]):
            self.assertEqual(Utils.boat("123"), [])

    def test_boat_is_inactive_without_skill(self):
        with patch.object(Utils, "get_skill", return_value=[]):
            self.assertEqual(Utils.boat("123"), [])


class GetValueBoatBonusTests(unittest.TestCase):
    def setUp(self):
        data.clear()
        data["333"] = {
            'name': '舰娘',
            'strength': 10,
            'constitution': 10,
            'technique': 10,
            'volition': 10,
            'intelligence': 20,
            'charm': 10,
            'hp_v': 100,
            'hp_c': 100,
            'state': [],
            'skill': [[6, None, 3]],
        }

    def test_get_value_constitution_applies_boat_bonus(self):
        value = Utils.get_value("333", 'constitution')
        expected = 10 + 20 * sqrt(3)
        self.assertAlmostEqual(value[0], expected)

    def test_get_value_strength_applies_boat_bonus(self):
        value = Utils.get_value("333", 'strength')
        expected = 10 + 20 * sqrt(3)
        self.assertAlmostEqual(value[0], expected)

    def test_get_value_volition_applies_boat_bonus(self):
        value = Utils.get_value("333", 'volition')
        expected = 10 + 20 * sqrt(3)
        self.assertAlmostEqual(value[0], expected)

    def test_get_value_no_boat_bonus_while_cooling_down(self):
        data["333"]["skill"] = [[6, 9999999999, 3]]
        value = Utils.get_value("333", 'constitution')
        self.assertAlmostEqual(value[0], 10)


if __name__ == "__main__":
    unittest.main()
