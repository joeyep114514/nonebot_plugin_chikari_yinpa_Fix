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
### 原作者称由于学业问题，源项目更新放缓，但实际已进入半停更状态
这是一个基于NoneBot 2的银趴插件，由于源项目年久失修，本项目在此基础上进行了修复、完善以及多次平衡性调整，使其可供正常游玩

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
| chikari_yinpa_font | 否 | Path(__file__).parent / "resource" / "NotoSansCJKsc-VF.ttf" | 绘图所用 Noto Sans CJK 主字体（可变字体，自动应用 Regular 字重） |
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
| ypshop | 无 | 否 | 私聊/群聊 | 花费金钱购买商品（银趴商店） |
| work | 无 | 否 | 私聊/群聊 | 工作，获得金钱及其他东西 |
| transfer | 无 | 否 | 私聊/群聊 | 转账给他人 |

## 🔭 TODO

### 如果有什么好的想法，欢迎提交[issue](https://github.com/joeyep114514/nonebot_plugin_chikari_yinpa_Fix/issues)或[pr](https://github.com/joeyep114514/nonebot_plugin_chikari_yinpa_Fix/pulls)

- [x] 将经济相关拆分为单独的插件，未来可与其他插件互通

- [ ] 排名功能（群榜，总榜）

- [ ] 誓约系统

- [x] 成就系统

- [ ] bot随机自主出击

- [x] 单独的钓鱼插件

## 📝 更新日志

### v2.1.7
- 属性模型重构：各属性不再区分基础值与当前值，各类加成直接生效；检定（失神/昏迷/工作检定）与工作收益统一使用增益后的数值
- 属性上限规则统一：体质与意志上限 80（含各类加成，D10/探险提升同步封顶；吸血鬼种族体质上限 100→80），其余属性（力量/技巧/智力/魅力）无上限（取消原种族 100/80 上限）
- 商店价格调整：商品1 100→300、商品2 500→800、商品3 100→300（详见商店价格表）
- 商品3（精力药水）在 HP 已满时禁止购买并提示，避免无效消费
- 精简创建角色流程提示与种族介绍文案（信息不变，篇幅大幅缩短）
- 商店指令改为 `ypshop`（别名：银趴商店/买/买东西/店），与钓鱼插件的 `shop` 商店区分，避免指令冲突
- 图片渲染四周增加留白，文字不再贴边
- 商店列表改为统一格式：`===== 店名 =====` 标题 + `▶ 条目` + 底部购买提示（与钓鱼插件商店一致）
- 数据迁移：启动时自动为存量用户补齐缺失的 `skill` 字段（原子写回），旧版本用户升级后不会因缺字段崩溃；同时所有技能读写点改为防御式访问，`skill_refresh` 使用 `setdefault` 保证写入不丢失
- 平衡性调整：探险（工作6）特殊事件触发概率从 30% 下调至 10%（工作帮助文本同步更新）
- 精力药水（商品3）回复 HP 封顶至当前 HP 上限（含舰装加成），不再出现溢出数值
- Bug 修复：`/work` 传入非数字参数（如 `/work abc`）导致命令无响应；单次购买列表重复指定商品11（屹立不倒）会扣双份钱但只发货一份，现提前拦截提示
- 健壮性加固：新增 `safe_int` 安全整数转换，`str.isdigit()` 对上标（²）、带圈数字（①）等 Unicode 字符误判为数字但 `int()` 会抛错，此前 `/work ²`、`/ypshop ①`、`/transfer ²`、`/yinpa_help skill ²` 及建号流程回复此类字符均会使命令无响应，现全部统一走安全解析并给出错误提示
- Bug 修复：商店按名称购买扣款后崩溃、重复购买商品11仍扣款、舰装破损后等级被重置为1、购买舰装升级书会清除破损冷却、数据文件改为原子写入并在损坏时自动备份恢复、帮助命令非法参数崩溃、商品12效果不落盘、新建用户缺失技能字段导致的潜在崩溃等
- 帮助文本与代码一致性修正：种族属性上限、状态/商品描述公式、失神期间技能失效说明、转账限制说明、指南中的属性与收益说明
- 技能平衡性调整：
  - 猫化（ID2）攻防加成从 `1d(30√L)` 调整为 `1d(20√L)`
  - 自然之心（ID3）攻防加成从 `1d(智力×√L/2)` 调整为 `1d(智力×√L/3)`
  - 圣体（ID4）/ 淫纹（ID5）加成从 `1d(80√L)` 调整为 `1d(50√L)`
  - 舰装（ID6）机制重做：不再增加力量/体质/意志属性，改为意志HP、体质HP上限各增加 `100√L`
  - 猩红之影（ID7）白天惩罚改为 `15/√L`、夜晚加成改为 `10√L`
  - 弱点（ID15）改为每次受击时 `1d100 < 30√L` 则额外受到 `1d500`（掷骰）伤害（等级越高触发概率越大）
- 同步更新技能帮助文本

### v2.0.7
- 文本转图片（透/榨等反馈、帮助、商店、工作列表）新增自动换行，长文本不再渲染成超宽长条图
- 信息图（/info）属性只显示当前值，不再显示基础值双栏（力量/体质/技巧/意志/智力/魅力）

### v2.0.6
- 转账取消冷却与解锁门槛，只要余额充足即可转账，无任何限制
- 工作冷却固定为 1 小时，并跨注销保存（注销重注册后冷却仍保留）

### v2.0.2

- README 新增更新日志章节
- 主帮助版本号与插件版本对齐

### v2.0.1

- 长消息（PVP 结果、商店/工作列表、帮助等）渲染为图片发送，短消息保持纯文本
- 数值展示与计算统一四舍五入保留两位小数
- 新增新手引导式主帮助（/yinpa_help），完善工作/商店/D10 说明
- PyPI 发布仅限主分支或 tag 触发

### v2.0.0

- 平衡性调整：工作系统、吸血鬼、D10 预算池、成就系统
- 适配独立钓鱼插件，成就/统计互通

## 🥳 预览图

（已过时）

![image](image/img_1.png)
