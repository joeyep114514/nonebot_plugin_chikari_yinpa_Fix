<div align="center">
    <a href="https://v2.nonebot.dev/store">
        <img src="./image/NoneBotPlugin.svg" width="300" alt="logo">
    </a>

# nonebot-plugin-chikari-yinpa-fix

_✨ 一个基于 NoneBot2 的银趴插件（修复版）✨_

<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/joeyep114514/nonebot_plugin_chikari_yinpa_Fix" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-chikari-yinpa-fix">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-chikari-yinpa-fix.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

**当前版本：2.1.8**

</div>

> [!WARNING]
> 本插件包含 NSFW 内容，应仅在合适的群聊/环境中部署。源项目已进入半停更状态，本仓库在其基础上做修复、平衡性调整与功能维护。

## 简介

本项目是 `nonebot-plugin-chikari-yinpa-fix`，面向 QQ 群聊的 OneBot v11 角色扮演/养成插件。玩家通过签到、打工、商店、对战等指令积累 YPD 与属性，解锁技能和成就。所有长文本反馈统一由 Pillow 渲染为图片发送，避免群聊刷屏。

设计目标：

- **可配置**：初始属性、金钱、字体、图片宽度等通过 NoneBot 配置注入。
- **可扩展**：种族、技能、状态、商品、工作全部集中在 `dicts.py`，新增内容改动面小。
- **可维护**：JSON 原子写入、启动时数据迁移、失败恢复、防御式读取。

## 功能概览

| 模块 | 说明 |
|---|---|
| 角色创建 | 昵称 → 种族 → 自由属性点三步流程，支持随机种族/随机加点 |
| 日常 | 签到、打工（搬砖/援交/直播/写文/打架/探险）、转账 |
| 对战 | 透、榨、冲、扣，结算意志/体质 HP、状态与技能效果 |
| 商店 | 伟哥、技能书、D10、转生苹果等 15 件商品；每条商品带简述 |
| 成长 | 技能升级、状态、D10 属性预算池、24 项成就 |
| 转生 | 购买【转生苹果】二次确认后重选种族、重配属性，保留金钱与成就 |
| 渲染 | 长消息/信息图/商店/帮助自动折行渲染，宽度可配置 |

## 技术栈

- Python 3.9+
- [NoneBot2](https://v2.nonebot.dev/) + `nonebot-adapter-onebot` (OneBot v11)
- Pillow（文本转图片）
- `nonebot-plugin-localstore`、`nonebot-plugin-value`、`nonebot-plugin-orm`
- 可选：`nonebot-plugin-fishing2`（钓鱼成就/统计互通）

## 项目结构

```text
nonebot_plugin_chikari_yinpa/
├── __init__.py       # 插件元数据、matcher 注册、启动钩子
├── config.py         # Pydantic 配置模型
├── data_handles.py   # JSON 持久化、原子写入、数据迁移、用户增删改
├── dicts.py          # 种族/技能/状态/商品/工作/成就常量
├── handles.py        # 指令处理器与交互流程
├── utils.py          # 属性计算、随机检定、图片渲染
└── resource/         # Noto 字体（主字体与 Emoji 字体）
```

运行时数据（`data.json` / `config.json`）由 `nonebot-plugin-localstore`
管理，默认不在插件包内；只有未安装 localstore 时才会回退到包内 `data/` 目录。

## 安装

### 作为 NoneBot 插件安装

```bash
# nb-cli
nb plugin install nonebot-plugin-chikari-yinpa-fix

# 或 pip
pip install nonebot-plugin-chikari-yinpa-fix
```

然后在 NoneBot 项目的 `pyproject.toml` 中启用：

```toml
[tool.nonebot]
plugins = ["nonebot_plugin_chikari_yinpa"]
```

### 从源码开发

```bash
git clone https://github.com/joeyep114514/nonebot_plugin_chikari_yinpa_Fix.git
cd nonebot_plugin_chikari_yinpa_Fix
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

本仓库只包含插件本体，不包含 NoneBot 入口。本地运行需要准备一个 NoneBot2 项目，将本仓库路径加入 `plugins`，或使用 `nb plugin install` 后以开发模式加载。

## 配置

配置项通过 NoneBot 项目的 `.env` / `.env.prod` 注入（均为可选项）：

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `chikari_yinpa_initial_sex_value` | `50` | 初始性别倾向，目前无实际作用 |
| `chikari_yinpa_initial_penis_length` | `10` | 初始长度 |
| `chikari_yinpa_initial_vagina_depth` | `10` | 初始深度 |
| `chikari_yinpa_initial_money` | `100` | 新建角色初始 YPD |
| `chikari_yinpa_initial_free_points` | `180` | 普通种族自由属性点 |
| `chikari_yinpa_human_bonus_points` | `40` | 人类额外自由属性点 |
| `chikari_yinpa_constitution_volition_ratio` | `2` | 体质/意志兑换率（每 2 点换 1 属性） |
| `chikari_yinpa_join_timeout` | `600` | 创建/转生流程超时时间（秒） |
| `chikari_yinpa_font` | `resource/NotoSansCJKsc-VF.ttf` | 主字体（可变字体，自动应用 Regular 字重） |
| `chikari_yinpa_emoji_font` | `resource/NotoEmoji.ttf` | 黑白 Emoji 字体 |
| `chikari_yinpa_image_max_width` | `600` | 图片最大宽度（px，含左右留白，范围 320–1600） |

## 指令

指令前缀以 NoneBot 配置为准，以下以 `/` 示意；部分指令有中文别名。

| 指令 | 权限 | 说明 |
|---|---|---|
| `/yinpa_control <enable/disable>` | 主人/群主/管理员 | 开启/关闭本群银趴 |
| `/yinpa_help [分类]`（别名 `银趴帮助`） | 所有人 | 查看帮助（新手指南/种族/技能/状态/工作/商店） |
| `/yinpa_join [昵称]` | 所有人 | 加入银趴（三步创建流程） |
| `/yinpa_leave [key]` | 所有人 | 离开银趴（二次确认 key） |
| `/sign_in` | 所有人 | 每日签到 |
| `/info [@某人]` | 所有人 | 查看自己/他人信息图 |
| `/tou` `/zha` `/chong` `/kou` | 所有人 | 互动与对战 |
| `/shop`（别名 `ypshop`/`银趴商店`） | 所有人 | 商店列表/购买 |
| `/work`（别名 `工作`/`打工`） | 所有人 | 打工赚钱 |
| `/transfer`（别名 `转账`） | 所有人 | 转账给他人 |

> `shop` 别名可能与钓鱼插件冲突；使用 `ypshop` 可避免。

## 维护与扩展

### 数据与持久化

- 用户数据与群开关由 `nonebot-plugin-localstore` 保存为 `data.json` / `config.json`，默认在系统用户数据目录下（具体路径由 localstore 决定）；未安装 localstore 时回退到插件包内 `data/`。
- 所有写入走 `DHandles.data_set` / `DHandles.file_save`，采用「临时文件 + `os.replace`」原子替换。
- 启动时会修复缺失的 `skill` 字段；JSON 损坏会备份为 `*.corrupt.<timestamp>` 后重置。
- 金钱通过 `nonebot-plugin-value` 的 `YPD` 货币账户单独存储，不在 `data.json` 中。
- 修改数据结构时，需在 `data_handles.py` 的启动迁移段补充兼容逻辑，避免存量用户升级崩溃。

### 图片渲染

所有长文本统一走 `Utils.text_to_image()`：

- 按配置的 `chikari_yinpa_image_max_width` 折行，画布宽度不会超过该值。
- 优先在 `、，。；：！？` 等标点后断行，续行带悬挂缩进，并处理行首禁则。
- 单行超过 2000 字或总行数超过 100 行会被截断（追加省略提示），用于防御超大图分配。
- 信息图由 `Utils.get_user_info_image()` 组装文本后复用同一渲染器。

新增图片消息直接调用 `MessageSegment.image(Utils.text_to_image(text))`，无需自行计算宽度。

### 扩展商店

新增商品通常涉及 `dicts.py` 的四处修改：

1. `shop_dict`：`id -> 商品名`
2. `shop_price_dict`：`id -> 价格`
3. `shop_help`：`商品名 -> 详细帮助文本`
4. `shop_brief_dict`：`id -> 商店列表中的一行简述`

随后在 `utils.py` 的 `Utils.gain_item()` 中增加 `elif id == ...` 分支。若商品需要交互（如转生苹果的二次确认），需在 `handles.py` 中单独处理 `yinpa_shop` 分支，并避免走 `gain_item` 的直接发货路径。

### 扩展指令

1. 在 `__init__.py` 中用 `on_command` / `on_message` 注册 matcher，设置 `priority` 与 `block`。
2. 在 `handles.py` 的 `yinpa_Handles` 中实现处理器（签名通常为 `matcher, event, args`）。
3. 如需多步交互，参考 `pending_join` / `pending_reincarnate` 的内存态缓存，并配合 `_join_pending_rule` / `_reincarnate_pending_rule` 注册高优先级 `on_message`。
4. 同步更新 `dicts.yinpa_help_dict`、`help_aliases` 与本 README 的指令表。

### 版本号

发布前统一修改：

- `pyproject.toml` 的 `version`
- `nonebot_plugin_chikari_yinpa/__init__.py` 的 `__version__`
- `dicts.py` 主帮助标题中的版本号
- `CHANGELOG.md` 新增对应版本段落

## 测试与检查

仓库暂未提供自动化测试套件；提交前至少执行：

```bash
python -m compileall -q nonebot_plugin_chikari_yinpa
```

并手动回归以下路径：`/info`、`/shop`、`/work` 长文本、`/yinpa_join` 创建流程、转生苹果确认/取消/超时。

## 贡献

提交 Issue 或 PR 时遵循以下约定：

- 一个 PR 只做一类改动，说明动机、行为变化与回归范围；
- 涉及数值平衡时同步更新 `dicts.py` 帮助文本与本 README；
- 新增配置项时同步更新 `config.py`、配置表与 `CHANGELOG.md`；
- 不提交运行时数据（localstore 目录或回退的 `data/`）或任何令牌/密钥。

## 更新日志

版本历史见 [CHANGELOG.md](./CHANGELOG.md)。

## License

[MIT](./LICENSE)

## 预览

（已过时）

![image](image/img_1.png)
