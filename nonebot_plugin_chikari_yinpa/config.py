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
    """初始金钱。默认：100"""
<<<<<<< HEAD
    chikari_yinpa_font:Path = Path(__file__).parent / "resource" / "SourceHanSansSC-VF.ttf"
    """绘图所用字体。默认：'模块路径/resource/SourceHanSansSC-VF.ttf'"""
=======
    chikari_yinpa_transfer_unlock_money: Optional[int] = 10000
    """转账功能解锁所需金钱。默认：10000"""
    chikari_yinpa_transfer_cooldown: Optional[int] = 3600
    """转账冷却时间（秒）。默认：3600（1小时）"""
    chikari_yinpa_font:Path = Path(__file__).parent / "resource" / "NotoSerifCJKsc-VF.ttf"
    """绘图所用主字体。默认：'模块路径/resource/NotoSerifCJKsc-VF.ttf'"""
    chikari_yinpa_emoji_font:Path = Path(__file__).parent / "resource" / "NotoEmoji.ttf"
    """绘图所用 Emoji 字体。默认：'模块路径/resource/NotoEmoji.ttf'"""
>>>>>>> cc0ceec (v1.5.0 将字体换成了CJK字体，额外加了Emoji字体)
