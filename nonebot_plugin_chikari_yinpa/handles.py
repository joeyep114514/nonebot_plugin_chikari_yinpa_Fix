from nonebot.adapters.onebot.v11 import GroupMessageEvent,Message,MessageSegment
from nonebot.matcher import Matcher
from nonebot.params import CommandArg
from nonebot import get_bots
from time import time
from hashlib import md5
from math import sqrt, exp
import random

from .data_handles import data,configdata,DHandles
from .config import plugin_config
from .utils import Utils


from .dicts import dicts

# 昵称最大长度（字符数）
# 用于防止超长昵称在 get_user_info_image -> text_to_image 中触发超大图像分配（内存/CPU 耗尽）
MAX_NAME_LENGTH = 32

# 加入银趴创建流程的临时状态缓存（内存态，重启即失效）
# 结构：pending_join[uid] = {"step":"species"|"points", "species":int, "name":str, "ts":time()}
pending_join = {}

class yinpa_Handles():
    """消息处理
    """
    
    async def module_enable(
            matcher: Matcher,event: GroupMessageEvent,args: Message = CommandArg()
    ):
        """处理银趴的开关
        """
        
        command: str = args.extract_plain_text()
        if "enable" in command and not Utils.group_enable_check(event.group_id):
            DHandles.configdata_set("yinpa_enabled_group",configdata["yinpa_enabled_group"] + [event.group_id])
            await matcher.finish("本群银趴已开启")
        elif "disable" in command and Utils.group_enable_check(event.group_id):
            DHandles.group_remove(event.group_id)
            await matcher.finish("本群银趴已禁用")
        else:
            await matcher.finish("错误：参数错误！\n命令：/yinpa_control <enable/disable>")

    async def sign_in(
            matcher: Matcher,event: GroupMessageEvent
    ):
        """处理签到
        """
        
        if not Utils.group_enable_check(event.group_id):
            await matcher.finish("本群银趴已禁用")
        if not Utils.yinpa_user_presence_check(event.get_user_id()):
            await matcher.finish("您还未加入银趴！\ntips：请使用 /yinpa_join 或 /加入银趴 加入银趴")
        uid: str = event.get_user_id()
        if data[uid]["last_sign_in_time"] < (int)(time() / 86400):
            DHandles.data_set(uid,"last_sign_in_time",(int)(time() / 86400))
            DHandles.data_set(uid,'sign_in_count',data[uid].get('sign_in_count',0) + 1)
            d_pl = Utils.dice(100,(int)(data[uid]['penis_length']) ^ 1)
            d_vd = Utils.dice(100,(int)(data[uid]['vagina_depth']) ^ 2)
            old_money = await Utils.get_money(uid)
            d_m = Utils.dice(100,(int)(old_money) ^ 3)
            new_money = await Utils.add_money(uid, d_m)
            await matcher.send(f"{data[uid]['name']}签到成功\n长度增加：{data[uid]['penis_length']} + (1d100 / 100) = {data[uid]['penis_length']} + ({d_pl} / 100) = {round(data[uid]['penis_length'] + d_pl / 100,2)}\n深度增加：{data[uid]['vagina_depth']} + (1d100 / 100) = {data[uid]['vagina_depth']} + ({d_vd} / 100) = {round(data[uid]['vagina_depth'] + d_vd / 100,2)}\nYPD增加：{old_money} + 1d100 = {old_money} + {d_m} = {new_money}\nps：签到于早上8点刷新")
            DHandles.data_set(uid,'penis_length',round(data[uid]['penis_length'] + d_pl / 100,2))
            DHandles.data_set(uid,'vagina_depth',round(data[uid]['vagina_depth'] + d_vd / 100,2))
            await matcher.finish()
        else:
            await matcher.finish("你今天已经打过卡了呢~\nps：签到于早上8点刷新，别问我为什么")

    async def yinpa_join(
            matcher: Matcher,event: GroupMessageEvent,args: Message = CommandArg()
    ):
        """处理加入银趴（第一步：昵称 → 选择种族）"""
        
        if not Utils.group_enable_check(event.group_id):
            await matcher.finish("本群银趴已禁用，你不准参加银趴！")
        if Utils.yinpa_user_presence_check(event.get_user_id()):
            await matcher.finish("您已加入银趴！\n如果想要重置银趴数据，请使用 /leave_yinpa 或 /离开银趴 离开银趴后再加入")
        uid: str = event.get_user_id()
        command: str = args.extract_plain_text()
        arg_list: list = command.split()
        if len(arg_list) >= 1:
            name: str = arg_list[0]
        else:
            bot = get_bots()[(str)(event.self_id)]
            name: str = (await bot.call_api("get_group_member_info",group_id = event.group_id,user_id = uid))["nickname"]
        if len(name) > MAX_NAME_LENGTH:
            await matcher.finish(f"昵称过长！\n昵称请控制在 {MAX_NAME_LENGTH} 个字符以内")
        if Utils.find_user_name(name):
            await matcher.finish("已经有人使用这个昵称了！")
        # 中途重新加入：重置旧状态重来
        pending_join[uid] = {"step":"species","species":None,"name":name,"ts":time()}
        await matcher.finish(MessageSegment.image(Utils.text_to_image(await yinpa_Handles._species_select_text())))

    @staticmethod
    def is_join_pending(uid: str):
        """判断用户是否处于创建流程中（含超时清理）

        Args:
            uid (str): 用户id

        Returns:
            bool: 是否处于创建流程
        """
        
        pj = pending_join.get(uid)
        if not pj:
            return False
        plugin_config = _get_plugin_config()
        if time() - pj["ts"] > plugin_config.chikari_yinpa_join_timeout:
            pending_join.pop(uid, None)
            return False
        return True

    @staticmethod
    def _get_pending(uid: str):
        """读取有效的创建状态（含超时清理）

        Args:
            uid (str): 用户id

        Returns:
            dict: 创建状态，无效时返回 None
        """
        
        pj = pending_join.get(uid)
        if not pj:
            return None
        plugin_config = _get_plugin_config()
        if time() - pj["ts"] > plugin_config.chikari_yinpa_join_timeout:
            pending_join.pop(uid, None)
            return None
        return pj

    @staticmethod
    async def _species_select_text():
        """选择种族的提示文案
        """
        
        return "请选择加入的种族【回复对应序号】\n0随机 1人类 2猫娘 3精灵 4天使 5魅魔 6舰娘 7吸血鬼"

    @staticmethod
    async def _points_input_text(species: int):
        """分配自由属性点的提示文案（按所选种族动态填充）

        Args:
            species (int): 种族id
        """
        
        spec = dicts.species_initial_ability[species]
        base = spec["base"]
        cap = spec["cap"]
        free = spec["free_pts"]
        spname = dicts.species_dict[species]
        return (f"您选择了【{spname}】。\n\n"
                "各属性作用一览：\n"
                "力量  —— 主要提升打工(搬砖/打架)收益，并参与伤害计算\n"
                "体质  —— 提供体质HP(体质+10)×10，决定承伤上限与昏迷抗性\n"
                "技巧  —— 本对战伤害的主要来源，决定出手力度\n"
                "意志  —— 提供意志HP(意志+10)×5，平时受击先扣这个，决定生存能力\n"
                "智力  —— 影响自然之心/舰装等技能强度，与直播/写文收益相关\n"
                "魅力  —— 影响直播/援交收益，并可压制对手\n\n"
                "属性上限(所有种族一致)：\n"
                f"力量{cap[0]} 体质{cap[1]} 技巧{cap[2]} 意志{cap[3]} 智力{cap[4]} 魅力{cap[5]}\n\n"
                "种族基础属性：您当前各项起始值为\n"
                f"力量{base[0]}  体质{base[1]}  技巧{base[2]}\n"
                f"意志{base[3]}  智力{base[4]}  魅力{base[5]}\n"
                "(基础属性由种族决定，加点是在此之上继续累加，最终属性 = 基础属性 + 加点增量，不能超过上限)\n\n"
                f"您获得自由属性点 {free}。\n"
                "分配逻辑：1自由属性点可兑换\n"
                "    +1  力量/技巧/智力/魅力 ；\n"
                "    +1  体质/意志 需要 2 自由点（体质/意志请填偶数）。\n"
                "注意：点数只够专精几项，无法六项全满，请想清楚取舍方向。\n"
                "请按格式 \"**/**/**/**/**/**\" 回复已进行对应属性点分配\n"
                "（顺序：力量/体质/技巧/意志/智力/魅力）。\n"
                "** 为分配给该属性的自由属性点数（不是最终属性值，也不是增量），\n"
                "体质/意志必须为偶数；例：85/0/85/0/0/0 = 共分配170点。\n"
                "若回复\"随机\"，将在自由点内自动随机分配。")

    @staticmethod
    async def _join_pick_species(matcher: Matcher, uid: str, pj: dict, text: str):
        """处理创建流程第二步：选择种族

        Args:
            matcher (Matcher): 匹配器
            uid (str): 用户id
            pj (dict): 创建状态
            text (str): 用户回复的文本
        """
        
        if not text.isdigit():
            await matcher.finish("参数错误！\n请回复对应种族序号（0随机 1人类 2猫娘 3精灵 4天使 5魅魔 6舰娘 7吸血鬼）")
        species: int = int(text)
        if species < 0 or species > 7:
            await matcher.finish("参数错误！\n不存在指定的种族\n种族列表参照： /yinpa_help 种族 ")
        if species == 0:
            species = Utils.dice(7,uid)
        pj["species"] = species
        pj["step"] = "points"
        pj["ts"] = time()
        await matcher.finish(MessageSegment.image(Utils.text_to_image(await yinpa_Handles._points_input_text(species))))

    @staticmethod
    def _validate_points(species: int, text: str):
        """校验自由属性点分配格式

        Args:
            species (int): 种族id
            text (str): 用户输入的 "力量/体质/技巧/意志/智力/魅力"

        Returns:
            list|str: 合法的六项点数列表，非法时返回错误提示字符串
        """
        
        spec = dicts.species_initial_ability[species]
        base = spec["base"]
        cap = spec["cap"]
        free = spec["free_pts"]
        rate = dicts.attribute_order["rate"]
        names = dicts.attribute_order["names"]
        try:
            parts = [int(x.strip()) for x in text.strip().split("/")]
        except Exception:
            return "必须输入六个整数"
        if len(parts) != 6:
            return "必须按格式 \"**/**/**/**/**/**\" 输入六项点数（顺序：力量/体质/技巧/意志/智力/魅力）"
        if any(p < 0 for p in parts):
            return "每项点数不能为负数"
        if parts[1] % 2 != 0 or parts[3] % 2 != 0:
            return "体质、意志的点数必须为偶数（2 的倍数）"
        if sum(parts) > free:
            return f"六项点数之和（{sum(parts)}）超过自由属性点上限（{free}）"
        for i in range(6):
            inc = parts[i] if rate[i] == 1 else int(parts[i] * rate[i])
            if base[i] + inc > cap[i]:
                return f"「{names[i]}」分配过多：基础{base[i]} + 增量{inc} 超过属性上限{cap[i]}"
        return parts

    @staticmethod
    def _random_pts(species: int):
        """在自由点内随机分配六项（体质/意志自动取偶数，不超过上限）

        Args:
            species (int): 种族id

        Returns:
            list: 六项自由点列表
        """
        
        spec = dicts.species_initial_ability[species]
        base = spec["base"]
        cap = spec["cap"]
        free = spec["free_pts"]
        rate = dicts.attribute_order["rate"]
        cost = [1,2,1,2,1,1]
        pts = [0] * 6
        remaining = free
        while True:
            cand = []
            for i in range(6):
                step = 1 if cost[i] == 1 else 2
                if cost[i] > remaining:
                    continue
                if base[i] + (pts[i] + step) * rate[i] <= cap[i]:
                    cand.append(i)
            if not cand:
                break
            i = random.choice(cand)
            step = 1 if cost[i] == 1 else 2
            pts[i] += step
            remaining -= cost[i]
        return pts

    @staticmethod
    async def _join_pick_points(matcher: Matcher, uid: str, pj: dict, text: str):
        """处理创建流程第三步：分配自由属性点并创建角色

        Args:
            matcher (Matcher): 匹配器
            uid (str): 用户id
            pj (dict): 创建状态
            text (str): 用户回复的文本
        """
        
        if text == "随机":
            pts = yinpa_Handles._random_pts(pj["species"])
        else:
            result = yinpa_Handles._validate_points(pj["species"], text)
            if isinstance(result, str):
                await matcher.finish(f"分配错误：{result}\n请重新按格式 \"**/**/**/**/**/**\" 回复（体质/意志为偶数），或回复\"随机\"自动分配")
            pts = result
        await yinpa_Handles._create_user(matcher, uid, pj, pts)

    @staticmethod
    async def _create_user(matcher: Matcher, uid: str, pj: dict, pts: list):
        """创建角色、写入初始技能/金钱并发送信息图

        Args:
            matcher (Matcher): 匹配器
            uid (str): 用户id
            pj (dict): 创建状态
            pts (list): 六项自由点
        """
        
        species = pj["species"]
        name = pj["name"]
        plugin_config = _get_plugin_config()
        DHandles.user_add_with_points(uid,name,species,pts)
        DHandles.achievement_set(uid,"A01")
        await Utils.set_money(uid, plugin_config.chikari_yinpa_initial_money)
        skill = []
        for i in dicts.species_initial_ability[species]["skill"]:
            skill.append([i,0,1])
        DHandles.data_set(uid,"skill",skill)
        obj = md5("Chikari`s salt".encode("utf-8"))
        obj.update(f"{uid}".encode("utf-8"))
        DHandles.data_set(uid,"md5",obj.hexdigest())
        pending_join.pop(uid, None)
        await matcher.send("创建角色成功！")
        await matcher.finish(MessageSegment.image(await Utils.get_user_info_image(uid)))

    async def yinpa_join_step(
            matcher: Matcher,event: GroupMessageEvent
    ):
        """处理加入银趴的后续步骤（第二步选择种族 / 第三步分配属性点）"""
        
        uid: str = event.get_user_id()
        pj = yinpa_Handles._get_pending(uid)
        if not pj:
            await matcher.finish("创建流程已超时或未开始，请重新使用 /yinpa_join 或 /加入银趴 开始")
        text: str = event.get_plaintext().strip()
        if pj["step"] == "species":
            await yinpa_Handles._join_pick_species(matcher,uid,pj,text)
        else:
            await yinpa_Handles._join_pick_points(matcher,uid,pj,text)

    async def yinpa_leave(
            matcher: Matcher,event: GroupMessageEvent,args: Message = CommandArg()
    ):
        """处理离开银趴
        """
        
        if not Utils.group_enable_check(event.group_id):
            await matcher.finish("本群银趴已禁用")
        if not Utils.yinpa_user_presence_check(event.get_user_id()):
            await matcher.finish("您还未加入银趴！\n请使用 /join_yinpa 或 /加入银趴 加入银趴")
        uid: str=event.get_user_id()
        command: str = args.extract_plain_text()
        if not command or not data[uid]["md5"] or command != data[uid]["md5"]:
            obj = md5("Chikari`s salt".encode("utf-8"))
            obj.update(f"{uid}".encode("utf-8"))
            DHandles.data_set(uid,"md5",obj.hexdigest())
            await matcher.finish(f"警告：这将清除你的所有银趴数据！\n请输入 /yinpa_leave {obj.hexdigest()} 以完成操作")
        else:
            name = data[uid]['name']
            DHandles.user_remove(uid)
            await matcher.finish(f"离开银趴成功。\n大家会记住你的，{name}")

    async def yinpa_help(
            matcher: Matcher,args: Message = CommandArg()
    ):
        """处理银趴帮助
        """
        
        command = args.extract_plain_text()
        help_key = command.split()
        if not help_key:
            await matcher.finish(MessageSegment.image(Utils.text_to_image(dicts.yinpa_help_dict[""])))
        if dicts.help_aliases.get(help_key[0]):
            help_key[0] = dicts.help_aliases[help_key[0]]
        if help_key[0] == "all":
            await matcher.finish(MessageSegment.image(Utils.text_to_image("可用帮助：\n" + "\n".join(list(dicts.yinpa_help_dict.keys())))))
        elif help_key[0] == 'species':
            if len(help_key) >= 2 and dicts.species_help.get(help_key[1]):
                await matcher.finish(MessageSegment.image(Utils.text_to_image(dicts.species_help[help_key[1]])))
            elif len(help_key) >= 2 and dicts.species_dict.get(int(help_key[1])):
                await matcher.finish(MessageSegment.image(Utils.text_to_image(dicts.species_help[dicts.species_dict[int(help_key[1])]])))
            else:
                str = ""
                for i in list(dicts.species_dict.keys()):
                    str += f"{i}：{dicts.species_dict[i]}\n"
                await matcher.finish("错误：该种族不存在\n可用种族：\n" + str + "\n输入/yinpa_help species [种族名或种族ID] 以查看种族描述")
        elif help_key[0] == "skill":
            if len(help_key) >= 2 and dicts.skill_help.get(help_key[1]):
                await matcher.finish(MessageSegment.image(Utils.text_to_image(dicts.skill_help[help_key[1]])))
            elif len(help_key) >= 2 and dicts.skill_dict.get(int(help_key[1])):
                await matcher.finish(MessageSegment.image(Utils.text_to_image(dicts.skill_help[dicts.skill_dict[int(help_key[1])]])))
            else:
                str = ""
                for i in list(dicts.skill_dict.keys()):
                    str += f"{i}：{dicts.skill_dict[i]}\n"
                await matcher.finish("错误：该技能不存在\n可用技能：\n" + str + "\n输入/yinpa_help skill [技能名或技能ID] 以查看技能描述")
        elif help_key[0] == 'state':
            if len(help_key) >= 2 and dicts.state_help.get(help_key[1]):
                await matcher.finish(MessageSegment.image(Utils.text_to_image(dicts.state_help[help_key[1]])))
            elif len(help_key) >= 2 and dicts.state_dict.get(int(help_key[1])):
                await matcher.finish(MessageSegment.image(Utils.text_to_image(dicts.state_help[dicts.state_dict[int(help_key[1])]])))
            else:
                str = ""
                for i in list(dicts.state_dict.keys()):
                    str += f"{i}：{dicts.state_dict[i]}\n"
                await matcher.finish("错误：该状态不存在\n可用状态：\n" + str + "\n输入/yinpa_help state [状态名或状态ID] 以查看状态描述")
        elif help_key[0] == "shop":
            if len(help_key) >= 2 and dicts.shop_help.get(help_key[1]):
                await matcher.finish(MessageSegment.image(Utils.text_to_image(dicts.shop_help[help_key[1]])))
            elif len(help_key) >= 2 and dicts.shop_dict.get(int(help_key[1])):
                await matcher.finish(MessageSegment.image(Utils.text_to_image(dicts.shop_help[dicts.shop_dict[int(help_key[1])]])))
            else:
                str = ""
                for i in list(dicts.shop_dict.keys()):
                    str += f"{i}：{dicts.shop_dict[i]} 售价：{dicts.shop_price_dict[i]}\n"
                await matcher.finish("错误：该商品不存在\n可用商品：\n" + str + "\n输入/yinpa_help shop [商品名或商品ID] 以查看商品描述")
        elif help_key[0] == "work":
            if len(help_key) >= 2 and dicts.work_dict.get(help_key[1]):
                await matcher.finish(MessageSegment.image(Utils.text_to_image(dicts.work_help_dict[help_key[1]])))
            elif len(help_key) >= 2 and dicts.work_dict.get(int(help_key[1])):
                await matcher.finish(MessageSegment.image(Utils.text_to_image(dicts.work_help_dict[dicts.work_dict[int(help_key[1])]])))
            else:
                str = ""
                for i in list(dicts.work_dict.keys()):
                    str += f"{i}：{dicts.work_dict[i]}\n"
                await matcher.finish("错误：该工作不存在\n可用工作：\n" + str + "\n输入/yinpa_help work [工作名或工作ID] 以查看工作描述")
        elif dicts.yinpa_help_dict.get(help_key[0]):
            await matcher.finish(MessageSegment.image(Utils.text_to_image(dicts.yinpa_help_dict[help_key[0]])))
        else:
            await matcher.finish(MessageSegment.image(Utils.text_to_image("错误：不存在对应的帮助\n可用帮助：\n" + "\n".join(list(dicts.yinpa_help_dict.keys())))))

    async def yinpa_info(
            matcher: Matcher,event: GroupMessageEvent,args: Message = CommandArg()
    ):
        """处理查询信息
        """
        
        if not Utils.group_enable_check(event.group_id):
            await matcher.finish("本群银趴已禁用")
        at:list = Utils.get_at(event)
        if not at:
            arg_list = (args.extract_plain_text()).split()
            if arg_list:
                f_uid = None
                for i in arg_list:
                    f_uid = Utils.find_user_name(i)
                    if f_uid:
                        at = [f_uid]
                        break
                if not f_uid:
                    await matcher.finish("错误：未找到目标！")
        else:
            at = [at[0]]
        uid: str = event.get_user_id()
        if not at or at == ['all']:
            if not data.get(uid):
                await matcher.finish("错误：你还没加入银趴！")
            await matcher.finish(MessageSegment.image(await Utils.get_user_info_image(uid)))
        else:
            at = at[0]
            if not data.get(at):
                await matcher.finish("错误：目标还没加入银趴！")
            await matcher.finish(MessageSegment.image(await Utils.get_user_info_image(at)))

    async def yinpa_tou(
            matcher: Matcher,event: GroupMessageEvent,args: Message = CommandArg()
    ):
        """处理透人
        """
        
        if not Utils.group_enable_check(event.group_id):
            await matcher.finish("本群银趴已禁用")
        at:list = Utils.get_at(event)
        if not at:
            arg_list = (args.extract_plain_text()).split()
            if arg_list:
                f_uid = None
                for i in arg_list:
                    f_uid = Utils.find_user_name(i)
                    if f_uid:
                        at = f_uid
                        break
                if not f_uid:
                    await matcher.finish("错误：未找到目标！")
            else:
                await matcher.finish("错误：未指定目标！")
        elif at == ['all']:
            await matcher.finish("错误：未指定目标！")
        else:
            at = at[0]
        uid: str = event.get_user_id()
        if not Utils.yinpa_user_presence_check(uid):
            await matcher.finish("您还未加入银趴！\ntips：请使用 /yinpa_join 或 /加入银趴 加入银趴")
        if not Utils.yinpa_user_presence_check(at):
            await matcher.finish("对方还未加入银趴！")
        if uid == at:
            await matcher.finish("你想透自己？请使用 /冲 或 /扣")
        await Utils.refresh_data(uid)
        await Utils.refresh_data(at)
        oc = await Utils.operation_check(uid)
        if oc:
            await matcher.finish(f"错误：操作失败！\n原因：{oc}")
        if Utils.get_state(at,2):
            await matcher.finish(f"错误：操作失败！\n原因：你连昏迷的{data[at]['name']}都不放过吗？")
        pl = (int)(data[uid]['penis_length']) * 4
        if pl >= 80:
            pl = 80 + sqrt(pl - 80)
        atk_u = await Utils.get_attack_list(uid,at) + [[pl,f"{data[uid]['name']}：长度",False]]
        str_u = f"{data[at]['name']}受到的伤害：1d50"
        for i in atk_u:
            if i[2]:
                if i[0] > 0:
                    str_u += f" + {int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_u += f" - {-int(i[0])}（{i[1]}）"
            else:
                if i[0] > 0:
                    str_u += f" + 1d{int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_u += f" - 1d{-int(i[0])}（{i[1]}）"
        res_u = Utils.dice(50,uid)
        str_u += f" = {res_u}"
        for i in atk_u:
            if i[2]:
                if i[0] > 0:
                    str_u += f" + {int(i[0])}"
                    res_u += int(i[0])
                elif i[0] < 0:
                    str_u += f" - {int(i[0])}"
                    res_u -= int(i[0])
            else:
                if i[0] > 0:
                    d = Utils.dice(int(i[0]),(int)(uid) ^ int(i[0]) ^ 101)
                    str_u += f" + {d}"
                    res_u += d
                elif i[0] < 0:
                    d = Utils.dice(-int(i[0]),(int)(uid) ^ int(i[0]) ^ 102)
                    str_u += f" - {d}"
                    res_u -= d
        str_u += f" = {res_u}\n"
        if res_u <= 0:
            res_u = 0
            str_u += " = 0"
        vd = (int)(data[at]['vagina_depth']) * 4
        if vd >= 80:
            vd = 80 + sqrt(vd - 80)
        atk_t = await Utils.get_attack_list(at,uid) + [[vd,f"{data[at]['name']}：深度",False]]
        str_t = f"{data[uid]['name']}受到的伤害：1d50"
        for i in atk_t:
            if i[2]:
                if i[0] > 0:
                    str_t += f" + {int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_t += f" - {-int(i[0])}（{i[1]}）"
            else:
                if i[0] > 0:
                    str_t += f" + 1d{int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_t += f" - 1d{-int(i[0])}（{i[1]}）"
        res_t = Utils.dice(50,at)
        str_t += f" = {res_t}"
        for i in atk_t:
            if i[2]:
                if i[0] > 0:
                    str_t += f" + {int(i[0])}"
                    res_t += int(i[0])
                elif i[0] < 0:
                    str_t += f" - {int(i[0])}"
                    res_t -= int(i[0])
            else:
                if i[0] > 0:
                    d = Utils.dice(int(i[0]),(int)(at) ^ int(i[0]) ^ 103)
                    str_t += f" + {d}"
                    res_t += d
                elif i[0] < 0:
                    d = Utils.dice(-int(i[0]),(int)(at) ^ int(i[0]) ^ 104)
                    str_t += f" - {d}"
                    res_t -= d
        str_t += f" = {res_t}"
        if res_t <= 0:
            res_t = 0
            str_t += " = 0"
        hp_u = Utils.get_value(uid,"hp")
        hp_t = Utils.get_value(at,"hp")
        hp_str = f"HP： {hp_u[0]} → {hp_u[0] - res_t} "
        if hp_u[1]:
            hp_str += "（体质）"
        hp_str += f" | {hp_t[0]} → {hp_t[0] - res_u} "
        if hp_t[1]:
            hp_str += "（体质）"
        rh_str_u = Utils.reduce_hp(uid,res_t)
        rh_str_t = Utils.reduce_hp(at,res_u)
        DHandles.data_set(uid,"active_times",data[uid]["active_times"] + 1)
        DHandles.data_set(at,"passive_times",data[at]["passive_times"] + 1)
        DHandles.achievement_set(uid,"A02")
        await matcher.finish(MessageSegment.image(Utils.text_to_image(f"{data[uid]['name']}透了{data[at]['name']}\n" + str_t + "\n" + str_u + hp_str +  rh_str_u +  rh_str_t)))
        
    async def yinpa_zha(
            matcher: Matcher,event: GroupMessageEvent,args: Message = CommandArg()
    ):
        """处理榨人
        """
        
        if not Utils.group_enable_check(event.group_id):
            await matcher.finish("本群银趴已禁用")
        at:list = Utils.get_at(event)
        if not at:
            arg_list = (args.extract_plain_text()).split()
            if arg_list:
                f_uid = None
                for i in arg_list:
                    f_uid = Utils.find_user_name(i)
                    if f_uid:
                        at = f_uid
                        break
                if not f_uid:
                    await matcher.finish("错误：未找到目标！")
            else:
                await matcher.finish("错误：未指定目标！")
        elif at == ['all']:
            await matcher.finish("错误：未指定目标！")
        else:
            at = at[0]
        uid: str = event.get_user_id()
        if not Utils.yinpa_user_presence_check(uid):
            await matcher.finish("您还未加入银趴！\ntips：请使用 /yinpa_join 或 /加入银趴 加入银趴")
        if not Utils.yinpa_user_presence_check(at):
            await matcher.finish("对方还未加入银趴！")
        if uid == at:
            await matcher.finish("你想榨自己？请使用 /冲 或 /扣")
        await Utils.refresh_data(uid)
        await Utils.refresh_data(at)
        oc = await Utils.operation_check(uid)
        if oc:
            await matcher.finish(f"错误：操作失败！\n原因：{oc}")
        if Utils.get_state(at,2):
            await matcher.finish(f"错误：操作失败！\n原因：你连昏迷的{data[at]['name']}都不放过吗？")
        vd = (int)(data[uid]['vagina_depth']) * 4
        if vd >= 80:
            vd = 80 + sqrt(vd - 80)
        atk_u = await Utils.get_attack_list(uid,at) + [[vd,f"{data[uid]['name']}：深度",False]]
        str_u = f"{data[at]['name']}受到的伤害：1d50"
        for i in atk_u:
            if i[2]:
                if i[0] > 0:
                    str_u += f" + {int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_u += f" - {-int(i[0])}（{i[1]}）"
            else:
                if i[0] > 0:
                    str_u += f" + 1d{int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_u += f" - 1d{-int(i[0])}（{i[1]}）"
        res_u = Utils.dice(50,uid)
        str_u += f" = {res_u}"
        for i in atk_u:
            if i[2]:
                if i[0] > 0:
                    str_u += f" + {int(i[0])}"
                    res_u += int(i[0])
                elif i[0] < 0:
                    str_u += f" - {int(i[0])}"
                    res_u -= int(i[0])
            else:
                if i[0] > 0:
                    d = Utils.dice(int(i[0]),(int)(uid) ^ int(i[0]) ^ 101)
                    str_u += f" + {d}"
                    res_u += d
                elif i[0] < 0:
                    d = Utils.dice(-int(i[0]),(int)(uid) ^ int(i[0]) ^ 102)
                    str_u += f" - {d}"
                    res_u -= d
        str_u += f" = {res_u}\n"
        if res_u <= 0:
            res_u = 0
            str_u += " = 0"
        pl = (int)(data[at]['penis_length']) * 4
        if pl >= 80:
            pl = 80 + sqrt(pl - 80)
        atk_t = await Utils.get_attack_list(at,uid) + [[pl,f"{data[at]['name']}：长度",False]]
        str_t = f"{data[uid]['name']}受到的伤害：1d50"
        for i in atk_t:
            if i[2]:
                if i[0] > 0:
                    str_t += f" + {int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_t += f" - {-int(i[0])}（{i[1]}）"
            else:
                if i[0] > 0:
                    str_t += f" + 1d{int(i[0])}（{i[1]}）"
                elif i[0] < 0:
                    str_t += f" - 1d{-int(i[0])}（{i[1]}）"
        res_t = Utils.dice(50,at)
        str_t += f" = {res_t}"
        for i in atk_t:
            if i[2]:
                if i[0] > 0:
                    str_t += f" + {int(i[0])}"
                    res_t += int(i[0])
                elif i[0] < 0:
                    str_t += f" - {int(i[0])}"
                    res_t -= int(i[0])
            else:
                if i[0] > 0:
                    d = Utils.dice(int(i[0]),(int)(at) ^ int(i[0]) ^ 103)
                    str_t += f" + {d}"
                    res_t += d
                elif i[0] < 0:
                    d = Utils.dice(-int(i[0]),(int)(at) ^ int(i[0]) ^ 104)
                    str_t += f" - {d}"
                    res_t -= d
        str_t += f" = {res_t}"
        if res_t <= 0:
            res_t = 0
            str_t += " = 0"
        hp_u = Utils.get_value(uid,"hp")
        hp_t = Utils.get_value(at,"hp")
        hp_str = f"HP： {hp_u[0]} → {hp_u[0] - res_t}"
        if hp_u[1]:
            hp_str += "（体质）"
        hp_str += f" | {hp_t[0]} → {hp_t[0] - res_u}"
        if hp_t[1]:
            hp_str += "（体质）"
        rh_str_u = Utils.reduce_hp(uid,res_t)
        rh_str_t = Utils.reduce_hp(at,res_u)
        DHandles.data_set(uid,"active_times",data[uid]["active_times"] + 1)
        DHandles.data_set(at,"passive_times",data[at]["passive_times"] + 1)
        DHandles.achievement_set(uid,"A02")
        await matcher.finish(MessageSegment.image(Utils.text_to_image(f"{data[uid]['name']}榨了{data[at]['name']}\n" + str_t  + "\n" + str_u + hp_str + rh_str_u + rh_str_t)))
        
    async def yinpa_chong(
            matcher: Matcher,event: GroupMessageEvent
    ):
        """处理冲
        """
        
        if not Utils.group_enable_check(event.group_id):
            await matcher.finish("本群银趴已禁用")
        uid: str = event.get_user_id()
        if not Utils.yinpa_user_presence_check(event.get_user_id()):
            await matcher.finish("您还未加入银趴！\ntips：请使用 /yinpa_join 或 /加入银趴 加入银趴")
        oc = await Utils.operation_check(uid)
        if oc:
            await matcher.finish(f"错误：操作失败！\n原因：{oc}")
        await Utils.refresh_data(uid)
        d = Utils.dice(100,uid)
        hp = Utils.get_value(uid,"hp")
        pl_str = f"长度： {data[uid]['penis_length']} → {round(data[uid]['penis_length'] + d / 100 - 0.5,2)}"
        DHandles.data_set(uid,'penis_length',round(data[uid]['penis_length'] + d / 100 - 0.5,2))
        hp_str = f"HP： {hp[0]} → {hp[0] - d}"
        rh_str = Utils.reduce_hp(uid,d)
        await matcher.finish(f"{data[uid]['name']}冲了一发\n" + pl_str + "\n" + hp_str + rh_str)
        
    async def yinpa_kou(
            matcher: Matcher,event: GroupMessageEvent
    ):
        """处理扣
        """
        
        if not Utils.group_enable_check(event.group_id):
            await matcher.finish("本群银趴已禁用")
        uid: str = event.get_user_id()
        if not Utils.yinpa_user_presence_check(event.get_user_id()):
            await matcher.finish("您还未加入银趴！\ntips：请使用 /yinpa_join 或 /加入银趴 加入银趴")
        oc = await Utils.operation_check(uid)
        if oc:
            await matcher.finish(f"错误：操作失败！\n原因：{oc}")
        await Utils.refresh_data(uid)
        d = Utils.dice(40,uid)
        hp = Utils.get_value(uid,"hp")
        vd_str = f"深度： {data[uid]['vagina_depth']} → {round(data[uid]['vagina_depth'] + d / 100,2)}"
        DHandles.data_set(uid,'vagina_depth',round(data[uid]['vagina_depth'] + d / 100,2))
        hp_str = f"HP： {hp[0]} → {hp[0] - d}"
        rh_str = Utils.reduce_hp(uid,d)
        await matcher.finish(f"{data[uid]['name']}扣了一次\n" + vd_str + "\n" + hp_str + rh_str)

    async def yinpa_shop(
            matcher: Matcher,event: GroupMessageEvent,args: Message = CommandArg()
    ):
        """处理商店
        """
        
        if not Utils.group_enable_check(event.group_id):
            await matcher.finish("本群银趴已禁用")
        uid = event.get_user_id()
        if not Utils.yinpa_user_presence_check(uid):
            await matcher.finish("您还未加入银趴！\ntips：请使用 /yinpa_join 或 /加入银趴 加入银趴")
        command = args.extract_plain_text()
        shop_key = command.split()
        if not shop_key:
            str = ""
            for i in list(dicts.shop_dict.keys()):
                str += f"{i}：{dicts.shop_dict[i]} 售价：{dicts.shop_price_dict[i]}\n"
            await matcher.finish(MessageSegment.image(Utils.text_to_image("可用商品：\n" + str + "\n输入/yinpa_help shop [商品名或商品ID] 以查看商品描述")))
        else:
            goods = shop_key
            price = 0
            for i in goods:
                if not dicts.shop_dict.get(i) and not dicts.shop_help.get(i) and not dicts.shop_dict.get(int(i)):
                    str = ""
                    for j in list(dicts.shop_dict.keys()):
                        str += f"{j}：{dicts.shop_dict[j]} 售价：{dicts.shop_price_dict[j]}\n"
                    await matcher.finish(MessageSegment.image(Utils.text_to_image("错误：该商品不存在\n可用商品：\n" + str + "\n输入/yinpa_help shop [商品名或商品ID] 以查看商品描述")))
                if i in list(dicts.shop_dict.values()):
                    i = (list(dicts.shop_dict.keys()))[(list(dicts.shop_dict.values())).index(i)]
                i = int(i)
                price += dicts.shop_price_dict[i]
            current_money = await Utils.get_money(uid)
            if current_money < price:
                await matcher.finish(f"错误：你的 YPD 并不够买这些商品！\n这些商品的总售价：{price}\n你的 YPD：{current_money}")
            await Utils.add_money(uid, -price)
            str = ""
            for i in goods:
                i = int(i)
                str += await Utils.gain_item(uid,i)
            await matcher.finish(MessageSegment.image(Utils.text_to_image(str)))

    async def yinpa_work(
            matcher: Matcher,event: GroupMessageEvent,args: Message = CommandArg()
    ):
        """处理工作
        """
        
        if not Utils.group_enable_check(event.group_id):
            await matcher.finish("本群银趴已禁用")
        uid = event.get_user_id()
        if not Utils.yinpa_user_presence_check(event.get_user_id()):
            await matcher.finish("您还未加入银趴！\ntips：请使用 /yinpa_join 或 /加入银趴 加入银趴")
        await Utils.refresh_data(uid)
        command = args.extract_plain_text()
        work_key = command.split()
        if not work_key:
            msg = ""
            for i in list(dicts.work_dict.keys()):
                msg += f"{i}：{dicts.work_dict[i]}\n"
            await matcher.finish(MessageSegment.image(Utils.text_to_image("可用工作：\n" + msg + "\n输入/yinpa_help work [工作名或工作ID] 以查看工作描述")))
        work_key = work_key[0]
        if not dicts.work_dict.get(work_key) and not dicts.work_help_dict.get(work_key) and not dicts.work_dict.get(int(work_key)):
            msg = ""
            for i in list(dicts.work_dict.keys()):
                msg += f"{i}：{dicts.work_dict[i]}"
            await matcher.finish(MessageSegment.image(Utils.text_to_image("错误：该工作不存在\n可用工作：\n" + msg + "\n输入/yinpa_help work [工作名或工作ID] 以查看工作描述")))
        oc = await Utils.operation_check(uid)
        if oc:
            await matcher.finish(f"错误：操作失败！\n原因：{oc}")
        if DHandles.work_cooldown_get(uid) >= time():
            await matcher.finish("你现在正在工作冷却中！")
        if work_key in list(dicts.work_dict.values()):
            work_key = (list(dicts.work_dict.keys()))[(list(dicts.work_dict.values())).index(work_key)]
        work_key = int(work_key)
        if work_key != 3:
            DHandles.data_set(uid,'live_broken',True)
        msg = ""
        money = 0.0
        if work_key == 1:
            # 搬砖：勤能补拙（基础属性 + 1d500，累计次数递减加成，封顶 +25%）
            money += (data[uid]['strength'] + data[uid]['constitution']) * Utils.dice(500,data[uid]['strength'] + data[uid]['constitution']) / 8
            brick_count = data[uid].get('brick_count',0)
            multiplier = 1 + 0.25 * (1 - exp(-brick_count / 15))
            money *= multiplier
            if money < 0:
                money = 0
            money = round(money, 2)
            DHandles.data_set(uid,'brick_count',brick_count + 1)
            msg += f"你进行了工作：{dicts.work_dict[work_key]}\n收益：{money}\n"
            msg += f"搬砖经验累积！本次搬砖收入 ×{round(multiplier,3)}\n"
        elif work_key == 2:
            # 援交：基础属性 + 1d500，榨精心得检定 + 意志检定失神
            money += (data[uid]['technique'] * 0.7 + data[uid]['charm'] * 0.9) * Utils.dice(500,data[uid]['technique'] + data[uid]['charm']) / 6
            if money < 0:
                money = 0
            money = round(money, 2)
            msg += f"你进行了工作：{dicts.work_dict[work_key]}\n收益：{money}\n"
            d = Utils.dice(400,data[uid]['technique'] + data[uid]['charm'])
            msg += f"榨精心得检定：1d400 = {d} "
            if d < (data[uid]['technique'] + data[uid]['charm']):
                if Utils.get_state(uid,4):
                    msg += f" < {data[uid]['technique'] + data[uid]['charm']}\n你已拥有【榨精心得】，本次不再重复获得。\n"
                else:
                    DHandles.state_refresh(uid,4,time() + 315360000)
                    msg += f" < {data[uid]['technique'] + data[uid]['charm']}\n获得状态：【榨精心得】（ID：4），作为主动方时额外造成对方当前HP的10%。\n"
            else:
                msg += f" >= {data[uid]['technique'] + data[uid]['charm']}\n"
            d = Utils.dice(100,data[uid]['volition'])
            msg += f"意志检定：1d100 = {d} "
            if d >= data[uid]['volition']:
                DHandles.data_set(uid,"hp_v",0)
                d = min(Utils.dice(30,(int)(uid) ^ 100), 30)
                DHandles.state_refresh(uid,1,time() + d * 60)
                DHandles.achievement_set(uid,"A03")
                msg += f" >= {data[uid]['volition']}\n{data[uid]['name']}失神了！失神状态将持续1d30 = {d}分钟。（期间无法行动，技能失效。如果失神期间受到攻击，失神状态将延长一分钟。）"
            else:
                msg += f" < {data[uid]['volition']}\n"
        elif work_key == 3:
            # 直播：连续开播（2小时未直播或做过其他工作即断链）
            money += (data[uid]['intelligence'] + data[uid]['charm']) * Utils.dice(500,data[uid]['intelligence'] + data[uid]['charm']) / 8
            if money < 0:
                money = 0
            now = int(time())
            last_live_time = data[uid].get('last_live_time',0)
            live_bonus = data[uid].get('live_bonus',False)
            live_broken = data[uid].get('live_broken',False)
            broken = (now - last_live_time > 7200) or live_broken
            bonus_note = ""
            if not broken and live_bonus:
                money *= 1.3
                bonus_note = "\n连续直播加成：×1.3"
            elif broken and (last_live_time != 0 or live_broken):
                bonus_note = "\n连续直播加成断链，本次收益 ×1"
            money = round(money, 2)
            msg += f"你进行了工作：{dicts.work_dict[work_key]}\n收益：{money}{bonus_note}\n"
            DHandles.data_set(uid,'live_bonus',True)
            DHandles.data_set(uid,'last_live_time',now)
            DHandles.data_set(uid,'live_broken',False)
        elif work_key == 4:
            # 写文：基础属性 + 1d500，意志检定通过 ×1.3
            money += (data[uid]['technique'] + data[uid]['intelligence']) * Utils.dice(500,data[uid]['technique'] + data[uid]['intelligence']) / 9
            if money < 0:
                money = 0
            money = round(money, 2)
            msg += f"你进行了工作：{dicts.work_dict[work_key]}\n收益：{money}\n"
            d = Utils.dice(100,data[uid]['volition'])
            msg += f"意志检定：1d100 = {d} "
            if d < data[uid]['volition']:
                money *= 1.3
                money = round(money, 2)
                msg += f" < {data[uid]['volition']}\n文思泉涌！本次写文收益 ×1.3，最终收益：{money}\n"
            else:
                msg += f" >= {data[uid]['volition']}\n"
        elif work_key == 5:
            # 打架：基础属性 + 1d500，恒触发体质检定昏迷
            money += (data[uid]['strength'] + data[uid]['constitution']) * Utils.dice(500,data[uid]['strength'] + data[uid]['constitution']) / 6
            if money < 0:
                money = 0
            money = round(money, 2)
            msg += f"你进行了工作：{dicts.work_dict[work_key]}\n收益：{money}\n"
            d = Utils.dice(100,data[uid]['constitution'])
            msg += f"体质检定：1d100 = {d} "
            if d >= data[uid]['constitution']:
                DHandles.data_set(uid,"hp_v",0)
                d = Utils.dice(3,(int)(uid) ^ 103)
                DHandles.state_refresh(uid,2,time() + d * 3600)
                DHandles.achievement_set(uid,"A04")
                msg += f" >= {data[uid]['constitution']}\n{data[uid]['name']}昏迷了！昏迷状态将持续1d3 = {d}小时。（期间无法行动，无法被透，技能失效。）"
            else:
                msg += f" < {data[uid]['constitution']}\n"
        elif work_key == 6:
            # 探险：彩票（成功概率50%，事件触发率30%）
            d = Utils.dice(100,(int)(uid) ^ 102)
            money += (d - 50) * 300
            if money < 0:
                money = 0
            money = round(money, 2)
            msg += f"你进行了工作：{dicts.work_dict[work_key]}\n收益：{money}\n"
            if Utils.dice(10,(int)(uid) ^ 103) <= 3:
                d = Utils.dice(10,(int)(uid) ^ 104)
                if d >= 1 and d <= 3:
                    keys = ['strength','constitution','technique','volition','intelligence','charm']
                    i = keys[Utils.dice(6,(int)(uid) ^ 105) - 1]
                    d = Utils.dice(100,(int)(uid) ^ 106) / 20
                    new_value = data[uid][i] + d
                    if i in ['constitution','volition']:
                        new_value = min(new_value, 90)
                    msg += f"触发事件：你的{dicts.attribute_dict[i]}： {data[uid][i]} → {new_value}\n"
                    DHandles.data_set(uid,i,new_value)
                elif d >= 4 and d <= 6:
                    l = list(dicts.shop_dict.keys())
                    i = Utils.dice(len(l),(int)(uid) ^ 107)
                    msg += await Utils.gain_item(uid,l[i - 1])
                elif d >= 7 and d <= 9:
                    d = Utils.dice(1000,(int)(uid) ^ 108)
                    await Utils.add_money(uid, d)
                    msg += f"触发事件：金钱彩蛋 +{d} YPD\n"
                elif d == 10:
                    d = Utils.dice(5000,(int)(uid) ^ 109)
                    await Utils.add_money(uid, d)
                    l = list(dicts.shop_dict.keys())
                    i = Utils.dice(len(l),(int)(uid) ^ 110)
                    msg += f"触发稀有奇遇：金钱 +{d} YPD\n"
                    msg += await Utils.gain_item(uid,l[i - 1])
        DHandles.work_cooldown_set(uid,(time() + 3600))
        DHandles.data_set(uid,'work_count',data[uid].get('work_count',0) + 1)
        if work_key == 6:
            DHandles.data_set(uid,'explore_count',data[uid].get('explore_count',0) + 1)
        await Utils.add_money(uid, money)
        msg += "一小时内你将无法继续工作"
        await matcher.finish(MessageSegment.image(Utils.text_to_image(msg)))

    async def yinpa_transfer(
            matcher: Matcher,event: GroupMessageEvent,args: Message = CommandArg()
    ):
        """处理转账
        """
        
        if not Utils.group_enable_check(event.group_id):
            await matcher.finish("本群银趴已禁用")
        uid: str = event.get_user_id()
        if not Utils.yinpa_user_presence_check(uid):
            await matcher.finish("您还未加入银趴！\ntips：请使用 /yinpa_join 或 /加入银趴 加入银趴")
        at:list = Utils.get_at(event)
        command: str = args.extract_plain_text()
        arg_list: list = command.split()
        if not arg_list:
            await matcher.finish("错误：参数错误！\n命令：/transfer <金额> <@某人 或 银趴昵称>")
        if not arg_list[0].isdigit():
            await matcher.finish("错误：金额必须为正整数！")
        amount = int(arg_list[0])
        if amount <= 0:
            await matcher.finish("错误：金额必须为正整数！")
        if not at:
            f_uid = None
            for i in arg_list[1:]:
                f_uid = Utils.find_user_name(i)
                if f_uid:
                    at = [f_uid]
                    break
            if not f_uid:
                await matcher.finish("错误：未找到目标！")
        elif at == ['all']:
            await matcher.finish("错误：不能转账给所有人！")
        else:
            at = [at[0]]
        target: str = at[0]
        if not Utils.yinpa_user_presence_check(target):
            await matcher.finish("对方还未加入银趴！")
        if uid == target:
            await matcher.finish("你不能给自己转账！")
        current_money = await Utils.get_money(uid)
        if current_money < amount:
            await matcher.finish(f"错误：你的 YPD 不够！\n需要：{amount}\n你的 YPD：{current_money}")
        cooldown = plugin_config.chikari_yinpa_transfer_cooldown
        next_time = DHandles.transfer_cooldown_get(uid)
        if next_time >= time():
            await matcher.finish(f"错误：转账冷却中！\n剩余：{int(next_time - time())} 秒")
        await Utils.add_money(uid, -amount)
        await Utils.add_money(target, amount)
        DHandles.transfer_cooldown_set(uid, time() + cooldown)
        await matcher.finish(f"转账{amount}给{data[target]['name']}成功，现在你的余额是{await Utils.get_money(uid)}")

    # async def test(
    #     matcher: Matcher,event: GroupMessageEvent,args: Message = CommandArg()
    # ):
    #     """测试用
    #     """
        
    #     uid = event.get_user_id()
    #     #await matcher.finish(await Utils.get_group_yinpa_list((str)(event.self_id),event.group_id))
    #     await matcher.finish(MessageSegment.image(Utils.draw_rank_image(event.group_id,uid,(str)(event.self_id))))


def _join_pending_rule(event: GroupMessageEvent):
    """on_message 规则：仅当该用户处于创建流程中时接管其普通消息"""
    
    if not isinstance(event, GroupMessageEvent):
        return False
    return yinpa_Handles.is_join_pending(event.get_user_id())