from nonebot import get_driver, on_command, require, on_message
require("nonebot_plugin_localstore")
require("nonebot_plugin_value")
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot.rule import Rule

from nonebot.plugin import PluginMetadata

from .config import Config
from .handles import yinpa_Handles, _join_pending_rule
from nonebot_plugin_value.api.api_currency import get_or_create_currency
from nonebot_plugin_value.pyd_models.currency_pyd import CurrencyData


@get_driver().on_startup
async def register_yinpa_currency():
    await get_or_create_currency(CurrencyData(id="YPD", display_name="YPD", symbol="YPD"))

__plugin_meta__ = PluginMetadata(
    name="Chikari_Yinpa_Fix",
    description="一个普通的银趴插件（修复版）",
    usage="",
    config=Config,
    type="application",
    homepage="https://github.com/joeyep114514/nonebot_plugin_chikari_yinpa_Fix",
    supported_adapters={"~onebot.v11"}
)

__version__ = "1.4.13"

on_yinpa_control = on_command(
    "yinpa_control",
    aliases={"银趴控制"},
    permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
    priority=10,
    block=False,
    handlers=[yinpa_Handles.module_enable]
)

on_sign_in = on_command(
    "sign_in",
    aliases={"签到","打卡"},
    priority=10,
    block=False,
    handlers=[yinpa_Handles.sign_in]
)

on_info = on_command(
    "info",
    aliases={"信息","查询"},
    priority=10,
    block=False,
    handlers=[yinpa_Handles.yinpa_info]
)

on_yinpa_help = on_command(
    "yinpa_help",
    aliases={"银趴帮助"},
    priority=10,
    block=False,
    handlers=[yinpa_Handles.yinpa_help]
)

on_yinpa_join = on_command(
    "yinpa_join",
    aliases={"加入银趴"},
    priority=10,
    block=False,
    handlers=[yinpa_Handles.yinpa_join]
)

# 接管创建流程中的普通消息（选择种族 / 分配属性点）
# 优先级置于命令之后（数值更大），确保诸如 /yinpa_join 重启等命令优先处理
on_yinpa_join_step = on_message(
    rule=Rule(_join_pending_rule),
    priority=1000,
    block=True,
    handlers=[yinpa_Handles.yinpa_join_step]
)

on_yinpa_leave = on_command(
    "yinpa_leave",
    aliases={"离开银趴"},
    priority=10,
    block=False,
    handlers=[yinpa_Handles.yinpa_leave]
)

on_yinpa_attack_tou = on_command(
    "tou",
    aliases={"透","插入"},
    priority=10,
    block=False,
    handlers=[yinpa_Handles.yinpa_tou]
)

on_yinpa_attack_zha = on_command(
    "zha",
    aliases={"榨","榨精"},
    priority=10,
    block=False,
    handlers=[yinpa_Handles.yinpa_zha]
)

on_yinpa_attack_chong = on_command(
    "chong",
    aliases={"冲","打胶","手冲","撸","导"},
    priority=10,
    block=False,
    handlers=[yinpa_Handles.yinpa_chong]
)

on_yinpa_attack_kou = on_command(
    "kou",
    aliases={"扣","扣扣","自慰","紫薇"},
    priority=10,
    block=False,
    handlers=[yinpa_Handles.yinpa_kou]
)

on_yinpa_shop = on_command(
    "shop",
    aliases={"商店","买","买东西","店"},
    priority=10,
    block=False,
    handlers=[yinpa_Handles.yinpa_shop]
)

on_yinpa_work = on_command(
    "work",
    aliases={"工作","打工"},
    priority=10,
    block=False,
    handlers=[yinpa_Handles.yinpa_work]
)

on_yinpa_transfer = on_command(
    "transfer",
    aliases={"转账"},
    priority=10,
    block=False,
    handlers=[yinpa_Handles.yinpa_transfer]
)

# on_test = on_command(
#     "test",
#     permission=SUPERUSER | GROUP_ADMIN | GROUP_OWNER,
#     priority=10,
#     block=False,
#     handlers=[yinpa_Handles.test]
# )