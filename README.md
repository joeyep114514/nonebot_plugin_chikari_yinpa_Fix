<div align="center">
    <a href="https://v2.nonebot.dev/store">
        <img src="./image/NoneBotPlugin.svg" width="300" alt="logo">
    </a>

# nonebot-plugin-chikari-yinpa-fix

_✨ NoneBot 一个普通的银趴插件（修复版）✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/joeyep114514/nonebot_plugin_chikari_yinpa_Fix" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-chikari-yinpa-fix">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-chikari-yinpa-fix.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>


## 📖 介绍

### 警告：本插件包含NSFW内容！
### 原作者称由于学业问题，源项目更新放缓，但源项目实际已进入半停更状态
这是一个基于NoneBot 2的银趴插件，由于源项目年久失修，本项目在源项目的基础上进行了修复、完善以及多次平衡性调整，使其可供正常游玩

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-chikari-yinpa-fix

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-chikari-yinpa-fix
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-chikari-yinpa-fix
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-chikari-yinpa-fix
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-chikari-yinpa-fix
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_chikari_yinpa"]

</details>
## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| chikari_yinpa_initial_sex_value | 否 | 50 | 目前无作用 |
| chikari_yinpa_initial_penis_length | 否 | 10 | 初始长度 |
| chikari_yinpa_initial_vagina_depth | 否 | 10 | 初始深度 |
| chikari_yinpa_initial_money | 否 | 100 | 初始金钱 |
| chikari_yinpa_transfer_unlock_money | 否 | 10000 | 转账功能解锁所需金钱 |
| chikari_yinpa_transfer_cooldown | 否 | 3600 | 转账冷却时间（秒，默认1小时） |
| chikari_yinpa_font | 否 | Path(__file__).parent / "resource" / "NotoSansCJK-Regular.ttc" | 绘图所用 Noto Sans CJK 主字体 |
| chikari_yinpa_emoji_font | 否 | Path(__file__).parent / "resource" / "NotoEmoji.ttf" | 绘图所用黑白 Noto Emoji 字体 |

## 🎉 使用
### 指令表
#### help指令中的提示以"/"为指令前缀，可根据实际情况自行修改
#### 部分指令存在别名，可在help指令中查询
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| yinpa_control | 主人/群主/管理员 | 否 | 群聊 | 控制本群银趴的开启/关闭 |
| help | 无 | 否 | 私聊/群聊 | 查询Chikari_Yinpa_Fix的帮助 |
| sign_in | 无 | 否 | 私聊/群聊 | 每日打卡，每天可使用一次，增加长度、深度、金钱 |
| yinpa_join | 无 | 否 | 私聊/群聊 | 加入银趴！ |
| yinpa_leave | 无 | 否 | 私聊/群聊 | 离开银趴！ |
| info | 无 | 否 | 私聊/群聊 | 查询自己或某人的银趴信息 |
| tou | 无 | 否 | 私聊/群聊 | 透某人 |
| zha | 无 | 否 | 私聊/群聊 | 榨某人 |
| chong | 无 | 否 | 私聊/群聊 | 冲一发，能够增加或减少一定长度 |
| kou | 无 | 否 | 私聊/群聊 | 扣一次，能够增加少量深度 |
| shop | 无 | 否 | 私聊/群聊 | 花费金钱购买商品 |
| work | 无 | 否 | 私聊/群聊 | 工作，获得金钱及其他东西 |
| transfer | 无 | 否 | 私聊/群聊 | 转账给他人（余额满 10000 YPD 解锁，冷却 1 小时） |

## 🔭 TODO

### 如果有什么好的想法，欢迎提交[issue](https://github.com/joeyep114514/nonebot_plugin_chikari_yinpa_Fix/issues)或[pr](https://github.com/joeyep114514/nonebot_plugin_chikari_yinpa_Fix/pulls)

- [x] 将经济相关拆分为单独的插件，未来可与其他插件互通

- [ ] 排名功能（群榜，总榜）

- [ ] 誓约系统

- [x] 成就系统

- [ ] bot随机自主出击

- [x] 单独的钓鱼插件

## 📝 更新日志

### v2.0.3

- 修复转账无冷却的问题：新增转账冷却（默认 1 小时，`chikari_yinpa_transfer_cooldown` 可调）
- 转账功能补上解锁门槛：余额达到 10000 YPD（`chikari_yinpa_transfer_unlock_money`）才可使用
- 帮助与 README 补齐转账指令说明

### v2.0.2

- 长消息（PVP 结果、商店/工作列表、帮助等）渲染为图片发送，短消息保持纯文本
- 数值展示与计算统一四舍五入保留两位小数
- 新增新手引导式主帮助（/yinpa_help），完善工作/商店/D10 说明

### v2.0.0

- 平衡性调整：工作系统、吸血鬼、D10 预算池、成就系统
- 适配独立钓鱼插件，成就/统计互通

## 🥳 预览图

（已过时）

![image](image/img_1.png)
