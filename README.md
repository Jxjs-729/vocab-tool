# 单词 — 托福词汇学习工具

基于王玉梅《TOEFL词汇》的 PWA 单词学习应用，收录 **4859 个托福核心词汇**。

## 功能

- 🔤 **字母筛选** — 按首字母浏览单词
- 📋 **List 分组** — 按原书 List 分组学习
- ⭐ **星级标记** — 三档重要度分类（高频/常用/低频）
- 📱 **PWA 离线可用** — 支持安装到手机/电脑桌面
- 🔍 **搜索** — 快速查找单词

## 在线地址

- GitHub Pages: [jxjs-729.github.io/vocab-tool](https://jxjs-729.github.io/vocab-tool)
- Gitee Pages: [fake-xuan-ke.gitee.io/vocab-tool](https://fake-xuan-ke.gitee.io/vocab-tool)
- 单词表: [jxjs-729.github.io/vocab-tool/单词表.html](https://jxjs-729.github.io/vocab-tool/单词表.html)

## 本地使用

直接用浏览器打开 `index.html` 或 `单词表.html` 即可，无需服务器。

## 项目结构

| 文件 | 说明 |
|------|------|
| `index.html` | PWA 单词学习主应用 |
| `单词表.html` | 完整词汇表（表格形式） |
| `words_data.js` | 单词数据库（JSON） |
| `extract_pdf.py` | 从 PDF 提取原始文本 |
| `build_words.py` | 解析文本生成结构化词库 |
| `build_pwa.py` | 将词库嵌入 HTML 生成 PWA |
| `sw.js` | Service Worker（离线缓存） |
| `manifest.json` | PWA 清单 |

## 数据来源

王玉梅《TOEFL词汇》— 收录托福考试高频词汇，按 List 编排，配星级标注。
