from pydantic import BaseModel
from typing import Optional
from pathlib import Path

class Config(BaseModel):
    chikari_yinpa_initial_sex_value: Optional[int] = 50
    """初始性别倾向。默认：50"""
    chikari_yinpa_initial_penis_length: Optional[int] = 10
    """初始长度。默认：10"""
    chikari_yinpa_initial_vagina_depth: Optional[int] = 10
    """初始深度。默认：10"""
    chikari_yinpa_initial_money: Optional[int] = 100
    """初始 YPD。默认：100"""
    chikari_yinpa_initial_free_points: Optional[int] = 180
    """普通种族初始自由属性点。默认：180"""
    chikari_yinpa_human_bonus_points: Optional[int] = 40
    """人类额外自由属性点（人类 = 180 + 40 = 220）。默认：40"""
    chikari_yinpa_constitution_volition_ratio: Optional[int] = 2
    """体质/意志兑换率（每 2 点换 1 属性）。默认：2"""
    chikari_yinpa_join_timeout: Optional[int] = 600
    """加入银趴创建流程超时时间（秒）。默认：600"""
    chikari_yinpa_transfer_unlock_money: Optional[int] = 10000
    """转账功能解锁所需 YPD。默认：10000"""
    chikari_yinpa_transfer_cooldown: Optional[int] = 3600
    """转账冷却时间（秒）。默认：3600（1小时）"""
    chikari_yinpa_font:Path = Path(__file__).parent / "resource" / "NotoSansCJKsc-VF.ttf"
    """绘图所用主字体。默认：'模块路径/resource/NotoSansCJKsc-VF.ttf'"""
    chikari_yinpa_emoji_font:Path = Path(__file__).parent / "resource" / "NotoEmoji.ttf"
    """绘图所用 Emoji 字体。默认：'模块路径/resource/NotoEmoji.ttf'"""
