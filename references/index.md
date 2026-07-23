# 郑钦安三书 索引

> 医疗边界：本资料仅供学习与文本检索使用。涉及个人症状、诊断、剂量、用药、急症、孕产、儿童、肿瘤、附子等热药情境时，必须由合格中医师面诊，不得据此自行用药。

本 skill 分三本原文 + 三份索引 + 两条脚本。

## 三本原文（`references/`）

| 文件 | 内容 | 段数 | 何时打开 |
|---|---|---|---|
| `yilizhenchuan.md` | 《医理真传》全文，4 卷 | 79 | 用户问郑钦安理论体系、阳虚门/阴虚门问答、用药金针 |
| `yifayuantong.md` | 《医法圆通》全文，4 卷 | 206 | 用户按症状/病名（心痛、咳嗽、腰痛...）查郑钦安如何辨阴阳、用哪一路方 |
| `shanghanheng.md` | 《伤寒恒论》全文，10 卷 | 29 | 用户查郑钦安对《伤寒论》某条条文的注解 |

每段有稳定 doc ID：`<book>#j<juan>-s<section:03d>`，例：`yilizhenchuan#j2-s001`。文件里作为 `<!-- id: ... -->` 注释，可直接定位。

## 三份索引（`indexes/` 与 `references/*-index.md`）

| 索引 | keys | 命中总数 | 用途 |
|---|---|---|---|
| `formulas.json` / `formulas-index.md` | 109 | 644 段 | 按方名(白通汤、潜阳丹、四逆汤...)找相关原文 |
| `symptoms.json` / `symptoms-index.md` | 119 | 1142 段 | 按症状(咳嗽、腰痛、手足冷、失眠...)找相关原文 |
| `themes.json` / `themes-index.md` | 59 | 686 段 | 按主题(坎中一阳、元阴元阳、扶阳、辨认一切阳虚证法...)找相关原文 |

JSON 每条记录含 `id`, `book`, `juan`, `title`, `excerpt`。markdown 版是人可读列表。

## 两条脚本（`scripts/`）

| 脚本 | 用途 | 示例 |
|---|---|---|
| `search.py` | 通用检索 | `python scripts/search.py 白通汤 --limit 5` |
| `list_by_type.py` | 列出索引所有 key | `python scripts/list_by_type.py formulas --with-counts` |

## 路由决策

- 用户给了具体方名 → `search.py <方名>`，优先走 formulas 索引
- 用户给了具体症状（可能是白话） → `search.py <症状>`，走 symptoms；不明用词先看 `beginner-questions.md`
- 用户问郑钦安某个术语/理论 → `search.py <术语>`，走 themes
- 用户给了《伤寒论》条文号或条文关键字 → 直接 grep `references/shanghanheng.md`
- 用户想看某个方在郑钦安的整体思想里如何被安置 → 打开 `references/yilizhenchuan.md` 的相关章节（阳虚门问答、用药金针等）

## 郑钦安核心章节速查（medical librarian's shelf）

- 阳虚辨认总法：`yilizhenchuan#j1-s012` (卷一·辨认一切阳虚证法)
- 阴虚辨认总法：`yilizhenchuan#j1-s013` (卷一·辨认一切阴虚证法)
- 伤寒六经提纲病情：`yilizhenchuan#j1-s020` (卷一)
- 六经定法贯解：`yilizhenchuan#j1-s021` (卷一)
- 阳虚门问答（数十条实例）：`yilizhenchuan#j2-s001`
- 阴虚门问答（数十条实例）：`yilizhenchuan#j3-s001`
- 认病捷要总诀（分症条目 s009-s036）：从 `yilizhenchuan#j4-s009` (发热类) 起,分类含疟疾/鼓胀/积聚/痰饮/咳嗽/喘/呕吐/霍乱/呃逆/痢症/头痛/心痛/胸腹胁背腰痛/二便病 等
- 钦安用药金针：`yilizhenchuan#j4-s038`
- 用药弊端说：`yifayuantong#j1-s001` (卷一开篇,郑氏对当时医界的批评总论)
- 各症辨认阴阳用药法眼（心病不安等症状论述）：`yifayuantong#j1-s003` 起

具体 ID 以本 skill 自带的 `indexes/section-manifest.json` 为准。

## 版权与来源

郑钦安原著已进入公有领域，但本仓库收录版本还包含现代序言、校订与唐步祺 `【阐释】`，不能把整份数据笼统声明为公版。文本取自中国维基文库的《医理真传》《医法圆通》《伤寒恒论》页面，并作繁体到简体转换、Wikitext 清理、分段与索引生成。

正文及其派生索引按 CC BY-SA 4.0 归因与共享，准确来源链接、改动说明和文件许可边界见根目录 `NOTICE.md`。
