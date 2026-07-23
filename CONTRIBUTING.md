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

项目只依赖 Python 标准库。提交前运行：

```powershell
python -m unittest discover -s tests -v
python -m py_compile scripts\search.py scripts\list_by_type.py
```

新增脚本行为或修复非平凡缺陷时，请先增加能复现预期行为的测试。

## 许可

提交代码或原创文档即表示你同意按 MIT License 提供贡献。提交来源文本或其派生索引时，还应确保能够按 CC BY-SA 4.0 再分发，并在必要时补充归因与改动说明。
