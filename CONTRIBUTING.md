# 贡献指南

感谢你帮助改进这个文献检索 skill。

## 可接受的贡献

- 修正文献转写、标点或索引错误
- 改善检索脚本和跨平台兼容性
- 增加可复现的测试或评测提示
- 改善来源归因和文档

不要提交个人诊断、方剂推荐、剂量、炮制或煎服建议。这个项目的边界是文本检索，不是临床决策。

## 文本勘误

请在 issue 或 pull request 中提供：

1. 稳定 doc ID，例如 `yilizhenchuan#j1-s012`
2. 当前文本与建议文本
3. 可核对的公开来源链接或版本信息
4. 该修改是否需要同步更新 JSON 和 Markdown 索引

不要只根据现代转述改写古籍原文。

## 本地验证

检索脚本与测试只依赖 Python 标准库（3.10+）。提交前运行：

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile scripts/search.py scripts/list_by_type.py scripts/build_variants.py
```

Windows 上把 `python3` 换成 `python`、路径分隔符换成 `\`。

新增脚本行为或修复非平凡缺陷时，请先增加能复现预期行为的测试。数据层的约束（doc ID 可寻址、索引 key 与语料一致、索引 key 不含句读）都写在 `tests/test_data_integrity.py`，改动语料或索引后必须通过。

## 生成物

`indexes/variants.json`（繁体/异体 → 简体单字映射）由脚本生成，不要手工编辑。改动 `references/*.md` 的用字后重新生成：

```bash
python3 -m pip install zhconv        # 仅此步需要，检索与测试都不依赖
python3 scripts/build_variants.py
python3 scripts/build_variants.py --check
```

该映射只收录“语料中不存在的字形 → 语料中存在的字形”，以免把《乾坤大旨》这类语料原有字形改写掉。

## 许可

提交代码或原创文档即表示你同意按 MIT License 提供贡献。提交来源文本或其派生索引时，还应确保能够按 CC BY-SA 4.0 再分发，并在必要时补充归因与改动说明。
