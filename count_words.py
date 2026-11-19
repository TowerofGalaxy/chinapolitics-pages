import os
import re

repo = r'D:\Documents\GitHub\chinapolitics'
files = [
    '00_系统规则与属性数据表.md',
    '01_第一卷_书斋与激流_1977-1982.md',
    '02_第二卷_前门东大街的风_1983-1990.md',
    '03_第三卷_东华门沉潜与外宣破冰_1990-2000.md',
    '04_第四卷_主政江淮与两会大考_2000-2007.md',
    '05_第五卷_大木仓胡同的算局_2007-2012.md',
    '06_第六卷_晚晴长风与历史行程_2013-2018.md',
    'README.md'
]

print(f"{'文件名':<40} | {'纯汉字数':<10} | {'字数(中文字+英文词)':<18} | {'非空字符数(含标点)':<18}")
print('-' * 95)

total_cn = 0
total_words = 0
total_chars = 0

for f in files:
    path = os.path.join(repo, f)
    with open(path, 'r', encoding='utf-8') as fp:
        text = fp.read()
    
    cn_chars = len(re.findall(r'[\u4e00-\u9fa5]', text))
    en_words = len(re.findall(r'[a-zA-Z0-9_-]+', text))
    word_count = cn_chars + en_words
    non_ws = len(re.sub(r'\s+', '', text))
    
    total_cn += cn_chars
    total_words += word_count
    total_chars += non_ws
    
    print(f"{f:<40} | {cn_chars:<10} | {word_count:<18} | {non_ws:<18}")

print('=' * 95)
print(f"{'【全剧本各卷分册独立合计】':<40} | {total_cn:<10} | {total_words:<18} | {total_chars:<18}")

combined_path = os.path.join(repo, '07_全卷整合版_浪潮与行程_完整互动剧本.md')
with open(combined_path, 'r', encoding='utf-8') as fp:
    c_text = fp.read()
c_cn = len(re.findall(r'[\u4e00-\u9fa5]', c_text))
c_words = c_cn + len(re.findall(r'[a-zA-Z0-9_-]+', c_text))
c_non_ws = len(re.sub(r'\s+', '', c_text))
print(f"{'07_全卷整合版(大通本)':<40} | {c_cn:<10} | {c_words:<18} | {c_non_ws:<18}")
