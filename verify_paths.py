# 旧版手写模型：规则可能与网页引擎不同，数值分布请使用 pnpm test:balance。
import json
import glob
import re
import sys

sys.stdout.reconfigure(line_buffering=True)
from collections import defaultdict

def clamp(val):
    return max(0, min(100, val))

def verify_schema_and_banned_words():
    with open("variables.json", "r", encoding="utf-8") as f:
        schema = json.load(f)
    defined_tags = set(schema["tags"].keys())

    banned = [
        "暗礁", "巨轮", "舵盘", "风浪", "绞肉机", "死一般寂静",
        "目光如炬", "鹰隼", "嘴角勾起", "面如死灰", "微积分", "大数定律", "史诗级"
    ]
    ghost_vars = ["政治威权", "程序理性", "世故身段", "民心值"]

    vol_files = sorted(glob.glob("0[0-7]_*.md")) + ["README.md"]
    found_tags_in_md = set()
    banned_hits = []
    ghost_hits = []
    non_flag_brackets = {
        "直接收益", "立刻代价", "立刻付出的代价", "后续反噬(Flag)", "后续章节的潜在反噬(Flag)",
        "后续反噬", "后续注脚", "前置加成", "前置修正", "前置门槛", "前置限制", "0, 100", "-4, +4"
    }

    for fn in vol_files:
        with open(fn, "r", encoding="utf-8") as f:
            text = f.read()
        for bw in banned:
            if bw in text:
                if fn == "README.md" and "彻底封禁" in text and bw in text.split("彻底封禁")[1].split("等大模型")[0]:
                    continue
                banned_hits.append((fn, bw))
        for gv in ghost_vars:
            if gv in text:
                ghost_hits.append((fn, gv))
        for m in re.findall(r"`\[([^\]]+)\]`", text):
            if m not in non_flag_brackets:
                found_tags_in_md.add(m)

    undefined_tags = found_tags_in_md - defined_tags
    unused_tags = defined_tags - found_tags_in_md
    print(f"Schema Tags Defined: {len(defined_tags)} | Used in 00-06: {len(found_tags_in_md)}")
    print(f"Undefined Tags in MD: {undefined_tags}")
    print(f"Unused Tags in Schema: {unused_tags}")
    print(f"Banned Word Hits in 00-06: {banned_hits}")
    print(f"Ghost Var Hits in 00-06: {ghost_hits}")
    return schema, not (undefined_tags or unused_tags or banned_hits or ghost_hits)

def evaluate_17th_congress(c, l, f, r, tags):
    if "象牙塔学者" in tags:
        return "Ending B (象牙塔的余生)"
    if c < 45 or f < 35:
        return "Ending C (改革折翼 · 倚楼听风)"
    if "激进政改旗手" in tags and c >= 50 and r >= 60:
        return "Ending D (顺水推舟 · 青灯咨政)"
    if c >= 62 and l >= 35 and r >= 50:
        return "PROCEED_TO_VOL5"
    return "Ending E (留任守成 · 异地平调)"

def evaluate_18th_congress(c, l, f, r, tags):
    eff_c = c - (8 if "大秘隐雷" in tags else 0)
    if (eff_c >= 85 and r >= 75
            and "自揭家丑非议" not in tags
            and "连带问责留档" not in tags
            and "大秘隐雷" not in tags):
        return "Ending A1 (巅峰折冲 · 核心统筹)"
    if eff_c < 60 or l < 30:
        return "Ending A3 (提前淡出 · 倚楼晚照)"
    return "PROCEED_TO_VOL6"

def run_historical_baseline():
    print("\n=== 验证全六卷正史基准路线 (Historical Baseline Route) ===")
    # Stage 1: Vol 1 (摸底C + 1-B + 2-A) -> Vol 2 (摸底A + 3-C + A-2 + B-1 + 4-1B + 4-B) -> Vol 3 (摸底B + 5-B + C-1 + D-2 + 6-B)
    ct, ra = 50, 50
    tags = {"纯粹知识分子底色", "第三梯队座谈纪要"}
    ct += 4; ra -= 3; tags.add("考察保留")
    ct += 6 + 1; ra -= 3; tags.add("大院子弟标签")
    ct, ra = clamp(ct), clamp(ra)
    print(f"卷一结束: 组织信任={ct}, 改革锐度={ra}")

    tags.add("温州调研原件")
    ra += 6 + 2; ct -= 3; tags.update(["商品经济探索先声", "筹会透支"]) # 3-C net -3
    ct += 2; ra -= 2  # A-2
    ra += 3; ct -= 3; tags.add("脱离工农议论")  # B-1
    ra -= 2  # 筹会透支
    ra += 2; ct -= 2  # 4-1B
    ra += 10; ct -= 15; tags.update(["庇护者的契约", "十年冷板凳"])
    ct, ra = clamp(ct), clamp(ra)
    print(f"卷二结束: 组织信任={ct}, 改革锐度={ra}, 警戒(<=35)={ct<=35}")

    tags.add("外宣案例剪报")
    ra += 5 + 2; ct -= 3; tags.update(["精准反制经验", "外宣基本功", "涉外政治风险"])
    ra += 2; ct -= 2; tags.add("涉外口径微瑕")  # C-1
    ct += 2; ra -= 2; tags.add("守旧平庸标签")  # D-2
    ra += 2  # 商品经济探索先声
    ct += 8; ra -= 5; tags.add("老同志的信赖档案")  # 6-B
    ct, ra = clamp(ct), clamp(ra)
    print(f"卷三结束: 组织信任={ct}, 改革锐度={ra}")

    # Stage 2: Vol 4 (A+C -> 1-A -> 2-A -> 3-A -> 4-A -> 5-B -> 1-C,2-C,3-C -> 6-A)
    c, l, f, r = 55, 60, 60, 50
    # Stage 1 -> Stage 2 value injection
    c += max(-4, min(4, (ct - 50) // 4))
    r += max(-4, min(4, (ra - 50) // 4))
    if "边缘平调序列" in tags: c -= 3
    if "报批越界通报" in tags: c -= 2
    c, r = clamp(c), clamp(r)

    tags.add("公交录像带")
    l += 5 + 3; tags.add("老同志口风")  # has 老同志的信赖档案
    l -= 2  # 脱离工农议论
    c += 5; r += 5; l -= 10; tags.add("机关震荡反弹")
    c += 10; l -= 15; f -= 10; tags.update(["彻底停工", "省府裂痕"])
    c += 15; l -= 10; tags.add("连带问责留档")
    l -= 2  # 省府裂痕 -> l=34 <= 35 (怠工触发!)
    c += 5; l += 20; f -= 12; tags.add("预备费见底")
    c += 5; r += 5; l += 3; tags.update(["制度精算样本", "形式主义诟病"])
    # 13: 1-C, 2-C, 3-C
    r += 3; c += 2 + 1; f -= 1; tags.add("涉外口径微瑕")
    r += 3; c += 2 + 1; l -= 1
    r += 4; c += 2; l -= 4 + 1; tags.add("地方抵制环保考核")
    r += 2; tags.add("外宣高手")
    # 14: 6-A
    r += 1; c -= 2; tags.update(["改革盟约", "派系结盟猜忌"])
    c, l, f, r = clamp(c), clamp(l), clamp(f), clamp(r)
    e17 = evaluate_17th_congress(c, l, f, r, tags)
    print(f"卷四结束(十七大节点): 中央={c}, 系统协同={l}, 财政={f}, 改革={r} => {e17}")

    # Vol 5: (摸底 A+C -> 15-B 测评 -> 16-B 特区 -> Black Swan C 借刀 -> 17-B 吹风会)
    if l < 50: l += 8
    tags.update(["监督局带病档案", "使节团提问清单"])
    if "形式主义诟病" in tags or "滑头风评" in tags: r -= 2
    if "党管干部质疑" in tags: c -= 3
    c += 5 + (2 if ("基层测评原始样表" in tags or "无暇履历" in tags or "宏观定力" in tags) else 0)
    r += 5; l -= 2
    tags.update(["加权考核矩阵", "加权考核执行损耗"])
    
    # 16-B
    c_base = c + (2 if "监督局带病档案" in tags else 0)
    r += 7; c = c_base + 2; l -= 2 + (1 if ("派系结盟猜忌" in tags or "地方招商宿怨" in tags) else 0)
    tags.update(["特区新局", "跨省空降派系芥蒂"])
    
    # Black Swan: 老陈的信封 (Option C: 借刀反查, requires 监督局带病档案)
    c += 2; l -= 2; r += 3
    
    # 17-B
    c_base = c - (2 if "大院子弟标签" in tags else 0)
    r += 7 + (2 if "使节团提问清单" in tags else 0)
    c = c_base + 2 - (2 if "改革保守退缩" in tags else 0)
    l -= 2
    tags.update(["执政党阳光化象征", "系统内保守派侧目"])
    c, l, f, r = clamp(c), clamp(l), clamp(f), clamp(r)
    e18 = evaluate_18th_congress(c, l, f, r, tags)
    print(f"卷五结束(十八大节点): 中央={c}, 系统协同={l}, 财政={f}, 改革={r} => {e18}")

    # Vol 6: (A -> 18-1A -> 18-2A)
    tags.add("群团基层调研底表")
    l -= 2  # 系统内保守派侧目/跨省空降派系芥蒂
    c += 4; r -= 3; tags.add("端方国士")
    r += 5 + 2; l -= 2; c -= 2; tags.add("未竞的改革之弦")
    c, l, f, r = clamp(c), clamp(l), clamp(f), clamp(r)
    print(f"卷六终局: 中央={c}, 系统协同={l}, 财政={f}, 改革={r} => Ending A2 (端方晚晴 · 稳健执印)")

def simulate_all_paths():
    def proj(flags, keep):
        return frozenset(flags & keep)

    s1_b_count = 0
    keep_v2 = {
        "第三梯队座谈纪要", "退稿油印刊物", "书生执拗", "考察保留", "大院子弟标签",
        "法治骨气", "老辈训诫", "双轨探索者", "导师推荐信底稿"
    }
    dp_v1 = defaultdict(int)
    for m1 in ["A", "B", "C"]:
        for c01 in ["1-A", "1-B", "1-C", "1-D"]:
            if c01 == "1-D":
                s1_b_count += 1
                continue
            for c02 in ["2-A", "2-B", "2-C"]:
                ct, ra = 50, 50
                t = {"纯粹知识分子底色"}
                if m1 == "A": t.add("退稿油印刊物")
                elif m1 == "B": t.add("导师推荐信底稿")
                else: t.add("第三梯队座谈纪要")
                if c01 == "1-A": ra += 5; ct -= 4; t.add("书生执拗")
                elif c01 == "1-B": ct += 4; ra -= 3; t.add("考察保留")
                else:
                    ra += 4 + (1 if "导师推荐信底稿" in t else 0)
                    ct -= 3; t.add("双轨探索者")
                if c02 == "2-A":
                    ct += 6 + (1 if "第三梯队座谈纪要" in t else 0)
                    ra -= 3; t.add("大院子弟标签")
                elif c02 == "2-B": ra += 7; ct -= 4; t.add("法治骨气")
                else: ct += 3; ra -= 5; t.add("老辈训诫")
                dp_v1[(clamp(ct), clamp(ra), proj(t, keep_v2))] += 1

    keep_v3 = {
        "书生执拗", "老辈训诫", "商品经济探索先声", "中宣部挂号", "破格外放序列",
        "边缘平调序列", "滑头避险定性", "大院子弟标签", "法治骨气", "双轨探索者",
        "导师推荐信底稿", "庇护者的契约", "滑头风评", "地方招商宿怨", "脱离工农议论",
        "青年统战滞后", "铁腕履历", "冷酷官僚风评"
    }
    dp_v2 = defaultdict(int)
    for (ct, ra, t1), w in dp_v1.items():
        for m2 in ["A", "B"]:
            for c03 in ["3-A", "3-B", "3-C"]:
                for p_a in ["A-1", "A-2"]:
                    for p_b in ["B-1", "B-2"]:
                        for c04_1 in ["4-1A", "4-1B"]:
                            for c04_2 in ["4-A", "4-B", "4-C"]:
                                ct2, ra2 = ct, ra
                                t = set(t1)
                                if m2 == "A": t.add("温州调研原件")
                                else: t.add("预审口径单")
                                if c03 == "3-A":
                                    ra2 += 7; ct2 -= 8 + (2 if "书生执拗" in t else 0)
                                    t.update(["风骨编辑部", "中宣部挂号"])
                                elif c03 == "3-B":
                                    ct2 += 4 + (2 if "温州调研原件" in t else 0)
                                    ra2 -= 4 + (2 if "考察保留" in t else 0)
                                    t.add("滑头风评")
                                else:
                                    ra2 += 6 + (2 if ("温州调研原件" in t or "第三梯队座谈纪要" in t) else 0)
                                    ct2 -= 3; t.update(["商品经济探索先声", "筹会透支"])
                                if p_a == "A-1": ra2 += 2; ct2 -= 2; t.add("地方招商宿怨")
                                else: ct2 += 2; ra2 -= 2
                                if p_b == "B-1": ra2 += 3; ct2 -= 3; t.add("脱离工农议论")
                                else: ct2 += 3; ra2 -= 3; t.add("青年统战滞后")
                                if "滑头风评" in t: ct2 -= 2
                                if "筹会透支" in t: ra2 -= 2
                                if c04_1 == "4-1A": ct2 += 3; ra2 -= 4
                                else:
                                    ra2 += 2; ct2 -= 2
                                    if "预审口径单" in t or "退稿油印刊物" in t: ct2 += 2
                                if c04_2 == "4-A":
                                    ct2 += 10; ra2 -= 15
                                    t.update(["铁腕履历", "破格外放序列", "冷酷官僚风评", "经贸法治底盘"])
                                elif c04_2 == "4-B":
                                    ra2 += 10; ct2 -= 15; t.update(["庇护者的契约", "十年冷板凳"])
                                else:
                                    ct2 -= 3; ra2 -= 3; t.update(["边缘平调序列", "滑头避险定性"])
                                dp_v2[(clamp(ct2), clamp(ra2), proj(t, keep_v3))] += w

    keep_v4 = {
        "边缘平调序列", "报批越界通报", "滑头避险定性", "破格外放序列", "不务正业非议",
        "双轨探索者", "现代治理工具箱", "老辈训诫", "老同志的信赖档案", "法治骨气",
        "导师推荐信底稿", "外宣基本功", "精准反制经验", "外宣僵化印象", "守旧平庸标签",
        "涉外政治风险", "大院子弟标签", "庇护者的契约", "商品经济探索先声", "滑头风评",
        "苏南经济底稿", "经贸法治底盘", "地方招商宿怨", "脱离工农议论", "青年统战滞后",
        "清高孤僻风评"
    }
    def canon_s1(t):
        out = set()
        if "边缘平调序列" in t: out.add("EDGE")
        if "报批越界通报" in t: out.add("越界")
        if "滑头避险定性" in t: out.add("滑头避险定性")
        if any(k in t for k in ("破格外放序列", "不务正业非议", "脱离工农议论", "清高孤僻风评")): out.add("S08_PEN")
        if any(k in t for k in ("苏南经济底稿", "经贸法治底盘")): out.add("ECO_BASE")
        if any(k in t for k in ("老辈训诫", "老同志的信赖档案")): out.add("OLD_TRUST")
        if "老同志的信赖档案" in t: out.add("老同志的信赖档案")
        if any(k in t for k in ("双轨探索者", "现代治理工具箱")): out.add("DUAL_TOOL")
        if any(k in t for k in ("外宣基本功", "精准反制经验")): out.add("FX_SKILL")
        if "大院子弟标签" in t: out.add("大院子弟标签")
        if "滑头风评" in t: out.add("滑头风评")
        if "地方招商宿怨" in t: out.add("地方招商宿怨")
        if "青年统战滞后" in t: out.add("青年统战滞后")
        return frozenset(out)

    s1_acc = defaultdict(lambda: [0, 0, 0])
    for (ct2, ra2, t2), w in dp_v2.items():
        for m3 in ["A", "B"]:
            c05_opts = ["5-A", "5-B"] + (["5-C"] if ct2 > 35 else [])
            for c05 in c05_opts:
                for pc in ["C-1", "C-2"]:
                    for pd in ["D-1", "D-2"]:
                        ct3, ra3 = ct2, ra2
                        t = set(t2)
                        if m3 == "A": t.add("文官制度底稿")
                        else: t.add("外宣案例剪报")
                        if "书生执拗" in t: ct3 -= 2
                        if "老辈训诫" in t: ct3 += 2
                        if c05 == "5-A": ct3 += 3; ra3 -= 3; t.add("外宣僵化印象")
                        elif c05 == "5-B":
                            ra3 += 5 + (2 if "外宣案例剪报" in t else 0)
                            ct3 -= 3; t.update(["精准反制经验", "外宣基本功", "涉外政治风险"])
                        else:
                            ra3 += 8; ct3 -= 6 + (4 if "中宣部挂号" in t else 0)
                            t.add("报批越界通报")
                        if pc == "C-1": ra3 += 2; ct3 -= 2; t.add("涉外口径微瑕")
                        else: ct3 += 2; ra3 -= 2
                        if pd == "D-1": ra3 += 2; ct3 -= 2; t.add("不务正业非议")
                        else: ct3 += 2; ra3 -= 2; t.add("守旧平庸标签")
                        if "商品经济探索先声" in t: ra3 += 2
                        ct3 = clamp(ct3)
                        c06_opts = ["6-B", "6-C"] + (["6-A"] if ct3 > 35 else [])
                        for c06 in c06_opts:
                            t_end = set(t)
                            if c06 == "6-A": t_end.update(["现代治理工具箱", "不务正业非议"])
                            elif c06 == "6-B": t_end.update(["老同志的信赖档案", "守旧平庸标签"])
                            else: t_end.update(["苏南经济底稿", "清高孤僻风评"])
                            c_adj = max(-4, min(4, (clamp(ct3) - 50) // 4))
                            r_adj = max(-4, min(4, (clamp(ra3) - 50) // 4))
                            c_flag = canon_s1(t_end)
                            s1_acc[c_flag][0] += c_adj * w
                            s1_acc[c_flag][1] += r_adj * w
                            s1_acc[c_flag][2] += w

    s1_compact = {}
    for c_flag, (sc, sr, sw) in s1_acc.items():
        s1_compact[c_flag] = (round(sc / sw), round(sr / sw), sw)

    print(f"\n=== 全六卷联合路径穷举仿真 ===", flush=True)
    print(f"阶段一分支压缩后独立等效特征态: {len(s1_compact)} 种 (含终局B早退路径 {s1_b_count} 组基线)", flush=True)

    def step_dp(dp, fn, keep):
        nxt = defaultdict(int)
        for state, w in dp.items():
            for (c, l, f, r, flags) in fn(*state):
                nxt[(clamp(c), clamp(l), clamp(f), clamp(r), proj(flags, keep))] += w
        return nxt

    # 07 -> 08
    keep_08 = {
        "滑头避险定性", "ECO_BASE", "老同志的信赖档案", "DUAL_TOOL", "FX_SKILL",
        "大院子弟标签", "滑头风评", "地方招商宿怨", "青年统战滞后",
        "公交录像带", "城投挪用线索", "老同志口风", "机关震荡反弹", "土地融资依赖", "建委隐形积怨"
    }
    dp = defaultdict(int)
    for s1_flags, (c_adj, r_adj, w) in s1_compact.items():
        for inv in [("A", "B"), ("A", "C"), ("B", "C")]:
            c = clamp(55 + c_adj)
            l, f = 60, 60
            r = clamp(50 + r_adj)
            t4 = set(s1_flags)
            if "EDGE" in t4: c -= 3
            if "越界" in t4: c -= 2
            for act in inv:
                if act == "A": t4.add("公交录像带")
                elif act == "B":
                    f -= 3 if "ECO_BASE" in t4 else 5
                    t4.add("城投挪用线索")
                else:
                    l += 5 + (3 if "OLD_TRUST" in t4 else 0)
                    t4.add("老同志口风")
            c, l, f, r = clamp(c), clamp(l), clamp(f), clamp(r)
            s08_opts = ["1-B", "1-C"] + (["1-A"] if "公交录像带" in t4 else []) + (["1-D"] if "城投挪用线索" in t4 else [])
            for c08 in s08_opts:
                c8, l8, f8, r8 = c, l, f, r
                t8 = set(t4)
                if "S08_PEN" in t8: l8 -= 2
                if c08 == "1-A": c8 += 5; r8 += 5; l8 -= 10; t8.add("机关震荡反弹")
                elif c08 == "1-B": l8 += 5; c8 += 1; r8 -= 5; t8.add("整顿流于形式")
                elif c08 == "1-C": r8 += 8; f8 -= 10; l8 -= 5; t8.add("土地融资依赖")
                else:
                    r8 += 5 + (1 if "DUAL_TOOL" in t8 else 0)
                    f8 += 6; l8 -= 4; t8.add("建委隐形积怨")
                dp[(clamp(c8), clamp(l8), clamp(f8), clamp(r8), proj(t8, keep_08))] += w

    # 09
    keep_09 = {
        "ECO_BASE", "老同志的信赖档案", "DUAL_TOOL", "FX_SKILL", "大院子弟标签", "滑头风评", "地方招商宿怨", "青年统战滞后",
        "城投挪用线索", "老同志口风", "土地融资依赖", "建委隐形积怨", "滑头避险定性", "彻底停工", "省府裂痕", "设备共管方案", "折中敷衍疑虑", "地方重组意向"
    }
    def fn_09(c, l, f, r, t8):
        out = []
        for c09 in ["2-A", "2-B", "2-C"]:
            c9, l9, f9, r9 = c, l, f, r
            t9 = set(t8)
            if c09 == "2-A": c9 += 10; l9 -= 15; f9 -= 10; t9.update(["彻底停工", "省府裂痕"])
            elif c09 == "2-B": l9 += 10; f9 += 5; c9 -= 10; t9.add("地方重组意向")
            else: r9 += 4; f9 += 5; c9 -= 5; l9 -= 5; t9.update(["设备共管方案", "折中敷衍疑虑"])
            out.append((c9, l9, f9, r9, t9))
        return out
    dp = step_dp(dp, fn_09, keep_09)

    # 10
    keep_10 = {
        "老同志的信赖档案", "DUAL_TOOL", "FX_SKILL", "大院子弟标签", "滑头风评", "地方招商宿怨", "青年统战滞后",
        "老同志口风", "建委隐形积怨", "省府裂痕", "彻底停工", "设备共管方案", "抗辩部委记名", "连带问责留档"
    }
    def fn_10(c, l, f, r, t9):
        out = []
        s10_opts = ["3-A"] + (["3-B"] if ("城投挪用线索" in t9 or f >= 60) else []) + (["3-C"] if "设备共管方案" in t9 else [])
        for c10 in s10_opts:
            c10_v, l10_v, f10_v, r10_v = c, l, f, r
            t10 = set(t9)
            if "土地融资依赖" in t10: f10_v -= 3
            if "折中敷衍疑虑" in t10 or "滑头避险定性" in t10: c10_v -= 2
            if c10 == "3-A": c10_v += 15; l10_v -= 10; t10.add("连带问责留档")
            elif c10 == "3-B":
                l10_v += 15; f10_v += 5 + (2 if "ECO_BASE" in t10 else 0)
                c10_v -= 10 + (5 if "地方重组意向" in t10 else 0)
                t10.add("抗辩部委记名")
            else:
                f10_v += 10 + (2 if "ECO_BASE" in t10 else 0)
                l10_v -= 3
                c10_v -= 5 + (5 if "地方重组意向" in t10 else 0)
                t10.add("资产切割审计尾账")
            out.append((c10_v, l10_v, f10_v, r10_v, t10))
        return out
    dp = step_dp(dp, fn_10, keep_10)

    # 11
    keep_11 = {
        "老同志的信赖档案", "DUAL_TOOL", "FX_SKILL", "大院子弟标签", "滑头风评", "地方招商宿怨", "青年统战滞后",
        "老同志口风", "彻底停工", "设备共管方案", "抗辩部委记名", "官场寒蝉效应", "预备费见底", "雨中聚众影像"
    }
    def fn_11(c, l, f, r, t10):
        out = []
        s11_opts = ["4-B", "4-C"] + (["4-A"] if f > 40 else [])
        for c11 in s11_opts:
            c11_v, l11_v, f11_v, r11_v = c, l, f, r
            t11 = set(t10)
            if "建委隐形积怨" in t11 or "省府裂痕" in t11: l11_v -= 2
            half11 = (l11_v <= 35)
            if c11 == "4-A": c11_v += 5; l11_v += 20; f11_v -= 12; t11.add("预备费见底")
            elif c11 == "4-B": f11_v += 5; r11_v += (2 if half11 else 5); l11_v -= 15; t11.add("雨中聚众影像")
            else: c11_v += 5; l11_v -= 10; r11_v -= 5; t11.add("官场寒蝉效应")
            out.append((c11_v, l11_v, f11_v, r11_v, t11))
        return out
    dp = step_dp(dp, fn_11, keep_11)

    # 12
    keep_12 = {
        "FX_SKILL", "大院子弟标签", "滑头风评", "地方招商宿怨", "青年统战滞后", "连带问责留档",
        "彻底停工", "设备共管方案", "预备费见底", "雨中聚众影像", "激进政改旗手", "制度精算样本", "形式主义诟病"
    }
    def fn_12(c, l, f, r, t11):
        out = []
        s12_opts = ["5-B", "5-C"] + (["5-A"] if c > 40 else [])
        for c12 in s12_opts:
            c12_v, l12_v, f12_v, r12_v = c, l, f, r
            t12 = set(t11)
            if "抗辩部委记名" in t12: c12_v -= 2
            if "官场寒蝉效应" in t12: r12_v -= 2
            half12 = (l12_v <= 35)
            if c12 == "5-A":
                r12_v += (7 if half12 else 15); c12_v -= 15
                l12_v -= (5 if "老同志口风" in t12 else 10)
                t12.update(["激进政改旗手", "党管干部质疑"])
            elif c12 == "5-B":
                c12_v += 5
                base_r = 2 if half12 else 5
                bonus_r = (1 if half12 else 2) if "DUAL_TOOL" in t12 else 0
                r12_v += base_r + bonus_r
                l12_v += (3 if ("老同志口风" in t12 or "老同志的信赖档案" in t12) else -5)
                t12.update(["制度精算样本", "形式主义诟病"])
            else:
                c12_v += 5; l12_v += 5; r12_v -= 10; t12.add("改革保守退缩")
            out.append((c12_v, l12_v, f12_v, r12_v, t12))
        return out
    dp = step_dp(dp, fn_12, keep_12)

    # 13-1, 13-2, 13-3, 14
    print(f"dp at 12 size: {len(dp)}", flush=True)
    keep_13_1 = (keep_12 - {"雨中聚众影像", "彻底停工", "设备共管方案"}) | {"P1_C"}
    def fn_13_1(c, l, f, r, t):
        out = []
        cp = c - (2 if "雨中聚众影像" in t else 0)
        has_fx = ("FX_SKILL" in t)
        opts = ["1-A", "1-B"] + (["1-C"] if ("设备共管方案" in t or "彻底停工" in t) else [])
        for p1 in opts:
            tc = set(t)
            if p1 == "1-A": out.append((cp - 6, l, f, r + 3, tc))
            elif p1 == "1-B": out.append((cp + 1, l, f, r - 2, tc))
            else: tc.add("P1_C"); out.append((cp + 2 + (1 if has_fx else 0), l, f - 1, r + 3, tc))
        return out
    dp = step_dp(dp, fn_13_1, keep_13_1)

    keep_13_2 = (keep_13_1 - {"制度精算样本"}) | {"P2_C"}
    def fn_13_2(c, l, f, r, t):
        out = []
        has_fx = ("FX_SKILL" in t)
        opts = ["2-A", "2-B"] + (["2-C"] if "制度精算样本" in t else [])
        for p2 in opts:
            tc = set(t)
            if p2 == "2-A": out.append((c - 8, l, f, r + 4, tc))
            elif p2 == "2-B": out.append((c + 2, l - 2, f, r - 3, tc))
            else: tc.add("P2_C"); out.append((c + 2 + (1 if has_fx else 0), l - 1, f, r + 3, tc))
        return out
    dp = step_dp(dp, fn_13_2, keep_13_2)

    keep_13_3 = {
        "大院子弟标签", "滑头风评", "外宣高手", "形式主义诟病",
        "激进政改旗手", "地方招商宿怨", "青年统战滞后", "连带问责留档"
    }
    def fn_13_3(c, l, f, r, t):
        out = []
        for p3 in ["3-A", "3-B", "3-C"]:
            tc = set(t)
            if p3 == "3-A": out.append((c - 2, l, f, r - 2, tc))
            elif p3 == "3-B": out.append((c + 1, l, f, r - 2, tc))
            else:
                lp = l - (4 + (1 if "预备费见底" in tc else 0))
                rp = r + 4 + (2 if ("P1_C" in tc and "P2_C" in tc) else 0)
                if "P1_C" in tc and "P2_C" in tc: tc.add("外宣高手")
                out.append((c + 2, lp, f, rp, tc))
        return out
    dp = step_dp(dp, fn_13_3, keep_13_3)
    print(f"dp at 13 size: {len(dp)}", flush=True)

    # 14 -> 17th Congress Gateway
    def canon_s5(t):
        out = set()
        if "形式主义诟病" in t or "滑头风评" in t: out.add("FORM_OR_SLICK")
        if "无暇履历" in t or "宏观定力" in t: out.add("EXP_BONUS")
        if "派系结盟猜忌" in t or "地方招商宿怨" in t: out.add("FACTION_GRUDGE")
        if "改革盟约" in t: out.add("改革盟约")
        if "大院子弟标签" in t: out.add("大院子弟标签")
        if "外宣高手" in t: out.add("外宣高手")
        if "连带问责留档" in t: out.add("连带问责留档")
        if "青年统战滞后" in t: out.add("V6_R2_PEN")
        if "党管干部质疑" in t: out.add("党管干部质疑")
        if "改革保守退缩" in t: out.add("改革保守退缩")
        return frozenset(out)

    e17_counts = defaultdict(int)
    dp_s5 = defaultdict(int)
    c_lt_45 = 0
    f_lt_35 = 0
    f_lt_30 = 0
    c_ge_62 = 0
    l_ge_35 = 0
    r_ge_50 = 0
    for (cp, lp, fp, rp, tp), w in dp.items():
        for c14 in ["6-A", "6-B", "6-C"]:
            c14_v, l14_v, f14_v, r14_v = cp, lp, fp, rp
            t14 = set(tp)
            if c14 == "6-A": r14_v += 1; c14_v -= 2; t14.update(["改革盟约", "派系结盟猜忌"])
            elif c14 == "6-B": c14_v += 2; r14_v -= 2; t14.add("无暇履历")
            else: c14_v += 1; r14_v -= 1; t14.add("宏观定力")
            c14_v, l14_v, f14_v, r14_v = clamp(c14_v), clamp(l14_v), clamp(f14_v), clamp(r14_v)

            if c14_v < 45: c_lt_45 += w
            if f14_v < 35: f_lt_35 += w
            if f14_v < 30: f_lt_30 += w
            if c14_v >= 62: c_ge_62 += w
            if l14_v >= 35: l_ge_35 += w
            if r14_v >= 50: r_ge_50 += w

            e17 = evaluate_17th_congress(c14_v, l14_v, f14_v, r14_v, t14)
            if e17 != "PROCEED_TO_VOL5":
                e17_counts[e17] += w
            else:
                dp_s5[(c14_v, l14_v, r14_v, canon_s5(t14))] += w

    w_v5_start = sum(dp_s5.values())
    w_17_total = sum(e17_counts.values()) + w_v5_start
    print(f"\n=== 十七大节点分流统计 (17th Congress Gate Distribution) ===", flush=True)
    print(f"到达十七大路径权重总计: {w_17_total:,}", flush=True)
    print(f"  c < 45: {c_lt_45:,} ({c_lt_45/w_17_total*100:.2f}%)")
    print(f"  f < 35: {f_lt_35:,} ({f_lt_35/w_17_total*100:.2f}%)")
    print(f"  f < 30: {f_lt_30:,} ({f_lt_30/w_17_total*100:.2f}%)")
    print(f"  c >= 62: {c_ge_62:,} ({c_ge_62/w_17_total*100:.2f}%)")
    print(f"  l >= 35: {l_ge_35:,} ({l_ge_35/w_17_total*100:.2f}%)")
    print(f"  r >= 50: {r_ge_50:,} ({r_ge_50/w_17_total*100:.2f}%)")
    for k, v in sorted(e17_counts.items()):
        print(f"  {k}: {v:,} ({v / w_17_total * 100:.2f}%)", flush=True)
    print(f"  PROCEED_TO_VOL5: {w_v5_start:,} ({w_v5_start / w_17_total * 100:.2f}%)", flush=True)
    print(f"dp_s5 size: {len(dp_s5)}", flush=True)

    # Vol 5 Layered DP
    def step_v5(dp, fn, keep):
        nxt = defaultdict(int)
        for (c, l, r, flags), w in dp.items():
            for (c_v, l_v, r_v, t_v) in fn(c, l, r, flags):
                nxt[(clamp(c_v), clamp(l_v), clamp(r_v), proj(t_v, keep))] += w
        return nxt

    # 15
    keep_15 = {
        "监督局带病档案", "改革盟约", "FACTION_GRUDGE", "使节团提问清单",
        "大院子弟标签", "外宣高手", "V6_R2_PEN", "连带问责留档", "改革保守退缩"
    }
    def fn_14a_15(c, l, r, s5_rel):
        out = []
        l_enter = clamp(l + 8) if l < 50 else l
        for inv5 in [("A", "B"), ("A", "C"), ("B", "C")]:
            t5 = set(s5_rel)
            for a5 in inv5:
                if a5 == "A": t5.add("监督局带病档案")
                elif a5 == "B": t5.add("基层测评原始样表")
                else: t5.add("使节团提问清单")
            r_base = r - (2 if "FORM_OR_SLICK" in t5 else 0)
            c_base = c - (3 if "党管干部质疑" in t5 else 0)
            for c15 in ["15-A", "15-B", "15-C"]:
                c15_v, l15_v, r15_v = c_base, l_enter, r_base
                t15 = set(t5)
                if c15 == "15-A":
                    r15_v += 6; c15_v -= 8; l15_v -= 5
                elif c15 == "15-B":
                    c15_v += 5 + (2 if ("基层测评原始样表" in t15 or "EXP_BONUS" in t15) else 0)
                    r15_v += 5; l15_v -= 2
                else:
                    c15_v += 4; l15_v += 4; r15_v -= 8; t15.add("V6_R2_PEN")
                out.append((c15_v, l15_v, r15_v, t15))
        return out
    dp_15 = step_v5(dp_s5, fn_14a_15, keep_15)
    print(f"dp_15 size: {len(dp_15)}", flush=True)

    # 16
    keep_16 = {
        "监督局带病档案", "使节团提问清单", "大院子弟标签", "外宣高手",
        "V6_R2_PEN", "连带问责留档", "跨省空降派系芥蒂", "改革保守退缩"
    }
    def fn_16(c, l, r, t15):
        out = []
        c_base = c + (2 if "监督局带病档案" in t15 else 0)
        s16_opts = ["16-A", "16-C"] + (["16-B"] if ("改革盟约" in t15 and c_base > 40) else [])
        for c16 in s16_opts:
            c16_v, l16_v, r16_v = c_base, l, r
            t16 = set(t15)
            if c16 == "16-A":
                c16_v += 3; l16_v += 4; r16_v -= 4; t16.add("V6_R2_PEN")
            elif c16 == "16-B":
                r16_v += 7; c16_v += 2
                l16_v -= 2 + (1 if "FACTION_GRUDGE" in t16 else 0)
                t16.add("跨省空降派系芥蒂")
            else:
                c16_v += 4; r16_v += 2; l16_v -= 3
            out.append((c16_v, l16_v, r16_v, t16))
        return out
    dp_16 = step_v5(dp_15, fn_16, keep_16)
    print(f"dp_16 size: {len(dp_16)}", flush=True)

    # Black Swan: 【老陈的信封】
    keep_bs = {
        "使节团提问清单", "大院子弟标签", "外宣高手", "V6_R2_PEN",
        "连带问责留档", "跨省空降派系芥蒂", "大秘隐雷", "改革保守退缩"
    }
    def fn_bs(c, l, r, t16):
        out = []
        # Option A: 大义灭亲
        t_a = set(t16)
        out.append((c + 4, l - 4, r - 2, t_a))
        # Option B: 私心护短
        t_b = set(t16)
        t_b.add("大秘隐雷")
        out.append((c - 4, l + 3, r, t_b))
        # Option C: 借刀反查 (requires 监督局带病档案)
        if "监督局带病档案" in t16:
            t_c = set(t16)
            out.append((c + 2, l - 2, r + 3, t_c))
        return out
    dp_bs = step_v5(dp_16, fn_bs, keep_bs)
    print(f"dp_bs size: {len(dp_bs)}", flush=True)

    # 17: 外媒吹风会
    def canon_v6(t):
        disq = ("自揭家丑非议" in t or "连带问责留档" in t or "大秘隐雷" in t)
        r1 = ("密闭保稳惯性" in t or "自揭家丑非议" in t)
        l = ("系统内保守派侧目" in t or "跨省空降派系芥蒂" in t)
        r2 = ("V6_R2_PEN" in t)
        has_lei = ("大秘隐雷" in t)
        return (disq, r1, l, r2, has_lei)

    dp_v5 = defaultdict(int)
    for (c, l, r, t_bs), w in dp_bs.items():
        c_base = c - (2 if "大院子弟标签" in t_bs else 0)
        s17_opts = ["17-A", "17-C"] + (["17-B"] if ("外宣高手" in t_bs or r >= 60) else [])
        for c17 in s17_opts:
            c17_v, l17_v, r17_v = c_base, l, r
            t17 = set(t_bs)
            if c17 == "17-A":
                c17_v += 3; r17_v -= 4; t17.add("密闭保稳惯性")
            elif c17 == "17-B":
                r17_v += 7 + (2 if "使节团提问清单" in t17 else 0)
                c17_v += 2 - (2 if "改革保守退缩" in t17 else 0)
                l17_v -= 2; t17.add("系统内保守派侧目")
            else:
                r17_v += 5; c17_v -= 4; t17.add("自揭家丑非议")
            dp_v5[(clamp(c17_v), clamp(l17_v), clamp(r17_v), canon_v6(t17))] += w
    print(f"dp_v5 size: {len(dp_v5)}", flush=True)

    v5_counts = defaultdict(int)
    # 18th Congress Settlement
    for (c17_v, l17_v, r17_v, (disq, r1, l_pen, r2, has_lei)), w5 in dp_v5.items():
        eval_tags = set()
        if disq: eval_tags.add("自揭家丑非议")
        if has_lei: eval_tags.add("大秘隐雷")
        e18 = evaluate_18th_congress(c17_v, l17_v, 0, r17_v, eval_tags)
        if e18 == "Ending A1 (巅峰折冲 · 核心统筹)":
            v5_counts[e18] += w5 * 8
        elif e18 == "Ending A3 (提前淡出 · 倚楼晚照)":
            v5_counts[e18] += w5 * 8
        else:
            # Enters Vol 6 (正史主线 Ending A2)
            for m6 in ["A", "B"]:
                for c18_1 in ["18-1A", "18-1B"]:
                    for c18_2 in ["18-2A", "18-2B"]:
                        c18_v, l18_v, r18_v = c17_v, l17_v, r17_v
                        if r1: r18_v -= 2
                        if l_pen: l18_v -= 2
                        if r2: r18_v -= 2
                        if c18_1 == "18-1A": c18_v += 4 + (2 if m6 == "B" else 0); r18_v -= 3
                        else: r18_v += 4; c18_v -= 3
                        if c18_2 == "18-2A": r18_v += 5 + (2 if m6 == "A" else 0); l18_v -= 2; c18_v -= 2
                        else: c18_v += 4; r18_v -= 3
                        c18_v, l18_v, r18_v = clamp(c18_v), clamp(l18_v), clamp(r18_v)
                        v5_counts["Ending A2 (端方晚晴 · 稳健执印)"] += w5

    w_v5_leaves = sum(v5_counts.values())
    p_v5_enter = w_v5_start / w_17_total

    print(f"\n=== 十八大换届分流统计 (18th Congress Gate Distribution within Vol 5) ===", flush=True)
    print(f"卷五末梢加权权重总计: {w_v5_leaves:,}", flush=True)
    for k, v in sorted(v5_counts.items()):
        print(f"  {k}: {v:,} ({v / w_v5_leaves * 100:.2f}%)", flush=True)

    print(f"\n=== 全局结局归一化分布 (Normalized Playthrough Distribution across all 7 Endings) ===", flush=True)
    norm_dist = {}
    for k, v in sorted(e17_counts.items()):
        norm_dist[k] = (v / w_17_total) * 100
    for k, v in sorted(v5_counts.items()):
        norm_dist[k] = p_v5_enter * (v / w_v5_leaves) * 100

    for k, p in sorted(norm_dist.items()):
        print(f"  {k}: {p:.2f}%", flush=True)

if __name__ == "__main__":
    print("注意：以下历史手写模拟与当前网页规则不完全一致；新版结局分布请运行 pnpm test:balance。", flush=True)
    _, ok = verify_schema_and_banned_words()
    run_historical_baseline()
    simulate_all_paths()
    if not ok:
        raise SystemExit(1)
