# 郑钦安三书 索引

> 医疗边界：本资料仅供学习与文本检索使用。涉及个人症状、诊断、剂量、用药、急症、孕产、儿童、肿瘤、附子等热药情境时，必须由合格中医师面诊，不得据此自行用药。

本 skill 分三本原文 + 三份索引 + 检索脚本。

> 读取纪律：本目录和 `indexes/` 里的文件都很大（250-650 KB），**不要整文件读入上下文**。一律用 `scripts/search.py` 查询，用 `--id <doc-id>` 取单段。

## 三本原文（`references/`）

| 文件 | 内容 | 段数 | 体积 | 何时打开 |
|---|---|---|---|---|
| `yilizhenchuan.md` | 《医理真传》全文，4 卷 | 79 | ~460 KB | 用户问郑钦安理论体系、阳虚门/阴虚门问答、用药金针 |
| `yifayuantong.md` | 《医法圆通》全文，4 卷 | 206 | ~250 KB | 用户按症状/病名（心痛、咳嗽、腰痛...）查郑钦安如何辨阴阳、用哪一路方 |
| `shanghanheng.md` | 《伤寒恒论》全文，10 卷 | 29 | ~460 KB | 用户查郑钦安对《伤寒论》某条条文的注解 |

每段有稳定 doc ID：`<book>#j<juan>-s<section:03d>`，例：`yilizhenchuan#j2-s001`。文件里作为 `<!-- id: ... -->` 注释，可直接定位，或用 `python3 scripts/search.py --id yilizhenchuan#j2-s001` 取整段。

段落长度很不均匀：中位数约 250 字，但有 13 段超过 5000 字，最长的 `shanghanheng#j2-s001`（太阳中篇）接近 3 万字。取整段时注意 `--max-chars`（默认 4000）。

## 三份索引（`indexes/` 与 `references/*-index.md`）

| 索引 | keys | 命中总数 | 用途 |
|---|---|---|---|
| `formulas.json` / `formulas-index.md` | 109 | 644 段 | 按方名(白通汤、潜阳丹、四逆汤...)找相关原文 |
| `symptoms.json` / `symptoms-index.md` | 119 | 1142 段 | 按症状(咳嗽、腰痛、手足冷、失眠...)找相关原文 |
| `themes.json` / `themes-index.md` | 58 | 684 段 | 按主题(坎中一阳、元阴元阳、扶阳、辨认一切阳虚证法...)找相关原文 |

JSON 每条记录含 `id`, `book`, `juan`, `title`, `excerpt`。markdown 版是人可读列表。索引查询必须走脚本，不要读取整个 JSON。

`indexes/variants.json` 是繁体/异体 → 简体单字映射（生成物），供 `search.py` 在原词零命中时做一次归一化重试。

## 脚本（`scripts/`）

| 脚本 | 用途 | 示例 |
|---|---|---|
| `search.py` | 通用检索 / 按 doc ID 取段 | `python3 scripts/search.py 白通汤 --limit 5` |
| `list_by_type.py` | 列出索引所有 key | `python3 scripts/list_by_type.py formulas --with-counts` |
| `build_variants.py` | 重新生成繁简映射表（需 zhconv，仅开发期） | `python3 scripts/build_variants.py --check` |

## 路由决策

- 用户给了具体方名 → `search.py <方名> --index formulas`
- 用户给了具体症状（可能是白话） → `search.py <症状> --index symptoms`；不明用词先看 `beginner-questions.md`
- 用户问郑钦安某个术语/理论 → `search.py <术语> --index themes`
- 用户给了《伤寒论》条文号或条文关键字 → `search.py <关键字> --book shanghanheng`（正文保留“原文117”式编号）
- 用户给了 doc ID 或需要完整段落 → `search.py --id <doc-id>`
- 词性不确定 → 不带 `--index` 直接检索，脚本会先查三份索引再回退全文

## 郑钦安核心章节速查（medical librarian's shelf）

- 阳虚辨认总法：`yilizhenchuan#j1-s012` (卷一·辨认一切阳虚证法)
- 阴虚辨认总法：`yilizhenchuan#j1-s013` (卷一·辨认一切阴虚证法)
- 伤寒六经提纲病情：`yilizhenchuan#j1-s020` (卷一)
- 六经定法贯解：`yilizhenchuan#j1-s021` (卷一)
- 阳虚门问答（数十条实例）：`yilizhenchuan#j2-s001` (卷二·阳虚症门问答，约 2.5 万字)
- 阴虚门问答（数十条实例）：`yilizhenchuan#j3-s001` (卷三·阴虚症门问答，约 2.7 万字)
- 认病捷要总诀（分症条目 s009-s036）：从 `yilizhenchuan#j4-s009` (发热类) 起,分类含疟疾/鼓胀/积聚/痰饮/咳嗽/喘/呕吐/霍乱/呃逆/痢症/头痛/心痛/胸腹胁背腰痛/二便病 等
- 钦安用药金针：`yilizhenchuan#j4-s038`
- 用药弊端说：`yifayuantong#j1-s001` (卷一开篇,郑氏对当时医界的批评总论)
- 各症辩认阴阳用药法眼（总标题）：`yifayuantong#j1-s002`；其下各症从 `yifayuantong#j1-s003` (心病不安) 起

标题一律照录语料原字（例如《医法圆通》作“各症**辩**认阴阳用药法眼”，《医理真传》卷二作“阳虚**症**门问答”），按标题检索时请用这里的写法。具体 ID 以本 skill 自带的 `indexes/section-manifest.json` 为准。

## 版权与来源

郑钦安原著已进入公有领域，但本仓库收录版本还包含现代序言、校订与唐步祺 `【阐释】`，不能把整份数据笼统声明为公版。文本取自中国维基文库的《医理真传》《医法圆通》《伤寒恒论》页面，并作繁体到简体转换、Wikitext 清理、分段与索引生成。

正文及其派生索引按 CC BY-SA 4.0 归因与共享，准确来源链接、改动说明和文件许可边界见根目录 `NOTICE.md`。
