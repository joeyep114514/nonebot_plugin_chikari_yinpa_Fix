from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot import get_bots

import json
from random import randint,seed,choice
from time import time,localtime
from PIL import Image,ImageDraw,ImageFont
from io import BytesIO
from math import sqrt, exp
from pathlib import Path

from .data_handles import data,configdata,DHandles
from .dicts import dicts
from .config import plugin_config
from nonebot_plugin_value.api import api_balance

# 钓鱼插件可选集成：用于成就扫描（B02/C03/C04/D01/D02）
try:
    from nonebot_plugin_fishing2.data_source import get_fishing_achievement_stats as _fishing_get_stats
    _FISHING_AVAILABLE = True
except Exception:
    _FISHING_AVAILABLE = False

class Utils:
    @staticmethod
    def _is_emoji(character: str):
        codepoint = ord(character)
        return (
            0x1F000 <= codepoint <= 0x1FAFF
            or 0x2600 <= codepoint <= 0x27BF
            or 0x2300 <= codepoint <= 0x23FF
            or 0x2B00 <= codepoint <= 0x2BFF
        )

    @staticmethod
    def _load_fonts(font_size: int):
        main_font = ImageFont.truetype(plugin_config.chikari_yinpa_font, font_size)
        # 修复可变字体默认字重过细的问题：
        # NotoSansCJKsc-VF.ttf 的 wght 轴默认值为 100（Thin），直接加载会渲染成极细字体，
        # 需显式设置为 Regular（400）才能正常显示。
        try:
            main_font.set_variation_by_name("Regular")
        except Exception:
            try:
                main_font.set_variation_by_axes([400])
            except Exception:
                pass
        emoji_path = Path(plugin_config.chikari_yinpa_emoji_font)
        try:
            emoji_font = ImageFont.truetype(emoji_path, font_size)
        except OSError:
            fallback = Path("/usr/share/fonts/noto/NotoColorEmoji.ttf")
            emoji_font = ImageFont.truetype(fallback, 109) if fallback.exists() else main_font
        return main_font, emoji_font, font_size / emoji_font.size

    @staticmethod
    def _draw_emoji(image, x: int, y: int, character: str, font, scale: float):
        bbox = font.getbbox(character)
        width = max(1, bbox[2] - bbox[0])
        height = max(1, bbox[3] - bbox[1])
        layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        ImageDraw.Draw(layer).text((-bbox[0], -bbox[1]), character, font=font,
                                   fill="#000000", embedded_color=False)
        if scale != 1:
            layer = layer.resize((max(1, round(width * scale)), max(1, round(height * scale))),
                                 Image.Resampling.LANCZOS)
        image.paste(layer, (x, y), layer)
        return layer.width

    def group_enable_check(groupid: int):
        """检查群组是否在银趴列表中

        Args:
            groupid (int): 群组id

        Returns:
            int: 是否出现
        """
        
        return configdata["yinpa_enabled_group"].count(groupid)
    
    def last_operation_time_check(uid: str):
        """检测上次行动时间

        Args:
            uid (str): 用户id

        Returns:
            bool: 是否到时
        """
        
        minutes=(int)(time()/60)
        if data[uid]["last_operation_time"] < minutes:
            return True
        return False
    
    def set_last_operation_time(uid: str):
        """设置上次行动时间

        Args:
            uid (str): 用户id
        """
        
        DHandles.data_set(uid,"last_operation_time",(int)(time()/60))
        return
    
    _dice_counter = 0
    def dice(d:int,_seed):
        """骰子

        Args:
            d (int): 上限
            _seed (_type_): 随机数种子

        Returns:
            int: 值
        """
        
        d = int(d)
        if d <= 0:
            return 0
        Utils._dice_counter += 1
        seed((int)(time() * 1000) ^ d ^ (int)(_seed) ^ (Utils._dice_counter * 7919))
        return randint(1, d)
    
    def get_at(event: GroupMessageEvent):
        """获取消息中的at

        Args:
            event (GroupMessageEvent): 消息

        Returns:
            list: at列表
        """
        
        try:
            qq_list = []
            msg = json.loads(event.json())
            for i in msg['message']:
                if i['type'] == 'at':
                    if 'all' not in str(i):
                        qq_list.append((str)(int(i['data']['qq'])))
                    else:
                        return ['all']
            if event.to_me:
                qq_list += [(str)(event.self_id)]
            return qq_list
        except KeyError:
            return []

    def yinpa_user_presence_check(uid: str):
        """检查用户是否存在

        Args:
            uid (str): 用户id

        Returns:
            bool: 用户是否存在
        """
        
        if data.get(uid):
            return True
        return False

    @staticmethod
    async def get_money(uid: str) -> float:
        """获取用户的 YPD 数量

        Args:
            uid (str): 用户id

        Returns:
            float: YPD 数量
        """
        account = await api_balance.get_or_create_account(uid, "YPD")
        return account.balance

    @staticmethod
    async def set_money(uid: str, value: float) -> float:
        """设置用户的 YPD 数量

        Args:
            uid (str): 用户id
            value (float): YPD 数量

        Returns:
            float: 设置后的 YPD 数量
        """
        account = await api_balance.get_or_create_account(uid, "YPD")
        diff = value - account.balance
        if diff > 0:
            await api_balance.add_balance(uid, diff, "yinpa_set", "YPD")
        elif diff < 0:
            await api_balance.del_balance(uid, -diff, "yinpa_set", "YPD")
        return value

    @staticmethod
    async def add_money(uid: str, value: float) -> float:
        """增加/减少用户的 YPD 数量

        Args:
            uid (str): 用户id
            value (float): 变化量（负数为减少）

        Returns:
            float: 变化后的 YPD 数量
        """
        if value > 0:
            await api_balance.add_balance(uid, value, "yinpa_add", "YPD")
        elif value < 0:
            await api_balance.del_balance(uid, -value, "yinpa_del", "YPD")
        account = await api_balance.get_or_create_account(uid, "YPD")
        return account.balance
    
    def text_to_image(text: str):
        """文字转图片

        Args:
            text (str): 要转换的文字

        Returns:
            bytes: 图片
        """
        
        fontSize = 20
        # 防御：限制单行长度与总行数，防止超长文本（如超长昵称）触发超大图像分配导致内存/CPU 耗尽
        max_line_len = 100
        max_lines = 100
        # 自动换行宽度上限：超过该宽度（像素）的单行会折行，避免渲染出超宽长条图
        max_width = 800
        liens = text.split('\n')
        liens = [line[:max_line_len] for line in liens][:max_lines]
        font, emoji_font, emoji_scale = Utils._load_fonts(fontSize)

        def _char_width(character: str) -> float:
            return (emoji_font.getlength(character) * emoji_scale if Utils._is_emoji(character)
                    else font.getlength(character))

        # 按像素宽度自动换行
        wrapped_lines = []
        for line in liens:
            if not line:
                wrapped_lines.append("")
                continue
            cur = ""
            cur_width = 0.0
            for character in line:
                w = _char_width(character)
                if cur and cur_width + w > max_width:
                    wrapped_lines.append(cur)
                    cur = character
                    cur_width = w
                else:
                    cur += character
                    cur_width += w
            wrapped_lines.append(cur)
        liens = wrapped_lines[:max_lines]

        line_widths = []
        for line in liens:
            line_width = 0
            for character in line:
                line_width += _char_width(character)
            line_widths.append(line_width)
        image = Image.new("RGB", (max(1, int(max(line_widths, default=0))), len(liens) * (fontSize + 5)), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        for line_number, line in enumerate(liens):
            x = 0
            y = line_number * (fontSize + 5)
            for character in line:
                if Utils._is_emoji(character):
                    x += Utils._draw_emoji(image, int(x), y, character, emoji_font, emoji_scale)
                else:
                    draw.text((x, y), character, font=font, fill="#000000", stroke_width=0)
                    x += font.getlength(character)
        img = image.convert("RGB")
        img_byte = BytesIO()
        img.save(img_byte,"PNG")
        return img_byte.getvalue()

    async def get_user_info_image(uid: str):
        """获取用户的信息图

        Args:
            uid (str): 用户id

        Returns:
            bytes: 图片
        """
        
        await Utils.refresh_data(uid)
        await Utils.achievement_scan(uid)
        user_data = data[uid]
        skill_text = ""
        state_text = ""
        for i in user_data["skill"]:
            if i[0] == 6 and i[1] and i[1] >= time():
                skill_text += "\n    ——" + dicts.skill_dict[i[0]] + f'（等级：{i[2]}）（舰装损坏，{(int)(i[1] - time())}秒后修复）' + '；'
            else:
                skill_text += "\n    ——" + dicts.skill_dict[i[0]] + f'（等级：{i[2]}）' + '；'
        if not skill_text:
            skill_text = '无'
        for i in user_data["state"]:
            if i[0] == 4:
                state_text += dicts.state_dict[i[0]] + f'（等级：{i[2]}）（永久，触发后消耗）' + '；'
            else:
                state_text += dicts.state_dict[i[0]] + f'（等级：{i[2]}）（剩余时间：{(int)(i[1] - time())}秒）' + '；'
        if not state_text:
            state_text = '无'
        ach_list = data[uid].get("achievements") or []
        ach_names = "、".join([dicts.achievement_dict.get(a, a) for a in ach_list]) if ach_list else "无"
        ach_text = f"成就：{len(ach_list)}/24\n已达成：{ach_names}"
        text = f"    ID：{uid}\n"\
        f"    昵称：{user_data['name']}\n"\
        f"    种族：{dicts.species_dict[user_data['species']]}\n"\
        f"    意志HP：{user_data['hp_v']}\n"\
        f"    体质HP：{user_data['hp_c']}\n"\
        f"    长度：{round(user_data['penis_length'], 2)}\n"\
        f"    深度：{round(user_data['vagina_depth'], 2)}\n"\
        f"    力量：{Utils.get_value(uid,'strength')[0]}\n"\
        f"    体质：{Utils.get_value(uid,'constitution')[0]}\n"\
        f"    技巧：{Utils.get_value(uid,'technique')[0]}\n"\
        f"    意志：{Utils.get_value(uid,'volition')[0]}\n"\
        f"    智力：{Utils.get_value(uid,'intelligence')[0]}\n"\
        f"    魅力：{Utils.get_value(uid,'charm')[0]}\n"\
        f"    YPD：{await Utils.get_money(uid)}\n"\
        f"    技能：{skill_text}\n"\
        f"    状态：{state_text}\n"\
        f"    被动次数：{user_data['passive_times']}\n"\
        f"    主动次数：{user_data['active_times']}\n"\
        f"    {ach_text}"\
        
        return Utils.text_to_image(text)
    
    async def achievement_scan(uid: str):
        """扫描可回溯成就并写入新达成者

        Args:
            uid (str): 用户id
        """
        
        if not isinstance(data[uid].get("achievements"), list):
            DHandles.data_set(uid,"achievements",[])
        money = await Utils.get_money(uid)
        if money >= 1000:
            DHandles.achievement_set(uid,"A05")
        if money >= 10000:
            DHandles.achievement_set(uid,"A06")
        if money >= 1000000:
            DHandles.achievement_set(uid,"B05")
        if money >= 10000000:
            DHandles.achievement_set(uid,"D03")
        if data[uid].get("work_count",0) >= 100:
            DHandles.achievement_set(uid,"B01")
        if data[uid].get("sign_in_count",0) >= 30:
            DHandles.achievement_set(uid,"B03")
        if data[uid].get("active_times",0) + data[uid].get("passive_times",0) >= 100:
            DHandles.achievement_set(uid,"B04")
        if data[uid].get("d10_count",0) >= 50:
            DHandles.achievement_set(uid,"B06")
        if data[uid].get("pandora_count",0) >= 30:
            DHandles.achievement_set(uid,"B07")
        if data[uid].get("explore_count",0) >= 50:
            DHandles.achievement_set(uid,"B08")
        skill_ids = [s[0] for s in data[uid].get("skill",[])]
        if all(sid in skill_ids for sid in range(2,10)):
            DHandles.achievement_set(uid,"C01")
        if sum(1 for sid in skill_ids if 10 <= sid <= 15) >= 3:
            DHandles.achievement_set(uid,"C02")
        if _FISHING_AVAILABLE:
            try:
                fstats = await _fishing_get_stats(uid)
            except Exception:
                fstats = None
            if fstats:
                if fstats.get("frequency",0) >= 100:
                    DHandles.achievement_set(uid,"B02")
                if fstats.get("caught_all_catchable"):
                    DHandles.achievement_set(uid,"C03")
                if fstats.get("caught_all_catchable") and fstats.get("has_special"):
                    DHandles.achievement_set(uid,"C04")
                if fstats.get("total_spent",0) >= 1000000:
                    DHandles.achievement_set(uid,"D01")
                if fstats.get("has_eternal_rod"):
                    DHandles.achievement_set(uid,"D02")
        return
    
    async def refresh_data(uid: str):
        """更新用户数据

        Args:
            uid (str): 用户id
        """
        
        b = False
        for i in data[uid]["skill"]:
            if len(i) <= 2:
                DHandles.skill_refresh(uid,i[0],i[1])
        for i in data[uid]["state"]:
            if len(i) <= 2:
                DHandles.state_refresh(uid,i[0],i[1])
        new_state = list(data[uid]["state"])
        for i in data[uid]["state"]:
            if i[1] <= time():
                new_state.remove(i)
            if i[0] == 1:
                if i[1] > time():
                    b = True
                else:
                    DHandles.data_set(uid,'hp_v',Utils.get_hp_v_max(uid))
            elif i[0] == 2 and i[1] <= time():
                DHandles.data_set(uid,'hp_v',Utils.get_hp_v_max(uid))
                DHandles.data_set(uid,'hp_c',Utils.get_hp_c_max(uid))
        DHandles.data_set(uid,"state",new_state)
        if b :
            if data[uid]['hp_c'] + (int)(((int)(time()) - (int)(data[uid]["last_refresh_time"])) / 60) >= Utils.get_hp_c_max(uid):
                DHandles.data_set(uid,'hp_c',Utils.get_hp_c_max(uid))
            else:
                DHandles.data_set(uid,'hp_c',data[uid]['hp_c'] + ((int)(((int)(time()) - (int)(data[uid]["last_refresh_time"])) / 60)) * Utils.get_regeneration_rate(uid))
        else:
            DHandles.data_set(uid,'hp_c',Utils.get_hp_c_max(uid))
            if data[uid]['hp_v'] + (int)(((int)(time()) - (int)(data[uid]["last_refresh_time"])) / 60) >= Utils.get_hp_v_max(uid):
                DHandles.data_set(uid,'hp_v',Utils.get_hp_v_max(uid))
            else:
                DHandles.data_set(uid,'hp_v',data[uid]['hp_v'] + ((int)(((int)(time()) - (int)(data[uid]["last_refresh_time"])) / 60)) * Utils.get_regeneration_rate(uid))
        DHandles.data_set(uid,"last_refresh_time",time())
        return

    def get_skill(uid: str,id: int):
        """获取技能

        Args:
            uid (str): 用户id
            id (int): 技能id

        Returns:
            list: [技能id,附加数据,等级]
        """
        
        s = []
        for i in data[uid]["skill"]:
            if i[0] == id:
                s = i
            if len(i) <= 2:
                DHandles.skill_refresh(uid,i[0],i[1])
        if s and s[0] not in [9,10,11,12,13,14,15,] and Utils.get_state(uid,1):
            s = []
        return s

    def get_state(uid: str,id: int):
        """获取状态

        Args:
            uid (str): 用户id
            id (int): 状态id

        Returns:
            list: [状态id,结束时间,等级]
        """
        
        s = []
        for i in data[uid]["state"]:
            if i[0] == id:
                s = i
            if len(i) <= 2:
                DHandles.state_refresh(uid,i[0],i[1])
        return s

    def is_night():
        """判断是否为晚上

        Returns:
            bool: 是否为晚上
        """
        
        b = True
        hour = localtime().tm_hour
        if hour >= 6 and hour < 18:
            b = False
        return b

    def boat(uid: str):
        """判断舰装是否生效

        Args:
            uid (str): 用户id

        Returns:
            list: 舰装技能条目，未生效时返回空列表
        """
        
        s = Utils.get_skill(uid,6)
        if not s:
            return []

        cooldown_end = s[1]
        if cooldown_end is None or cooldown_end <= time():
            return s
        return []

    def vampire(uid: str):
        """判断吸血鬼技能是否生效

        Args:
            uid (str): 用户id

        Returns:
            int: 加成值，无吸血鬼技能时返回0
        """
        
        if  i := Utils.get_skill(uid,7):
            if Utils.is_night():
                return 10 * sqrt(i[2])
            else:
                return -15 / sqrt(i[2])
        return 0

    def get_hp_bonus(uid: str):
        """舰装血量上限加成

        舰装未破损时，意志HP与体质HP上限各增加 200×√(等级)。

        Args:
            uid (str): 用户id

        Returns:
            int: 血量上限加成
        """
        
        if i := Utils.boat(uid):
            return int(200 * sqrt(i[2]))
        return 0

    def get_hp_v_max(uid: str):
        """获取意志HP上限

        Args:
            uid (str): 用户id

        Returns:
            int: 意志HP上限
        """
        
        return int((Utils.get_value(uid,'volition')[0] + 10) * 5) + Utils.get_hp_bonus(uid)

    def get_hp_c_max(uid: str):
        """获取体质HP上限

        Args:
            uid (str): 用户id

        Returns:
            int: 体质HP上限
        """
        
        return int((Utils.get_value(uid,'constitution')[0] + 10) * 10) + Utils.get_hp_bonus(uid)

    def get_value(uid: str,key: str):
        """获取用户当前状态下的某一数值

        Args:
            uid (str): 用户id
            key (str): 数值名

        Returns:
            list: [数值,附加信息]
        """
        
        b = False
        value = 0
        if key == "hp":
            if Utils.get_state(uid,1):
                b = True
            if b:
                hp = data[uid]['hp_c']
            else:
                hp = data[uid]['hp_v']
            value = hp
        elif key == 'penis_length':
            value = data[uid]['penis_length']
        elif key == 'vagina_depth':
            value = data[uid]['vagina_depth']
        elif key == 'strength':
            value = data[uid]['strength']
            value += Utils.vampire(uid)
        elif key == 'constitution':
            value = data[uid]['constitution']
            value += Utils.vampire(uid)
        elif key == 'technique':
            value = data[uid]['technique']
            value += Utils.vampire(uid)
            if (i := Utils.get_skill(uid,12)) and Utils.is_night():
                value += -20 * i[2]
        elif key == 'volition':
            value = data[uid]['volition']
            value += Utils.vampire(uid)
            if (i := Utils.get_skill(uid,12)) and Utils.is_night():
                value += -20 * i[2]
        elif key == 'intelligence':
            value = data[uid]['intelligence']
        elif key == 'charm':
            value = data[uid]['charm']
        if value < 0:
            value = 0
        return [round(value, 2),b]

    async def get_attack_list(uid: str,target: str):
        """获取用户对目标造成的伤害

        Args:
            uid (str): 用户id
            target (str): 目标id

        Returns:
            list: 伤害列表
        """
        
        await Utils.refresh_data(uid)
        await Utils.refresh_data(target)
        atk = [[Utils.get_value(uid,'technique')[0],f"{data[uid]['name']}：技巧",False]]
        if Utils.get_state(uid,4):
            extra = int(Utils.get_value(target,"hp")[0] * 0.1)
            if extra > 0:
                atk.append([extra,f"{data[uid]['name']}：榨精心得",True])
            data[uid]["state"] = [s for s in data[uid]["state"] if s[0] != 4]
            DHandles.file_save()
        if i := Utils.get_skill(uid,2):
            atk.append([20 * sqrt(i[2]),f"{data[uid]['name']}：猫化",False])
        if i := Utils.get_skill(uid,3):
            atk.append([Utils.get_value(uid,'intelligence')[0] / 3 * sqrt(i[2]),f"{data[uid]['name']}：自然之心",False])
        if i := Utils.get_skill(uid,5):
            atk.append([50 * sqrt(i[2]),f"{data[uid]['name']}：淫纹",False])
        if i := Utils.get_state(uid,3):
            atk.append([30 * sqrt(i[2]),f"{data[uid]['name']}：伟哥",False])
        if i := Utils.get_skill(uid,11):
            atk.append([60 * i[2],f"{data[uid]['name']}：亡命疯徒",False])
        if i := Utils.get_skill(target,11):
            atk.append([60 * i[2],f"{data[target]['name']}：亡命疯徒",False])
        if i := Utils.get_skill(target,14):
            atk.append([50 * i[2],f"{data[target]['name']}：敏感",False])
        if i := Utils.get_skill(target,15):
            if Utils.dice(100,i[2] * 15) < 30:
                atk.append([300,f"{data[target]['name']}：弱点",True])
        
        if i := Utils.get_skill(target,2):
            atk.append([-20 * sqrt(i[2]),f"{data[target]['name']}：猫化",False])
        if i := Utils.get_skill(target,3):
            atk.append([-Utils.get_value(target,'intelligence')[0] / 3 * sqrt(i[2]),f"{data[target]['name']}：自然之心",False])
        if i := Utils.get_skill(target,4):
            atk.append([-50 * sqrt(i[2]),f"{data[target]['name']}：圣体",False])
        if i := Utils.get_skill(uid,10):
            atk.append([-50 * i[2],f"{data[uid]['name']}：呓语",False])
        return atk
    
    def reduce_hp(uid: str,hp: int):
        """减少hp并返回描述文本

        Args:
            uid (str): 用户id
            hp (int): 减少的hp

        Returns:
            str: 若有高潮/失神/昏迷，则返回相关描述文本
        """
        
        str = ""
        if not Utils.get_state(uid,1):
            DHandles.data_set(uid,'hp_v',(int)(Utils.get_value(uid,"hp")[0] - hp))
            if data[uid]['hp_v'] <= 0:
                d = Utils.dice(100,(int)(uid) ^ 10)
                str += f"\n{data[uid]['name']}高潮了！\n意志检定：1d100 = {d}"
                if d >= data[uid]['volition']:
                    DHandles.data_set(uid,'hp_v',0)
                    d = min(Utils.dice(30,(int)(uid) ^ 11), 30)
                    DHandles.state_refresh(uid,1,time() + d * 60)
                    DHandles.achievement_set(uid,"A03")
                    str += f" >= {data[uid]['volition']}\n{data[uid]['name']}失神了！失神状态将持续1d30 = {d}分钟。（期间无法行动，技能失效。如果失神期间受到攻击，失神状态将延长一分钟。）"
                else:
                    d = Utils.dice(data[uid]['volition'],(int)(uid) ^ 12)
                    DHandles.data_set(uid,'hp_v',(d + 10) * 5)
                    str += f" < {data[uid]['volition']}\n{data[uid]['name']}的意志HP回复至{data[uid]['hp_v']}"
        else:
            DHandles.data_set(uid,'hp_c',(int)(Utils.get_value(uid,"hp")[0] - hp))
            DHandles.state_refresh(uid,1,Utils.get_state(uid,1)[1] + 60)
            if data[uid]['hp_c'] <= 0:
                d = Utils.dice(100,(int)(uid) ^ 13)
                str += f"\n{data[uid]['name']}高潮了！\n体质检定：1d100 = {d}"
                if d >= data[uid]['constitution']:
                    DHandles.data_set(uid,'hp_c',0)
                    d = min(Utils.dice(5,(int)(uid) ^ 14), 5)
                    DHandles.state_refresh(uid,2,time() + d * 3600)
                    DHandles.achievement_set(uid,"A04")
                    str += f" >= {data[uid]['constitution']}\n{data[uid]['name']}昏迷了！昏迷状态将持续1d5 = {d}小时。（期间无法行动，无法被透，技能失效。）"
                    if Utils.boat(uid):
                        DHandles.skill_refresh(uid,6,time() + 259200)
                        str += f"\n{data[uid]['name']}的舰装破损了！将进入三天的冷却。"
                else:
                    d = Utils.dice(data[uid]['constitution'],(int)(uid) ^ 15)
                    DHandles.data_set(uid,'hp_c',(d + 10) * 5)
                    str += f" < {data[uid]['constitution']}\n{data[uid]['name']}的体质HP回复至{data[uid]['hp_c']}"
        if str:
            str = "\n" + str
        return str
    
    async def operation_check(uid: str):
        """检测用户是否能够行动

        Args:
            uid (str): 用户id

        Returns:
            str: 不能行动的理由，可以行动时返回""
        """
        
        oc = ""
        await Utils.refresh_data(uid)
        if not Utils.last_operation_time_check(uid):
            oc += "你操作太快了！"
        if Utils.get_state(uid,1) and not Utils.get_skill(uid,9):
            oc += "你失神了！"
        if Utils.get_state(uid,2):
            oc += "你昏迷了！"
        if not oc:
            Utils.set_last_operation_time(uid)
        return oc
    
    def find_user_name(name: str):
        """从昵称查找至用户id

        Args:
            name (str): 银趴昵称

        Returns:
            str: 用户id，未找到时返回None
        """
        
        for i in data.keys():
            if data[i].get('name') == name:
                return i
        return None
    
    def get_regeneration_rate(uid: str):
        """获取hp自然恢复速度

        Args:
            uid (str): 用户id

        Returns:
            int: 每分钟自然恢复hp
        """
        
        rr = 1
        if i := Utils.get_skill(uid,8):
            rr += 5 * i[2]
        if i := Utils.get_skill(uid,13):
            rr += -5 * i[2]
        if rr < 0:
            rr = 0
        return rr
    
    D10_ATTR_KEYS = ("penis_length","vagina_depth","strength","constitution","technique","volition","intelligence","charm")
    D10_CAP = 50
    D10_CAP_MONEY = 500000

    def d10_apply(uid: str,key: str,delta):
        """按 D10 属性预算池规则应用属性增减并持久化预算池

        Args:
            uid (str): 用户id
            key (str): 属性键
            delta (float): 变更量（正数为加、负数为减）

        Returns:
            float: 实际应用的变更量
        """
        
        if key == "money":
            cap = Utils.D10_CAP_MONEY
        else:
            cap = Utils.D10_CAP
        d10_used = data[uid].get("d10_used")
        if not isinstance(d10_used, dict):
            d10_used = {}
        used = d10_used.get(key, 0)
        if delta > 0:
            actual = min(delta, cap - used)
            if actual < 0:
                actual = 0
        else:
            actual = delta
        d10_used[key] = max(0, used + actual)
        DHandles.data_set(uid,"d10_used",d10_used)
        return actual
    
    async def gain_item(uid: str,id: int):
        """用户获得物品

        Args:
            uid (str): 用户id
            id (int): 物品id

        Returns:
            str: 描述文本
        """
        
        str = ''
        str += f"你获得了物品：{dicts.shop_dict[id]}\n"
        if id == 1:
            str += DHandles.state_refresh(uid,3,time() + 3600,level = 1,mode = 'add')
        elif id == 2:
            DHandles.data_set(uid,'penis_length',data[uid]['penis_length'] + 2)
            DHandles.data_set(uid,'vagina_depth',data[uid]['vagina_depth'] + 2)
            str += "长度增加了2cm，深度增加了2cm\n"
        elif id == 3:
            hp = Utils.get_value(uid,"hp")
            if hp[1]:
                DHandles.data_set(uid,"hp_c",data[uid]["hp_c"] + 100)
                str += "体质HP增加了100\n"
            else:
                DHandles.data_set(uid,"hp_v",data[uid]["hp_v"] + 100)
                str += "意志HP增加了100\n"
        elif id == 4:
            str += DHandles.skill_refresh(uid,2,level = 1,mode = 'add')
        elif id == 5:
            str += DHandles.skill_refresh(uid,3,level = 1,mode = 'add')
        elif id == 6:
            str += DHandles.skill_refresh(uid,4,level = 1,mode = 'add')
        elif id == 7:
            str += DHandles.skill_refresh(uid,5,level = 1,mode = 'add')
        elif id == 8:
            str += DHandles.skill_refresh(uid,6,level = 1,mode = 'add')
        elif id == 9:
            str += DHandles.skill_refresh(uid,7,level = 1,mode = 'add')
        elif id == 10:
            str += DHandles.skill_refresh(uid,8,level = 1,mode = 'add')
        elif id == 11:
            if Utils.get_skill(uid,9):
                str += "你已经拥有屹立不倒，不能重复购买。\n"
                return str
            str += DHandles.skill_refresh(uid,9,level = 1,mode = 'add')
            DHandles.achievement_set(uid,"D04")
        elif id == 12:
            data[uid]["skill"] = [i for i in data[uid]["skill"] if i[0] not in [10,11,12,13,14,15,]]
            str += "已清除所有诅咒"
        elif id == 13:
            d = Utils.dice(10,13)
            pool = [i for i in range(2,16)]
            if Utils.get_skill(uid,9):
                pool.remove(9)
            sk = choice(pool)
            str += f"1d10 = {d}\n"
            str += DHandles.skill_refresh(uid,sk,level = 5 + d,mode = 'add')
            DHandles.data_set(uid,'pandora_count',data[uid].get('pandora_count',0) + 1)
        elif id == 14:
            DHandles.data_set(uid,'d10_count',data[uid].get('d10_count',0) + 1)
            d = Utils.dice(10,13)
            str += f"1d10 = {d}"
            if d == 1:
                d = Utils.dice(10,131)
                actual = Utils.d10_apply(uid,'penis_length',d * 0.1)
                new_value = round(data[uid]['penis_length'] + actual, 2)
                str += f"1d10 = {d}\n长度：{data[uid]['penis_length']} → {new_value}"
                if actual < d * 0.1:
                    str += "（已达D10预算上限）"
                DHandles.data_set(uid,'penis_length',new_value)
            elif d == 2:
                d = Utils.dice(10,132)
                actual = Utils.d10_apply(uid,'vagina_depth',d * 0.1)
                new_value = round(data[uid]['vagina_depth'] + actual, 2)
                str += f"1d10 = {d}\n深度：{data[uid]['vagina_depth']} → {new_value}"
                if actual < d * 0.1:
                    str += "（已达D10预算上限）"
                DHandles.data_set(uid,'vagina_depth',new_value)
            elif d == 3:
                d = Utils.dice(10,133)
                actual = Utils.d10_apply(uid,'strength',d)
                new_value = data[uid]['strength'] + actual
                str += f"1d10 = {d}\n力量：{data[uid]['strength']} → {new_value}"
                if actual < d:
                    str += "（已达D10预算上限）"
                DHandles.data_set(uid,'strength',new_value)
            elif d == 4:
                d = Utils.dice(10,134)
                actual = Utils.d10_apply(uid,'constitution',d)
                new_value = min(data[uid]['constitution'] + actual, 90)
                str += f"1d10 = {d}\n体质：{data[uid]['constitution']} → {new_value}"
                if actual < d:
                    str += "（已达D10预算上限）"
                DHandles.data_set(uid,'constitution',new_value)
            elif d == 5:
                d = Utils.dice(10,135)
                actual = Utils.d10_apply(uid,'technique',d)
                new_value = data[uid]['technique'] + actual
                str += f"1d10 = {d}\n技巧：{data[uid]['technique']} → {new_value}"
                if actual < d:
                    str += "（已达D10预算上限）"
                DHandles.data_set(uid,'technique',new_value)
            elif d == 6:
                d = Utils.dice(10,136)
                actual = Utils.d10_apply(uid,'volition',d)
                new_value = min(data[uid]['volition'] + actual, 90)
                str += f"1d10 = {d}\n意志：{data[uid]['volition']} → {new_value}"
                if actual < d:
                    str += "（已达D10预算上限）"
                DHandles.data_set(uid,'volition',new_value)
            elif d == 7:
                d = Utils.dice(10,137)
                actual = Utils.d10_apply(uid,'intelligence',d)
                new_value = data[uid]['intelligence'] + actual
                str += f"1d10 = {d}\n智力：{data[uid]['intelligence']} → {new_value}"
                if actual < d:
                    str += "（已达D10预算上限）"
                DHandles.data_set(uid,'intelligence',new_value)
            elif d == 8:
                d = Utils.dice(10,138)
                actual = Utils.d10_apply(uid,'charm',d)
                new_value = data[uid]['charm'] + actual
                str += f"1d10 = {d}\n魅力：{data[uid]['charm']} → {new_value}"
                if actual < d:
                    str += "（已达D10预算上限）"
                DHandles.data_set(uid,'charm',new_value)
            elif d == 9:
                d = Utils.dice(10,139)
                actual = Utils.d10_apply(uid,'money',d * 1000)
                current_money = await Utils.get_money(uid)
                new_money = await Utils.add_money(uid, actual)
                str += f"1d10 = {d}\nYPD：{current_money} → {new_money}"
                if actual < d * 1000:
                    str += "（已达D10金钱预算上限）"
            elif d == 10:
                d = Utils.dice(2,1310)
                str += f"1d10 = {d}\n"
                si = 1
                if d == 1:
                    si = 1
                    str += "1d2 = 1（大成功）\n"
                    DHandles.achievement_set(uid,"C05")
                elif d == 2:
                    si = -1
                    str += "1d2 = 2（大失败）\n"
                    DHandles.achievement_set(uid,"C06")
                d = Utils.dice(9,1311)
                str += f"1d9 = {d}\n"
                if d == 1:
                    d = Utils.dice(100,131)
                    actual = Utils.d10_apply(uid,'penis_length',d * 0.1 * si)
                    new_value = round(data[uid]['penis_length'] + actual, 2)
                    str += f"1d100 = {d}\n长度：{data[uid]['penis_length']} → {new_value}"
                    DHandles.data_set(uid,'penis_length',new_value)
                elif d == 2:
                    d = Utils.dice(100,132)
                    actual = Utils.d10_apply(uid,'vagina_depth',d * 0.1 * si)
                    new_value = round(data[uid]['vagina_depth'] + actual, 2)
                    str += f"1d100 = {d}\n深度：{data[uid]['vagina_depth']} → {new_value}"
                    DHandles.data_set(uid,'vagina_depth',new_value)
                elif d == 3:
                    d = Utils.dice(100,133)
                    actual = Utils.d10_apply(uid,'strength',d * si)
                    new_value = data[uid]['strength'] + actual
                    str += f"1d100 = {d}\n力量：{data[uid]['strength']} → {new_value}"
                    DHandles.data_set(uid,'strength',new_value)
                elif d == 4:
                    d = Utils.dice(100,134)
                    actual = Utils.d10_apply(uid,'constitution',d * si)
                    new_value = min(data[uid]['constitution'] + actual, 90)
                    str += f"1d100 = {d}\n体质：{data[uid]['constitution']} → {new_value}"
                    DHandles.data_set(uid,'constitution',new_value)
                elif d == 5:
                    d = Utils.dice(100,135)
                    actual = Utils.d10_apply(uid,'technique',d * si)
                    new_value = data[uid]['technique'] + actual
                    str += f"1d100 = {d}\n技巧：{data[uid]['technique']} → {new_value}"
                    DHandles.data_set(uid,'technique',new_value)
                elif d == 6:
                    d = Utils.dice(100,136)
                    actual = Utils.d10_apply(uid,'volition',d * si)
                    new_value = min(data[uid]['volition'] + actual, 90)
                    str += f"1d100 = {d}\n意志：{data[uid]['volition']} → {new_value}"
                    DHandles.data_set(uid,'volition',new_value)
                elif d == 7:
                    d = Utils.dice(100,137)
                    actual = Utils.d10_apply(uid,'intelligence',d * si)
                    new_value = data[uid]['intelligence'] + actual
                    str += f"1d100 = {d}\n智力：{data[uid]['intelligence']} → {new_value}"
                    DHandles.data_set(uid,'intelligence',new_value)
                elif d == 8:
                    d = Utils.dice(100,138)
                    actual = Utils.d10_apply(uid,'charm',d * si)
                    new_value = data[uid]['charm'] + actual
                    str += f"1d100 = {d}\n魅力：{data[uid]['charm']} → {new_value}"
                    DHandles.data_set(uid,'charm',new_value)
                elif d == 9:
                    d = Utils.dice(100,139)
                    actual = Utils.d10_apply(uid,'money',d * 1000 * si)
                    current_money = await Utils.get_money(uid)
                    new_money = await Utils.add_money(uid, actual)
                    str += f"1d100 = {d}\nYPD：{current_money} → {new_money}"
        return str
    
    async def get_group_yinpa_list(bid: str,gid: int):
        """获取群内加入银趴的成员

        Args:
            bid (str): bot的id
            gid (int): 群的id

        Returns:
            list: 一个由群员id组成的列表
        """
        bot = get_bots()[bid]
        gmdlist = await bot.call_api('get_group_member_list',group_id = gid)
        gymlist = []
        for i in gmdlist:
            if data.get(i["user_id"]):
                gymlist.append(i["user_id"])
        return gymlist
    
    # def draw_rank_image(gid: int,uid: str,bid: str,mode = ""):
    #     gymlist = Utils.get_group_yinpa_list(bid,gid)
        
        
    #     image = Image.new("RGB",(512,1024),(255,255,255))
    #     draw = ImageDraw.Draw(image)
    #     linewidth = 24
    #     for k in range(2):
    #         for j in range(2):
    #             tx = 28 + j * 256
    #             ty = 28 + k * 512
    #             for i in range(20):
    #                 draw.line([(tx,ty + i * linewidth),(tx + 200,ty + i * linewidth)],(0,0,0),1)
    #                 draw.line([(tx,ty + 512 + i * linewidth),(tx + 200,ty + 512 + i * linewidth)],(0,0,0),1)
    #             for i in range(2):
    #                 draw.line([(tx,ty + i * 512),(tx,ty + 456 + i * 512)],(0,0,0),1)
    #                 draw.line([(tx + 100,ty + i * 512 + linewidth),(tx + 100,ty + 456 + i * 512)],(0,0,0),1)
    #                 draw.line([(tx + 200,ty + i * 512),(tx + 200,ty + 456 + i * 512)],(0,0,0),1)
    #     img = image.convert("RGB")
    #     img_byte = BytesIO()
    #     img.save(img_byte,"PNG")
    #     return img_byte.getvalue()