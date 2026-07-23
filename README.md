# 郑钦安三书原文检索 Skill

一个面向 Agent Skills 兼容客户端的中文文献检索技能，用稳定段落 ID 检索《医理真传》《医法圆通》《伤寒恒论》的方剂、症状词和理论主题。

它是古籍图书管理员，不是医疗助手：只定位和解释文本，不诊断、不选方、不提供剂量或煎服方法。

## 功能

- 三书全文按 314 个稳定 doc ID 分段
- 109 个方剂词、119 个症状词、59 个主题词索引
- 按方名、白话词、理论术语、书名或 doc ID 检索
- 区分郑钦安原论、仲景原文、校补文字与后人 `【阐释】`
- 两个零第三方依赖的 Python 命令行工具
- Windows GBK 终端与 CRLF 换行兼容

## 安装

将仓库克隆到客户端支持的 skills 目录，并保持最终目录名为 `zheng-qinan`。例如：

```powershell
git clone https://github.com/88lin/zheng-qinan-skill.git "$env:USERPROFILE\.codex\skills\zheng-qinan"
```

也可以安装到项目级目录：

```powershell
git clone https://github.com/88lin/zheng-qinan-skill.git ".agents\skills\zheng-qinan"
```

重启或刷新客户端后，可以直接问：

```text
帮我找郑钦安谈“坎中一阳”的原文。
《医法圆通》哪里讨论过咳嗽？只要出处和原文。
白通汤在三书中分别出现在哪些段落？
```

## 命令行检索

仅需 Python 3.10 或更高版本，无第三方依赖。

```powershell
python scripts/search.py 白通汤 --limit 5
python scripts/search.py 坎中一阳 --index themes
python scripts/search.py 咳嗽 --book yifayuantong
python scripts/search.py 白通汤 --show-full
python scripts/list_by_type.py formulas --with-counts
```

`search.py` 先查方剂、症状和主题索引；没有精确 key 时回退到三书全文。成功返回退出码 `0`，无结果返回 `1`。

## 目录

```text
zheng-qinan/
├── SKILL.md
├── indexes/                  # JSON 索引与 section manifest
├── references/               # 三书正文、人工入口和人可读索引
├── scripts/                  # 检索脚本
├── evals/                    # 技能行为评测提示
└── tests/                    # 脚本与数据完整性测试
```

## 医疗边界

本项目仅供历史文献检索与学习。文本中可能出现附子、乌头类药物、历史剂量、炮制和煎服方法；这些内容不能作为个人医疗建议或实际用药依据。真实健康问题应咨询具备资质的专业人员，紧急情况应立即联系当地急救服务。

详见 [SKILL.md](SKILL.md) 的 `Safety boundaries`。

## 数据来源与许可

郑钦安原著已进入公有领域，但收录版本包含现代整理、序言和后人阐释，因此不能把整个数据集声明为公版。

- 技能说明、脚本、测试和本项目原创文档：MIT License
- 三书文本及包含原文摘录的派生索引：CC BY-SA 4.0

准确来源链接、归因、改编说明与逐目录许可边界见 [NOTICE.md](NOTICE.md)。

## 开发与验证

```powershell
python -m unittest discover -s tests -v
python -m py_compile scripts\search.py scripts\list_by_type.py
```

贡献前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。涉及文本勘误时，请附 doc ID 和可核对的来源。
