import re

# 读取完整单词数据
with open(r"D:\Claude Code\vocab-tool\words_data.js", 'r', encoding='utf-8') as f:
    data_js = f.read()

# 读取当前 HTML
with open(r"D:\Claude Code\vocab-tool\index.html", 'r', encoding='utf-8') as f:
    html = f.read()

# 找到嵌入的示例数据块并替换
# 示例数据从 "const DEFAULT_WORDS = [" 到对应的 "];"
old_start = html.index('// === 单词数据 ===')
# 找到这个 script 块的结束
script_end = html.index('</script>', old_start)
# 找到这个 script 块内 "const DEFAULT_WORDS = [" 的位置
dws = html.index('const DEFAULT_WORDS = [', old_start)
# 找到对应的 "];" (在 script 结束之前)
dws_end = html.index('];', dws) + 2
# 找到注释 "// 完整词库见..."
comment_end = html.index('\n', dws_end)

new_data_block = html[old_start:dws] + data_js + '\n'
new_html = html[:old_start] + new_data_block + html[comment_end+1:]

with open(r"D:\Claude Code\vocab-tool\index.html", 'w', encoding='utf-8') as f:
    f.write(new_html)

import os
size_kb = os.path.getsize(r"D:\Claude Code\vocab-tool\index.html") / 1024
print(f"PWA 版 index.html 已生成 ({size_kb:.0f} KB)")

# 验证
word_count = new_html.count("word: '")
print(f"嵌入单词数: {word_count}")
