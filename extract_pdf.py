import pdfplumber
import glob
import os
import sys
import re
import json

sys.stdout.reconfigure(encoding='utf-8')

pdf_files = glob.glob(r"D:\Claude Code\vocab-tool\*.pdf")
if not pdf_files:
    print("未找到 PDF 文件")
    exit()

PDF_PATH = pdf_files[0]
pdf = pdfplumber.open(PDF_PATH)

# 按页提取，保持页面边界信息
all_lines = []
page_breaks = []  # 记录每页的起始行号
for i, page in enumerate(pdf.pages):
    start_idx = len(all_lines)
    text = page.extract_text()
    if text:
        for line in text.split('\n'):
            line = line.strip()
            if line:
                all_lines.append(line)
    page_breaks.append(start_idx)

pdf.close()
print(f"总行数: {len(all_lines)}, 页数: {len(page_breaks)}")

# 关键规律: 中文释义总是出现在条目编号行(header)的前一行
# Header 格式: {数字}{单词} {词性}.
# 例如: "1abandon vt." -> 前一行 "抛弃；放弃" 就是释义

# 先找到所有 header 行的索引
HEADER_RE = re.compile(
    r'^(\d{1,4})\s*([a-zA-Z][a-zA-Z\-\'’]*(?:\s+[a-zA-Z\-\'’]+)*)\s+'
    r'(vi\.|vt\.|v\.|n\.|adj\.|adv\.|prep\.|pron\.|conj\.|art\.)'
)

headers = []  # [(line_index, number, word, pos)]
for idx, line in enumerate(all_lines):
    m = HEADER_RE.match(line)
    if m:
        headers.append((idx, int(m.group(1)), m.group(2).strip(), m.group(3)))

print(f"找到 {len(headers)} 个词条头部")

# 解析每个词条
words = []
seen_word_lower = set()

for i, (hidx, num, word, pos) in enumerate(headers):
    # 跳过太短的词
    if len(word) < 2:
        continue

    # 默认意义行在前一行
    meaning_start = hidx - 1

    # 收集释义: 只取紧邻 header 前 1 行的中文内容
    # PDF 规律: 中文释义几乎总是在 header 的前一行
    meaning_lines = []

    # 策略1: 取 header 前一行(如果含中文)
    if meaning_start >= 0:
        line = all_lines[meaning_start]
        has_cjk = bool(re.search(r'[一-鿿]', line))
        if has_cjk:
            # 只保留中文和标点部分，去掉尾部可能的英文/数字
            cleaned = re.sub(r'[a-zA-Z0-9=, ]+$', '', line).strip()
            if cleaned:
                meaning_lines.append(cleaned)

    # 策略2: 如果前面没找到，试试 header 后一行
    if not meaning_lines:
        after = hidx + 1
        if after < len(all_lines):
            line = all_lines[after]
            if re.search(r'[一-鿿]', line) and not HEADER_RE.match(line):
                cleaned = re.sub(r'[a-zA-Z0-9=, ]+$', '', line).strip()
                if cleaned:
                    meaning_lines.append(cleaned)

    # 策略3: 如果 header 行本身包含中文(少见但存在)
    if not meaning_lines:
        line = all_lines[hidx]
        cjk_part = re.search(r'[一-鿿][一-鿿；，。！？\s]+', line)
        if cjk_part:
            meaning_lines.append(cjk_part.group().strip())

    meaning = '；'.join(meaning_lines) if meaning_lines else ''

    # 跳过释义太短或纯英文的
    if len(meaning) < 2:
        continue

    # 去重
    wl = word.lower()
    if wl in seen_word_lower:
        continue
    seen_word_lower.add(wl)

    # 频率: 按编号在全书中的位置估算
    # 编号大致从 1 到 ~4000（跳跃但不影响分布）
    ratio = min(num / 4000, 1.0)
    if ratio < 0.15: freq = 5
    elif ratio < 0.35: freq = 4
    elif ratio < 0.6: freq = 3
    elif ratio < 0.8: freq = 2
    else: freq = 1

    words.append({
        'word': word,
        'pos': pos,
        'meaning': meaning,
        'freq': freq
    })

print(f"解析到 {len(words)} 个有效单词")

# 保存
with open(r"D:\Claude Code\vocab-tool\words_parsed.json", 'w', encoding='utf-8') as f:
    json.dump(words, f, ensure_ascii=False, indent=2)

# 预览
print("\n=== 前 25 个 ===")
for w in words[:25]:
    stars = '★' * w['freq'] + '☆' * (5 - w['freq'])
    print(f"  {stars} {w['word']} ({w['pos']}) {w['meaning'][:60]}")

print("\n=== 中间抽查 (100-110) ===")
for w in words[100:110]:
    stars = '★' * w['freq'] + '☆' * (5 - w['freq'])
    print(f"  {stars} {w['word']} ({w['pos']}) {w['meaning'][:60]}")

print("\n=== 末尾抽查 ===")
for w in words[-10:]:
    stars = '★' * w['freq'] + '☆' * (5 - w['freq'])
    print(f"  {stars} {w['word']} ({w['pos']}) {w['meaning'][:60]}")
