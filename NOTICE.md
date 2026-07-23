# 来源、归因与许可说明

## 上游文本

本项目的三书文本来自中国维基文库，获取与核对日期为 2026-07-24：

- [《医理真传》](https://zh.wikisource.org/wiki/醫理真傳)
- [《医法圆通》](https://zh.wikisource.org/wiki/醫法圓通)
- [《伤寒恒论》](https://zh.wikisource.org/wiki/傷寒恆論)

归因对象包括郑寿全（郑钦安）、相关原作者，以及各页面历史中列出的中国维基文库贡献者。中国维基文库站点声明其文本采用 [Creative Commons Attribution-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-sa/4.0/deed.zh) 许可。

## 本项目所作改动

- 繁体转简体
- 移除 Wikitext 模板和部分排版标记
- 将正文切分为稳定 doc ID
- 生成方剂、症状与主题索引及摘录
- 保留来源版本中的现代序言、校订文字和唐步祺 `【阐释】`

郑钦安原著本身已进入公有领域；现代序言、校订、阐释和维基贡献不能据此自动视为公有领域。为保守且统一地满足再利用条件，本项目将三书文本及含原文摘录的派生数据按 CC BY-SA 4.0 提供，并明确标注上述改动。

## 文件边界

以下文件适用 CC BY-SA 4.0：

- `references/yilizhenchuan.md`
- `references/yifayuantong.md`
- `references/shanghanheng.md`
- `references/formulas-index.md`
- `references/symptoms-index.md`
- `references/themes-index.md`
- `indexes/formulas.json`
- `indexes/symptoms.json`
- `indexes/themes.json`
- `indexes/section-manifest.json`

其余由本项目原创的技能说明、脚本、测试和文档适用根目录 [LICENSE](LICENSE) 中的 MIT License，除非文件另有说明。

本说明不是法律意见。如你是相关内容的权利人，或发现归因、授权状态存在问题，请通过 GitHub issue 提供具体页面、段落或 doc ID，以便核实和处理。
