import json
import os

from pathlib import Path
from time import time
from .dicts import dicts
from .config import Config
try:
    from nonebot import get_plugin_config
except Exception:
    def get_plugin_config(cls):
        return cls()

def _get_plugin_config():
    try:
        return get_plugin_config(Config)
    except Exception:
        return Config()
try:
    import nonebot_plugin_localstore as store
except ImportError:
    class _FallbackStore:
        @staticmethod
        def get_plugin_data_file(filename):
            base = Path(__file__).resolve().parent / "data"
            base.mkdir(parents=True, exist_ok=True)
            return base / filename

        @staticmethod
        def get_plugin_config_file(filename):
            base = Path(__file__).resolve().parent / "data"
            base.mkdir(parents=True, exist_ok=True)
            return base / filename
    store = _FallbackStore()

plugin_data_file: Path = store.get_plugin_data_file("data.json")
plugin_config_file: Path = store.get_plugin_config_file("config.json")
plugin_data_file.parent.mkdir(parents=True, exist_ok=True)
plugin_config_file.parent.mkdir(parents=True, exist_ok=True)

def _load_json_with_recovery(path: Path, default_factory):
    """加载数据文件；若文件损坏（写入中途崩溃等），备份后重置，避免插件整体加载失败

    Args:
        path (Path): 数据文件路径
        default_factory: 生成默认数据的工厂

    Returns:
        dict: 加载（或重置）后的数据
    """
    try:
        return json.loads(path.read_text(encoding='utf-8'), strict=False)
    except ValueError:
        backup = path.parent / (path.name + f".corrupt.{int(time())}")
        path.replace(backup)
        print(f"[Chikari_Yinpa] 数据文件损坏，已备份至 {backup} 并重置为默认数据")
        return default_factory()

#用户数据文件初始化及载入

if not plugin_data_file.exists() or plugin_data_file.stat().st_size == 0:
    init_data = {}
    plugin_data_file.write_text(json.dumps(init_data, indent=4, ensure_ascii=False), encoding='utf-8')
    data = init_data
else:
    data = _load_json_with_recovery(plugin_data_file, dict)

if "_work_cooldown" not in data or not isinstance(data["_work_cooldown"], dict):
    data["_work_cooldown"] = {}

# 数据迁移：旧版本用户数据缺少 skill 字段，统一补齐为空列表，
# 避免升级后 refresh_data / get_skill / skill_refresh 等直接索引崩溃
# 注意：跳过 _ 前缀的内部字段（_work_cooldown 也是 dict，但不是用户记录）
_skill_migrated = False
for _uid, _ud in data.items():
    if _uid.startswith("_"):
        continue
    if isinstance(_ud, dict) and "skill" not in _ud:
        _ud["skill"] = []
        _skill_migrated = True
if _skill_migrated:
    _tmp = plugin_data_file.parent / (plugin_data_file.name + ".tmp")
    with open(_tmp, 'w', encoding='utf-8') as _f:
        json.dump(data, _f, indent=4, ensure_ascii=False)
    os.replace(_tmp, plugin_data_file)
    print(f"[Chikari_Yinpa] 已为存量用户数据补齐 skill 字段并写回文件")

#配置数据文件初始化及载入

if not plugin_config_file.exists() or plugin_config_file.stat().st_size == 0:
    init_data = {
        "yinpa_enabled_group":[],
    }
    plugin_config_file.write_text(json.dumps(init_data, indent=4, ensure_ascii=False), encoding='utf-8')
    configdata = init_data
else:
    configdata = _load_json_with_recovery(plugin_config_file, lambda: {"yinpa_enabled_group":[]})
    if not isinstance(configdata.get("yinpa_enabled_group"), list):
        configdata["yinpa_enabled_group"] = []


def _ship_hp_bonus(uid: str):
    """舰装血量上限加成 100×√(等级)（舰装未破损时生效）

    Args:
        uid (str): 用户id

    Returns:
        int: 舰装血量上限加成
    """
    
    from math import sqrt
    for i in data.get(uid, {}).get("skill", []):
        if i[0] == 6:
            cooldown = i[1]
            if cooldown is None or cooldown <= time():
                return int(100 * sqrt(i[2]))
            break
    return 0


class DHandles():
    """数据处理"""
    
    def file_save():
        """将内存中的数据保存至文件（临时文件 + 原子替换，避免写入中途崩溃损坏数据文件）
        """
        
        global data
        global configdata
        for path, payload in ((plugin_data_file, data), (plugin_config_file, configdata)):
            tmp = path.parent / (path.name + ".tmp")
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=4, ensure_ascii=False)
            os.replace(tmp, path)

    def data_set(uid: str,key: str,value):
        """设置特定用户的特定数值

        Args:
            uid (str): 用户id
            key (str): 数据键值
            value (_type_): 数据
        """
        
        global data
        data[uid][key] = value
        DHandles.file_save()
        return
    
    def configdata_set(key: str,value):
        """设置配置文件

        Args:
            key (str): 配置键值
            value (_type_): 数据
        """
        
        global configdata
        configdata[key] = value
        DHandles.file_save()
        return
    
    def group_remove(group_id: int):
        """将群组移出银趴

        Args:
            group_id (int): 群组id
        """
        
        global configdata
        configdata["yinpa_enabled_group"].remove(group_id)
        DHandles.file_save()
        return
    
    def user_add(uid: str,dict: dict):
        """将用户加入银趴

        Args:
            uid (str): 用户id
            dict (dict): 用户初始数据
        """
        
        global data
        data[uid] = dict
        data[uid]["hp_v"] = int((data[uid]["volition"] + 10) * 5) + _ship_hp_bonus(uid)
        data[uid]["hp_c"] = int((data[uid]["constitution"] + 10) * 10) + _ship_hp_bonus(uid)
        DHandles.file_save()
        return

    def user_add_with_points(uid: str,name: str,species: int,pts: list):
        """按种族模板 + 自由属性点创建角色

        Args:
            uid (str): 用户id
            name (str): 昵称
            species (int): 种族id
            pts (list): 六项自由点投入 [力量, 体质, 技巧, 意志, 智力, 魅力]
        """
        
        spec = dicts.species_initial_ability[species]
        rate = dicts.attribute_order["rate"]
        keys = dicts.attribute_order["keys"]
        final = {}
        for i in range(6):
            inc = int(pts[i] * rate[i])  # 体质/意志 2:1（配合偶数校验后无小数）
            total = spec["base"][i] + inc
            # cap 为 None 表示该属性无上限（力量/技巧/智力/魅力），仅体质/意志封顶 80
            final[keys[i]] = total if spec["cap"][i] is None else min(total, spec["cap"][i])
        plugin_config = _get_plugin_config()
        global data
        data[uid] = {
            'name':name,
            'species':species,
            'sex_value':plugin_config.chikari_yinpa_initial_sex_value,
            'penis_length':plugin_config.chikari_yinpa_initial_penis_length,
            'vagina_depth':plugin_config.chikari_yinpa_initial_vagina_depth,
            'strength':final["strength"],
            'constitution':final["constitution"],
            'technique':final["technique"],
            'volition':final["volition"],
            'intelligence':final["intelligence"],
            'charm':final["charm"],
            'state':[],
            'skill':[],
            "passive_times":0,
            "active_times":0,
            "last_sign_in_time":0,
            "last_operation_time":0,
            "last_refresh_time":time(),
            "next_work_time":0,
            "achievements":[],
            "d10_used":{},
            "brick_count":0,
            "live_bonus":False,
            "last_live_time":0,
            "live_broken":False,
            "work_count":0,
            "sign_in_count":0,
            "d10_count":0,
            "pandora_count":0,
            "explore_count":0,
        }
        data[uid]["hp_v"] = int((data[uid]["volition"] + 10) * 5) + _ship_hp_bonus(uid)
        data[uid]["hp_c"] = int((data[uid]["constitution"] + 10) * 10) + _ship_hp_bonus(uid)
        DHandles.file_save()
        return
        
    def user_remove(uid: str):
        """将用户移出银趴

        Args:
            uid (str): 用户id
        """
        
        global data
        del data[uid]
        DHandles.file_save()
        return
    
    def work_cooldown_get(uid: str):
        """读取用户独立的工作冷却结束时间（跨注销保留）

        Args:
            uid (str): 用户id

        Returns:
            int: 下次可工作的时间戳，无记录时为 0
        """
        
        global data
        if "_work_cooldown" not in data or not isinstance(data["_work_cooldown"], dict):
            data["_work_cooldown"] = {}
        return data["_work_cooldown"].get(uid, 0)
    
    def work_cooldown_set(uid: str,value):
        """写入用户独立的工作冷却结束时间（跨注销保留）

        Args:
            uid (str): 用户id
            value (int): 下次可工作的时间戳
        """
        
        global data
        if "_work_cooldown" not in data or not isinstance(data["_work_cooldown"], dict):
            data["_work_cooldown"] = {}
        data["_work_cooldown"][uid] = value
        DHandles.file_save()
        return
    
    def skill_refresh(uid: str,id: int,value = None,level: int = 1,mode: str = ''):
        """更新技能

        Args:
            uid (str): 用户id
            id (int): 技能id
            value (_type_, optional): 技能附加数据
            level (int): 技能等级
            mode (str): 若为'add'则为增加等级，否则为修改等级（如果未拥有该技能，则固定为修改等级）

        Returns:
            str: 描述文本
        """
        
        global data
        b = False
        # setdefault 保证原地修改（append/remove）作用于 data 中的真实列表
        skills = data[uid].setdefault("skill", [])
        if id == 9:
            level = 1
            mode = ''
        for i in list(skills):
            if i[0] == id:
                i[1] = value
                if len(i) >= 3:
                    if mode == 'add':
                        level += i[2]
                    i[2] = level
                else:
                    i.insert(2,level)
                b = True
                break
            if i[2] <= 0:
                skills.remove(i)
        if not b:
            skills.append([id,value,level])
        return f"获得技能：{dicts.skill_dict[id]}（等级：{level}）（ID：{id}）\n"
    
    def state_refresh(uid: str,id: int,value = time(),level: int = 1,mode: str = ''):
        """更新状态

        Args:
            uid (str): 用户id
            id (int): 状态id
            value (_type_, optional): 状态结束时间
            level (int): 状态等级
            mode (str): 若为'add'则为增加等级，否则为修改等级（如果未拥有该状态，则固定为修改等级）

        Returns:
            str: 描述文本
        """
        
        global data
        b = False
        for i in range(len(data[uid]["state"])):
            if data[uid]["state"][i][0] == id:
                data[uid]["state"][i][1] = value
                if len(data[uid]["state"][i]) >= 3:
                    if mode == 'add':
                        level += data[uid]["state"][i][2]
                    data[uid]["state"][i][2] = level
                else:
                    data[uid]["state"][i].insert(2,level)
                if data[uid]["state"][i][2] <= 0:
                    del data[uid]["state"][i]
                b = True
                break
        if not b:
            data[uid]["state"].append([id,value,level])
        return f"获得状态：{dicts.state_dict[id]}（等级：{level}）（ID：{id}）（持续时间：{(int)(value - time())}秒）\n"

    def achievement_set(uid: str,aid: str):
        """写入成就（去重）

        Args:
            uid (str): 用户id
            aid (str): 成就id
        """
        
        global data
        achievements = data[uid].get("achievements")
        if not isinstance(achievements, list):
            achievements = []
        if aid not in achievements:
            achievements.append(aid)
            data[uid]["achievements"] = achievements
            DHandles.file_save()
        return
