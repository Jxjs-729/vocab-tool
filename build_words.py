import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

with open(r"D:\Claude Code\vocab-tool\words_parsed.json", 'r', encoding='utf-8') as f:
    words = json.load(f)

print(f"总词数: {len(words)}")

# 频段统计
for f in range(5, 0, -1):
    count = sum(1 for w in words if w['freq'] == f)
    print(f"  ★{f}: {count}")

# ===== 1. 生成 words_data.js（含词性）=====
js_lines = ['// 托福词汇数据 - 从王玉梅《TOEFL词汇》提取']
js_lines.append('// 自动生成，共 {} 个单词'.format(len(words)))
js_lines.append('const DEFAULT_WORDS = [')

for w in words:
    meaning_with_pos = f"{w['pos']} {w['meaning']}"
    meaning_escaped = meaning_with_pos.replace('\\', '\\\\').replace("'", "\\'").replace('\n', ' ')
    word_escaped = w['word'].replace('\\', '\\\\').replace("'", "\\'")
    js_lines.append(
        f"  {{ word: '{word_escaped}', phonetic: '', meaning: '{meaning_escaped}', "
        f"example: '', freq: {w['freq']} }},"
    )

js_lines.append('];')

with open(r"D:\Claude Code\vocab-tool\words_data.js", 'w', encoding='utf-8') as f:
    f.write('\n'.join(js_lines))

print("words_data.js 已生成（含词性）")

# ===== 2. 准备两种排序 =====
words_book = words  # 原书顺序
words_az = sorted(words, key=lambda w: w['word'].lower())  # A-Z

# ===== 3. 生成单词表 HTML =====
def build_rows(word_list, suffix):
    rows = []
    cur = None
    for i, w in enumerate(word_list, 1):
        first = w['word'][0].upper()
        stars = '★' * w['freq'] + '☆' * (5 - w['freq'])
        if first != cur:
            cur = first
            rows.append(f'<tr class="letter-head" id="l-{first}-{suffix}"><td colspan="4">{first}</td></tr>')
        rows.append(
            f'<tr><td class="num">{i}</td>'
            f'<td><span class="word">{w["word"]}</span></td>'
            f'<td><span class="pos">{w["pos"]}</span> <span class="meaning">{w["meaning"]}</span></td>'
            f'<td class="stars">{stars}</td></tr>'
        )
    return '\n'.join(rows)

def build_index(word_list, suffix):
    seen = set()
    links = []
    for w in word_list:
        first = w['word'][0].upper()
        if first not in seen:
            seen.add(first)
            links.append(f'<a href="#l-{first}-{suffix}" onclick="switchTab(\'{suffix}\')">{first}</a>')
    return ' '.join(links)

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>托福词汇表 - 王玉梅</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #f8f8f8; color: #333; }}
.header {{ background: #fff; border-bottom: 1px solid #e0e0e0; padding: 20px 32px; position: sticky; top: 0; z-index: 10; }}
.header h1 {{ font-size: 22px; margin-bottom: 4px; }}
.header p {{ font-size: 13px; color: #888; }}

.tab-bar {{ max-width: 1000px; margin: 16px auto 0; padding: 0 32px; display: flex; gap: 8px; }}
.tab-btn {{ padding: 8px 20px; border: 1px solid #ddd; border-radius: 6px; background: #fff; cursor: pointer; font-size: 14px; color: #666; }}
.tab-btn.active {{ background: #333; color: #fff; border-color: #333; }}

.legend {{ max-width: 1000px; margin: 12px auto 0; padding: 0 32px; display: flex; gap: 16px; font-size: 13px; color: #888; }}
.legend .star {{ color: #f0ad4e; }}

.index {{ max-width: 1000px; margin: 12px auto; padding: 0 32px; display: flex; flex-wrap: wrap; gap: 4px; }}
.index a {{ display: inline-block; padding: 3px 8px; font-size: 12px; color: #555; text-decoration: none; border-radius: 3px; }}
.index a:hover {{ background: #e8e8e8; }}

.table-wrap {{ max-width: 1000px; margin: 24px auto 60px; padding: 0 32px; }}
table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }}
th {{ background: #f5f5f5; padding: 10px 14px; text-align: left; font-size: 13px; color: #888; font-weight: 500; border-bottom: 1px solid #e0e0e0; }}
td {{ padding: 8px 14px; font-size: 14px; border-bottom: 1px solid #f0f0f0; }}
tr:hover td {{ background: #fafafa; }}
.num {{ color: #bbb; font-size: 12px; width: 40px; }}
.word {{ font-weight: 600; }}
.pos {{ color: #888; font-size: 12px; }}
.stars {{ color: #f0ad4e; font-size: 12px; white-space: nowrap; }}
.meaning {{ color: #444; }}

.letter-head {{ background: #f5f5f5 !important; }}
.letter-head td {{ padding: 12px 14px; font-weight: 700; font-size: 18px; color: #333; border-bottom: 2px solid #ddd; }}

.tab-content {{ display: none; }}
.tab-content.active {{ display: block; }}

@media print {{
  body {{ background: #fff; }}
  .header {{ position: static; }}
  .index {{ display: none; }}
  .tab-bar {{ display: none; }}
  .tab-content {{ display: block !important; }}
}}
</style>
</head>
<body>
<div class="header">
  <h1>托福词汇表</h1>
  <p>来源：王玉梅《TOEFL词汇》 | 共 {len(words)} 个单词</p>
</div>

<div class="tab-bar">
  <button class="tab-btn active" onclick="switchTab('az')">A-Z 字母顺序</button>
  <button class="tab-btn" onclick="switchTab('book')">原书顺序（词根词族）</button>
</div>

<div class="legend">
  <span><span class="star">★★★★★</span> 必考</span>
  <span><span class="star">★★★★</span> 高频</span>
  <span><span class="star">★★★</span> 常见</span>
  <span><span class="star">★★</span> 偏低频</span>
  <span><span class="star">★</span> 低频</span>
</div>

<div class="index" id="idx-az">
  <strong style="font-size:12px;color:#888;margin-right:6px;">字母索引：</strong>
  {build_index(words_az, 'az')}
</div>
<div class="index" id="idx-book" style="display:none;">
  <strong style="font-size:12px;color:#888;margin-right:6px;">字母索引：</strong>
  {build_index(words_book, 'book')}
</div>

<div class="table-wrap">
<div class="tab-content active" id="tab-az">
<table>
<thead><tr><th class="num">#</th><th>单词</th><th>释义</th><th>重要度</th></tr></thead>
<tbody>
{build_rows(words_az, 'az')}
</tbody></table>
</div>

<div class="tab-content" id="tab-book">
<table>
<thead><tr><th class="num">#</th><th>单词</th><th>释义</th><th>重要度</th></tr></thead>
<tbody>
{build_rows(words_book, 'book')}
</tbody></table>
</div>
</div>

<script>
function switchTab(name) {{
  document.querySelectorAll('.tab-btn').forEach(function(b) {{ b.classList.remove('active'); }});
  document.querySelectorAll('.tab-content').forEach(function(c) {{ c.classList.remove('active'); }});
  document.querySelectorAll('.index').forEach(function(i) {{ i.style.display = 'none'; }});
  if (name === 'az') {{
    document.querySelectorAll('.tab-btn')[0].classList.add('active');
    document.getElementById('tab-az').classList.add('active');
    document.getElementById('idx-az').style.display = 'flex';
  }} else {{
    document.querySelectorAll('.tab-btn')[1].classList.add('active');
    document.getElementById('tab-book').classList.add('active');
    document.getElementById('idx-book').style.display = 'flex';
  }}
}}
</script>
</body></html>'''

list_path = r"D:\Claude Code\vocab-tool\单词表.html"
with open(list_path, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = os.path.getsize(list_path) / 1024
print(f"单词表已生成: 单词表.html ({size_kb:.0f} KB)")

print("\n=== A-Z 顺序预览 ===")
for w in words_az[:8]:
    stars = '★' * w['freq'] + '☆' * (5 - w['freq'])
    print(f"  {stars} {w['word']} ({w['pos']}) {w['meaning'][:50]}")

print("\n=== 原书顺序预览 ===")
for w in words_book[:8]:
    stars = '★' * w['freq'] + '☆' * (5 - w['freq'])
    print(f"  {stars} {w['word']} ({w['pos']}) {w['meaning'][:50]}")
