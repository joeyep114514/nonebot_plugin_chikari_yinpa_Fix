import json
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


class GroupMessageEvent:
    pass


class Message:
    def extract_plain_text(self):
        return ""


class MessageSegment:
    pass


onebot_v11_module.GroupMessageEvent = GroupMessageEvent
onebot_v11_module.Message = Message
onebot_v11_module.MessageSegment = MessageSegment
sys.modules["nonebot.adapters"] = adapters_module
sys.modules["nonebot.adapters.onebot"] = onebot_module
sys.modules["nonebot.adapters.onebot.v11"] = onebot_v11_module

plugin_module = types.ModuleType("nonebot.plugin")


class PluginMetadata:
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


class Matcher:
    pass


matcher_module.Matcher = Matcher
sys.modules["nonebot.matcher"] = matcher_module

params_module = types.ModuleType("nonebot.params")


class CommandArg:
    def __init__(self, *args, **kwargs):
        pass


params_module.CommandArg = CommandArg
sys.modules["nonebot.params"] = params_module

from nonebot_plugin_chikari_yinpa.data_handles import configdata, data
from nonebot_plugin_chikari_yinpa.handles import yinpa_Handles


class _Finished(Exception):
    pass


class FakeMatcher:
    def __init__(self):
        self.finished = None
        self.sent = None

    async def send(self, msg):
        self.sent = msg

    async def finish(self, msg):
        self.finished = msg
        raise _Finished()


class FakeMessage:
    def __init__(self, text):
        self._text = text

    def extract_plain_text(self):
        return self._text


class FakeEvent:
    def __init__(self, group_id, user_id, messages, to_me=False):
        self.group_id = group_id
        self._user_id = str(user_id)
        self.self_id = "10000"
        self.to_me = to_me
        self._messages = messages

    def get_user_id(self):
        return self._user_id

    def json(self):
        return json.dumps({"message": self._messages})


def at_msg(qq):
    return {"type": "at", "data": {"qq": str(qq)}}


def text_msg(text):
    return {"type": "text", "data": {"text": text}}


class TransferTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        configdata["yinpa_enabled_group"] = [123456]
        data.clear()
        data["111"] = {"name": "阿明", "money": 1000}
        data["222"] = {"name": "小红", "money": 100}

    async def test_transfer_success(self):
        matcher = FakeMatcher()
        event = FakeEvent(123456, 111, [text_msg("100 "), at_msg(222)])
        args = FakeMessage("100")
        with self.assertRaises(_Finished):
            await yinpa_Handles.yinpa_transfer(matcher, event, args)
        self.assertEqual(data["111"]["money"], 900)
        self.assertEqual(data["222"]["money"], 200)
        self.assertIn("转账100给小红成功", matcher.finished)
        self.assertIn("现在你的余额是900", matcher.finished)

    async def test_transfer_insufficient_funds(self):
        matcher = FakeMatcher()
        event = FakeEvent(123456, 111, [text_msg("2000 "), at_msg(222)])
        args = FakeMessage("2000")
        with self.assertRaises(_Finished):
            await yinpa_Handles.yinpa_transfer(matcher, event, args)
        self.assertEqual(data["111"]["money"], 1000)
        self.assertEqual(data["222"]["money"], 100)
        self.assertIn("错误", matcher.finished)

    async def test_transfer_invalid_amount(self):
        matcher = FakeMatcher()
        event = FakeEvent(123456, 111, [text_msg("abc "), at_msg(222)])
        args = FakeMessage("abc")
        with self.assertRaises(_Finished):
            await yinpa_Handles.yinpa_transfer(matcher, event, args)
        self.assertEqual(data["111"]["money"], 1000)
        self.assertIn("金额必须为正整数", matcher.finished)

    async def test_transfer_missing_target(self):
        matcher = FakeMatcher()
        event = FakeEvent(123456, 111, [text_msg("100")])
        args = FakeMessage("100")
        with self.assertRaises(_Finished):
            await yinpa_Handles.yinpa_transfer(matcher, event, args)
        self.assertEqual(data["111"]["money"], 1000)
        self.assertIn("未找到目标", matcher.finished)

    async def test_transfer_to_self(self):
        matcher = FakeMatcher()
        event = FakeEvent(123456, 111, [text_msg("100 "), at_msg(111)])
        args = FakeMessage("100")
        with self.assertRaises(_Finished):
            await yinpa_Handles.yinpa_transfer(matcher, event, args)
        self.assertEqual(data["111"]["money"], 1000)
        self.assertIn("不能给自己转账", matcher.finished)

    async def test_transfer_by_nickname(self):
        matcher = FakeMatcher()
        event = FakeEvent(123456, 111, [text_msg("50 小红")])
        args = FakeMessage("50 小红")
        with self.assertRaises(_Finished):
            await yinpa_Handles.yinpa_transfer(matcher, event, args)
        self.assertEqual(data["111"]["money"], 950)
        self.assertEqual(data["222"]["money"], 150)
        self.assertIn("转账50给小红成功", matcher.finished)


if __name__ == "__main__":
    unittest.main()
