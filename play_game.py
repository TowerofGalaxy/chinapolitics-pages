#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
play_game.py - 《浪潮与行程：李源潮仕途模拟器》(1981-2018)
终端交互式政治模拟引擎 / 交互游玩脚本
"""

import sys
import os
import json
import time

# Ensure UTF-8 output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def clamp(val):
    return max(0, min(100, val))

class GameEngine:
    def __init__(self, auto_choices=None):
        self.auto_choices = list(auto_choices) if auto_choices else None
        self.auto_idx = 0
        
        # Load variables schema
        schema_path = os.path.join(os.path.dirname(__file__), "variables.json")
        with open(schema_path, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

        # Stage 1 variables
        self.stage = 1
        self.current_vol = 1
        self.ct = 50  # 组织信任度
        self.ra = 50  # 改革锐度
        
        # Stage 2 variables
        self.c = 55   # 中央信任度
        self.l = 60   # 地方向心力 / 系统协同度
        self.f = 60   # 财政健康度
        self.r = 50   # 改革开拓度

        self.tags = set(["纯粹知识分子底色"])
        self.history = []

    def log(self, text=""):
        print(text)

    def print_header(self, title):
        self.log("\n" + "=" * 68)
        self.log(f"  {title}")
        self.log("=" * 68)

    def print_status(self):
        self.log("-" * 68)
        if self.stage == 1:
            warn = " [! 警戒：低信任度引发边缘化审查]" if self.ct <= 35 else ""
            self.log(f"【当前官场属性 · 阶段一 (1981-2000)】")
            self.log(f"  组织信任度 (cadre_trust): {self.ct}/100{warn}")
            self.log(f"  改革锐度   (reform_acumen): {self.ra}/100")
        else:
            local_name = "地方向心力" if self.current_vol <= 4 else "系统协同度"
            warn_c = " [! 预警：中央质询]" if self.c < 45 else ""
            warn_l = " [! 预警：协同受阻]" if self.l <= 35 else ""
            warn_f = " [! 危机：财政见底]" if self.f < 35 else ""
            self.log(f"【主政与中枢属性 · 阶段二 (2000-2018)】")
            if self.current_vol == 6:
                self.log("  [收官脱敏软着陆模式 · 界面数值柱淡出，重点呈示晚晴手记与案头器物]")
            self.log(f"  中央信任度 (central_trust):  {self.c}/100{warn_c}")
            self.log(f"  {local_name} (local_cohesion): {self.l}/100{warn_l}")
            self.log(f"  财政健康度 (fiscal_stability): {self.f}/100{warn_f}")
            self.log(f"  改革开拓度 (reform_drive):     {self.r}/100")
        
        active_tags = [t for t in self.tags if t in self.schema.get("tags", {})]
        if active_tags:
            self.log(f"  核心政治履历/标记: {', '.join(sorted(active_tags))}")
        self.log("-" * 68)

    def choose(self, prompt, options):
        """
        options: list of tuples (key, label, callback)
        """
        self.log(f"\n{prompt}")
        for idx, (k, label, _) in enumerate(options, 1):
            self.log(f"  [{k}] {label}")

        while True:
            if self.auto_choices is not None and self.auto_idx < len(self.auto_choices):
                choice = self.auto_choices[self.auto_idx]
                self.auto_idx += 1
                self.log(f"\n[自动演化决策] 选择: {choice}")
            else:
                try:
                    choice = input("\n请在键盘输入对应选项代号后回车: ").strip()
                except (EOFError, KeyboardInterrupt):
                    self.log("\n演化终止。")
                    sys.exit(0)

            for k, label, cb in options:
                if choice.upper() == k.upper():
                    self.history.append((k, label))
                    return cb()
            self.log(f"输入无效，请在 {[k for k, _, _ in options]} 中选择。")

    def play(self):
        self.log("=" * 68)
        self.log("  《浪潮与行程：李源潮仕途模拟器》(1981-2018)")
        self.log("  —— 严谨历史政治模拟 · 案头公文与权力博弈 ——")
        self.log("=" * 68)
        self.log("【核心机制提示】")
        self.log("1. 现实主义铁律：绝无双赢选项，每项决策均伴随即时代价与后续反噬。")
        self.log("2. 两阶段生命周期：前二十年积累信任与锐度，主政江淮与调任中枢后承接四维博弈。")
        self.log("3. 严格去程式化：一切博弈停留在公文、编制、会议记录与制度推演上。")
        
        # Vol 1
        self.current_vol = 1
        self.vol1_run()
        if "象牙塔学者" in self.tags:
            return

        # Vol 2
        self.current_vol = 2
        self.vol2_run()

        # Vol 3
        self.current_vol = 3
        self.vol3_run()

        # Transition to Stage 2
        self.transition_to_stage2()

        # Vol 4
        self.current_vol = 4
        e17 = self.vol4_run()
        if e17 != "PROCEED_TO_VOL5":
            self.render_grand_ending(e17)
            return

        # Vol 5
        self.current_vol = 5
        e18 = self.vol5_run()
        if e18 in ("Ending A1 (巅峰折冲 · 核心统筹)", "Ending A3 (提前淡出 · 倚楼晚照)"):
            self.render_grand_ending(e18)
            return

        # Vol 6
        self.current_vol = 6
        final_ending = self.vol6_run()
        self.render_grand_ending(final_ending)

    # ------------------ VOLUME 1 ------------------
    def vol1_run(self):
        self.print_header("第一卷：书斋与激流 (1977-1982)")
        self.print_status()

        # Scene 01 AP
        self.log("\n【场景 01 前置 · 1981年10月 复旦大学数学系资料室】")
        self.log("五百七十万青年走进考场，最终仅有二十七万余人跨入大学校门。")
        self.log("毕业分配大表下达前夕，系党总支办公室的绿呢台子前放着三份绝密档案。你有 1 点精力(AP)翻阅其中一份：")
        
        def ap_a():
            self.tags.add("退稿油印刊物")
            self.log("\n>>> 你翻开了那份带有油印痕迹的未定稿诗刊，记下了数名热血青年的联络信箱。")
        def ap_b():
            self.tags.add("导师推荐信底稿")
            self.log("\n>>> 你仔细阅读了谷超豪先生起草的留校推荐信底稿，先生对微分方程学术传承寄予厚望。")
        def ap_c():
            self.tags.add("第三梯队座谈纪要")
            self.log("\n>>> 你查阅了市委组织部有关青年干部‘第三梯队’首期拟定选拔标准的红头调研纪要。")

        self.choose("【前期信息搜集 (AP=1)】", [
            ("A", "抽查抽屉夹层中的油印刊物底稿 (获取：[退稿油印刊物])", ap_a),
            ("B", "核对谷超豪先生拟定的公派选拔底表 (获取：[导师推荐信底稿])", ap_b),
            ("C", "调阅校党委组织部红头调研纪要 (获取：[第三梯队座谈纪要])", ap_c)
        ])

        # Scene 01 Choice
        self.log("\n【场景 01 · 毕业分配去向抉择】")
        self.log("复旦大学第一教学楼走廊里，晚秋风卷着梧桐叶贴在玻璃窗上。")
        self.log("校党委书记将三份去向表推到你面前：基础数学留校助教、团委机关直管专干、赴德公派预备。")

        def s01_a():
            self.ra += 5; self.ct -= 4
            self.tags.add("书生执拗")
            self.log("\n>>> 你坚持要求在学术与团学之间保持双肩挑。总支书记合上钢笔帽，叹了口气。")
        def s01_b():
            self.ct += 4; self.ra -= 3
            self.tags.add("考察保留")
            self.log("\n>>> 你工工整整写下‘服从组织挑选’。组织部专员在你的考核表右上角画了一个实心圆圈。")
        def s01_c():
            bonus = 1 if "导师推荐信底稿" in self.tags else 0
            self.ra += 4 + bonus; self.ct -= 3
            self.tags.add("双轨探索者")
            self.log("\n>>> 你提交了一份《关于数理逻辑在基层团学管理中量化应用的构想报告》。")
        def s01_d():
            self.tags.add("象牙塔学者")
            self.log("\n>>> 你在表格上勾选了‘纯学术留校’，坚决拒绝了任何党团兼职。")
            self.render_grand_ending("Ending B (象牙塔的余生)")

        opts = [
            ("1-A", "坚持保留偏微分方程课题组助教编制，兼职系团总支副书记", s01_a),
            ("1-B", "彻底服从分配，专职调入校团委任宣传部长，人事档案全迁", s01_b),
            ("1-C", "递交《关于数理逻辑在基层团学管理中量化应用的构想报告》", s01_c),
            ("1-D", "当场拒绝政治调配，申请纯学术留校攻读偏微分方程硕士", s01_d)
        ]
        self.choose("【场景 01 决策】", opts)
        if "象牙塔学者" in self.tags:
            return

        self.ct, self.ra = clamp(self.ct), clamp(self.ra)
        self.print_status()

        # Scene 02
        self.log("\n【场景 02 · 1981年10月 上海 静安区弄堂老宅】")
        self.log("父亲李干成坐在藤椅上，手里拿着一串暗红色的旧钥匙。")
        self.log("‘援朝，耀邦同志在中央反复讲干部年轻化、知识化，中组部今年专门发了文。’")
        self.log("‘可有些门，跨进去了，一辈子就由不得你自己的性子了。’")

        def s02_a():
            bonus = 1 if "第三梯队座谈纪要" in self.tags else 0
            self.ct += 6 + bonus; self.ra -= 3
            self.tags.add("大院子弟标签")
            self.log("\n>>> 你双手接下信件。老部下的关照为你铺平了第一步，但也贴上了大院子弟的无形标签。")
        def s02_b():
            self.ra += 7; self.ct -= 4
            self.tags.add("法治骨气")
            self.log("\n>>> 你委婉退回信件，表示愿从最基层的团宣干事做起。父亲在烟灰缸上重重磕了磕烟斗。")
        def s02_c():
            self.ct += 3; self.ra -= 5
            self.tags.add("老辈训诫")
            self.log("\n>>> 父亲提笔在《滕王阁序》字帖空白处写下：‘东隅已逝，桑榆非晚’。")

        self.choose("【场景 02 决策】", [
            ("2-A", "顺从接下信件，承诺按老同志指点的机关规矩做事", s02_a),
            ("2-B", "婉拒条子，表明要在复旦与团市委一线靠文字与实干立足", s02_b),
            ("2-C", "既不退信也不登门，求教治事心法", s02_c)
        ])
        self.ct, self.ra = clamp(self.ct), clamp(self.ra)
        self.print_status()

    # ------------------ VOLUME 2 ------------------
    def vol2_run(self):
        self.print_header("第二卷：前门东大街的风 (1983-1990)")
        self.print_status()

        # Scene 03 AP
        self.log("\n【场景 03 前置 · 1985年秋 北京 前门东大街团中央机关大楼】")
        self.log("十二届三中全会通过经济体制改革决定，城市商品经济与青年个体创业浪潮席卷全国。")
        self.log("办公桌上摆着两份加急材料，你有 1 点精力(AP)翻阅：")

        def ap2_a():
            self.tags.add("温州调研原件")
            self.log("\n>>> 你掌握了温州苍南个体户八人雇工线的原始账目调查底稿。")
        def ap2_b():
            self.tags.add("预审口径单")
            self.log("\n>>> 你掌握了中央书记处对青年思想动态的预审口径纪要。")

        self.choose("【前期信息搜集 (AP=1)】", [
            ("A", "翻阅温州苍南个体户八人雇工线原始账目调查底表 (获取：[温州调研原件])", ap2_a),
            ("B", "查阅中央书记处对全国高校青年思想动态的预审口径纪要 (获取：[预审口径单])", ap2_b)
        ])

        # Scene 03 Choice
        self.log("\n【场景 03 · 青年创业与雇工红线风波】")
        self.log("全国青年个体劳动者座谈会筹备会上，章华妹式个体户雇工突破8人红线成为争议焦点。")

        def s03_a():
            pen = 2 if "书生执拗" in self.tags else 0
            self.ra += 7; self.ct -= (8 + pen)
            self.tags.update(["风骨编辑部", "中宣部挂号"])
            self.log("\n>>> 《中国青年》整版刊发长篇通讯，在中宣部例会上被点名批评‘政治把关不严’。")
        def s03_b():
            bonus = 2 if "温州调研原件" in self.tags else 0
            pen = 2 if "考察保留" in self.tags else 0
            self.ct += 4 + bonus; self.ra -= (4 + pen)
            self.tags.add("滑头风评")
            self.log("\n>>> 会议通报被压缩为三段式汇报，平稳过关，但机关内私下议论其‘油滑避险’。")
        def s03_c():
            bonus = 2 if ("温州调研原件" in self.tags or "第三梯队座谈纪要" in self.tags) else 0
            self.ra += 6 + bonus; self.ct += 1 - 4
            self.tags.update(["商品经济探索先声", "筹会透支"])
            self.log("\n>>> 你以‘有计划的商品经济’理论包装，组织八省青年企业家调研，透支了部门活动经费。")

        self.choose("【场景 03 决策】", [
            ("3-A", "力挺雇工探索，指令《中国青年》刊发长篇通讯呼吁松绑", s03_a),
            ("3-B", "严格按照传统八人限额压制报道，定性为‘资本主义自发倾向苗头’", s03_b),
            ("3-C", "折中包装：以‘发展多种经济成分与青年互助组’名义组织八省调研", s03_c)
        ])

        # Desk Memo 01
        self.log("\n【案头批文 01 · 1986年夏 沿海合资玩具厂停工仲裁】")
        def p_a1():
            self.ra += 2; self.ct -= 2
            self.tags.add("地方招商宿怨")
            self.log("\n>>> 批复下发：由团委工农青年部进驻工会查验合同，外商以撤资向省委施压。")
        def p_a2():
            self.ct += 2; self.ra -= 2
            self.log("\n>>> 批复下发：协调市劳动局设立疏导基金，平息事态。")
        self.choose("【案头批文 01 签批】", [
            ("A-1", "签批支持依法维权，由团省委工农青年部进驻监督劳动仲裁", p_a1),
            ("A-2", "签批‘顾全引资大局’，协调地方劳动局与资方闭门调解", p_a2)
        ])

        # Desk Memo 02
        self.log("\n【案头批文 02 · 1987年春 全国青联青年知识分子界别名额方案】")
        def p_b1():
            self.ra += 3; self.ct -= 3
            self.tags.add("脱离工农议论")
            self.log("\n>>> 名额向中科院青年科学家及先锋人文学者倾斜，老同志提出‘脱离工农主体’质询。")
        def p_b2():
            self.ct += 3; self.ra -= 3
            self.tags.add("青年统战滞后")
            self.log("\n>>> 维持劳模与传统国企青年主力占比，多所高校青年教师学会联合表达失落。")
        self.choose("【案头批文 02 签批】", [
            ("B-1", "向高校青年科研骨干与归国学者倾斜，扩大自由学者界别", p_b1),
            ("B-2", "严格维持传统工农劳模与体制内单位青年骨干绝对多数", p_b2)
        ])

        # Passive penalty checks
        if "滑头风评" in self.tags: self.ct -= 2
        if "筹会透支" in self.tags: self.ra -= 2

        # Scene 04-1
        self.log("\n【场景 04-1 · 1989年5月 北京 东城区海运仓 中国青年报社】")
        def s04_1a():
            self.ct += 3; self.ra -= 4
            self.log("\n>>> 你签发值班指令：所有排版大样必须有社长与总编辑双签字方可上机。")
        def s04_1b():
            bonus = 2 if ("预审口径单" in self.tags or "退稿油印刊物" in self.tags) else 0
            self.ra += 2; self.ct += -2 + bonus
            self.log("\n>>> 你留在海运仓编委会会议室，通宵核对两篇青年思想动态专报清样。")
        self.choose("【场景 04-1 抉择】", [
            ("4-1A", "连夜进驻报社，执行严格发稿审批与双签字流程，封存敏感评论", s04_1a),
            ("4-1B", "留在夜班编辑部，与老编辑通宵修改评论清样，呈报青年心态内参", s04_1b)
        ])

        # Scene 04-2
        self.log("\n【场景 04-2 · 1990年夏 团中央书记处换届与去向抉择】")
        def s04_2a():
            self.ct += 10; self.ra -= 15
            self.tags.update(["铁腕履历", "破格外放序列", "冷酷官僚风评", "经贸法治底盘"])
            self.log("\n>>> 你选择外放外经贸部外资司，经历了残酷的涉外法治磨砺与外资审批大考。")
        def s04_2b():
            self.ra += 10; self.ct -= 15
            self.tags.update(["庇护者的契约", "十年冷板凳"])
            self.log("\n>>> 你选择调任中央外宣阵地，进入东华门与沙滩北街的漫长蓄力期。")
        def s04_2c():
            self.ct -= 3; self.ra -= 3
            self.tags.update(["边缘平调序列", "滑头避险定性"])
            self.log("\n>>> 你选择申请平调中央级群团研究机构，档案被归入‘暂缓重用考察’序列。")
        self.choose("【场景 04-2 分流】", [
            ("4-A", "服从组织特批，外放外经贸部外资司历练 (特异支线：[铁腕履历])", s04_2a),
            ("4-B", "接受中央对外宣传领导小组一局局长调任 (正史主线：[庇护者的契约])", s04_2b),
            ("4-C", "以家庭身体为由申请平调全国总工会宣教部 (保稳支线：[边缘平调序列])", s04_2c)
        ])

        self.ct, self.ra = clamp(self.ct), clamp(self.ra)
        self.print_status()

    # ------------------ VOLUME 3 ------------------
    def vol3_run(self):
        self.print_header("第三卷：东华门沉潜与外宣破冰 (1990-2000)")
        self.print_status()

        # Scene 05 AP
        self.log("\n【场景 05 前置 · 1992年春 国务院新闻办公室（东华门办公区）】")
        self.log("西方对华制裁阴霾尚未散去，国新办作为对外发声的桥头堡承受重压。")
        self.log("你桌上放着两卷保密资料，你有 1 点精力(AP)研读：")

        def ap3_a():
            self.tags.add("文官制度底稿")
            self.log("\n>>> 你研读了英国公务员法典及新加坡淡马锡政企管理模式译稿。")
        def ap3_b():
            self.tags.add("外宣案例剪报")
            self.log("\n>>> 你梳理了三十年来外媒涉华不实报道的反制口径案例汇编。")

        self.choose("【前期信息搜集 (AP=1)】", [
            ("A", "研读国外公务员法典及新加坡政企模式译稿 (获取：[文官制度底稿])", ap3_a),
            ("B", "梳理外媒不实报道反制案例汇编 (获取：[外宣案例剪报])", ap3_b)
        ])

        if "书生执拗" in self.tags: self.ct -= 2
        if "老辈训诫" in self.tags: self.ct += 2

        # Scene 05 Choice
        self.log("\n【场景 05 · 1992年春 涉外知识产权风暴新闻发布会】")
        self.log("国新办一局局长任上，美方以‘特别301条款’为要挟，境外记者在发布会上咄咄逼人。")

        def s05_a():
            self.ct += 3; self.ra -= 3
            self.tags.add("外宣僵化印象")
            self.log("\n>>> 严格照本宣科念通稿，外媒在晚报上刊出‘照本宣科的中国官员’。")
        def s05_b():
            bonus = 2 if "外宣案例剪报" in self.tags else 0
            self.ra += 5 + bonus; self.ct -= 3
            self.tags.update(["精准反制经验", "外宣基本功", "涉外政治风险"])
            self.log("\n>>> 亮出最高法司法解释与中美知识产权谈判备忘录，外媒哑口无言。")
        def s05_c():
            pen = 4 if "中宣部挂号" in self.tags else 0
            self.ra += 8; self.ct -= (6 + pen)
            self.tags.add("报批越界通报")
            self.log("\n>>> 当场宣布开放部分文化制品保税进口试点，被上级通报批评擅自宣布涉外政策。")

        self.choose("【场景 05 决策】", [
            ("5-A", "坚守既定口径，只宣读部委联合声明，拒绝回答自由提问", s05_a),
            ("5-B", "以事实反制：出示司法解释与外资保护白皮书，正面拆解质询", s05_b),
            ("5-C", "主动出击：当场宣布开放部分文化制品保税进口试点计划", s05_c)
        ])

        # Desk Memo 03
        self.log("\n【案头批文 03 · 1994年冬 外国金融信息机构驻华数据终端准入审定】")
        def p_c1():
            self.ra += 2; self.ct -= 2
            self.tags.add("涉外口径微瑕")
            self.log("\n>>> 批复下发：允许特许金融数据专线直通，上级批复‘需注意数据主权安全’。")
        def p_c2():
            self.ct += 2; self.ra -= 2
            self.log("\n>>> 批复下发：严格实行境内镜像与安全审查。")
        self.choose("【案头批文 03 签批】", [
            ("C-1", "准予特许试点，允许在部分重点涉外涉金融机构铺设专线终端", p_c1),
            ("C-2", "驳回试点申请，坚持境外金融数据必须经国内主管部门统一镜像转接", p_c2)
        ])

        # Desk Memo 04
        self.log("\n【案头批文 04 · 1997年春 国家级表演艺术院团差额拨款与自主分配】")
        def p_d1():
            self.ra += 2; self.ct -= 2
            self.tags.add("不务正业非议")
            self.log("\n>>> 批复下发：放开国家京剧院、交响乐团商业商演与演职员创收分成。")
        def p_d2():
            self.ct += 2; self.ra -= 2
            self.tags.add("守旧平庸标签")
            self.log("\n>>> 批复下发：维持传统全额拨款保障，严控院团涉足商业演出。")
        self.choose("【案头批文 04 签批】", [
            ("D-1", "批准国家院团演职员薪酬与商演票房挂钩，放开民营资本合作", p_d1),
            ("D-2", "维持全额财政兜底，严格禁止院团私自承接商业演出", p_d2)
        ])

        if "商品经济探索先声" in self.tags: self.ra += 2

        # Scene 06
        self.log("\n【场景 06 · 1998年7月 文化部副部长任上 · 沉潜与蓄力】")
        self.log("沙滩北街办公室的电风扇吱呀转动。秘书轻声汇报：李克强同志调任河南，汪洋同志调任安徽。")
        self.log("抽屉里躺着那本翻烂的《古文观止》，‘冯唐易老’四字下画着蓝铅笔细线。")

        def s06_a():
            self.tags.update(["现代治理工具箱", "不务正业非议"])
            self.log("\n>>> 你闭门撰写完成了《现代文官考核指标与公共事务管理论考》。")
        def s06_b():
            self.tags.update(["老同志的信赖档案", "守旧平庸标签"])
            self.log("\n>>> 你潜心督办全国文保单位定级修缮工程，各派老同志对你的严谨甚为认可。")
        def s06_c():
            self.tags.update(["苏南经济底稿", "清高孤僻风评"])
            self.log("\n>>> 你以文化产业考察名义走遍苏南，完成《长江三角洲县域产业与招商网络纪要》。")

        opts = [
            ("6-B", "主持全国重点文物保护单位修缮档案工程，频繁走访文化界老同志", s06_b),
            ("6-C", "借文化产业调研之名走遍苏南县市，撰写《长三角县域产业网络纪要》", s06_c)
        ]
        if self.ct > 35:
            opts.insert(0, ("6-A", "闭门研读现代公共管理，撰写《现代文官考核与公共事务治理论考》", s06_a))
        self.choose("【场景 06 抉择】", opts)

        self.ct, self.ra = clamp(self.ct), clamp(self.ra)
        self.print_status()

    # ------------------ TRANSITION ------------------
    def transition_to_stage2(self):
        self.stage = 2
        self.log("\n" + "#" * 68)
        self.log("  【历史行程转换点 · 二十年沉潜终得外放】")
        self.log("  2000年底，中央一纸任命：李源潮同志调任江苏省委副书记、南京市委书记。")
        self.log("  列车自北京站开出，驶向长江之畔的滚滚烟波。")
        self.log("  两维官场面板结案归档，全面切入四维主政中枢博弈系统：")
        self.log("  - 中央信任度 (central_trust): 基础值 55")
        self.log("  - 地方向心力 (local_cohesion): 基础值 60")
        self.log("  - 财政健康度 (fiscal_stability): 基础值 60")
        self.log("  - 改革开拓度 (reform_drive): 基础值 50")
        self.log("#" * 68)

        # Stage 1 to Stage 2 Value Injection (clamp to [-4, +4])
        c_inj = max(-4, min(4, (self.ct - 50) // 4))
        r_inj = max(-4, min(4, (self.ra - 50) // 4))
        self.c += c_inj
        self.r += r_inj
        self.log(f">>> [前期沉淀折算] 组织信任度({self.ct})换算中央信任开局修正: {c_inj:+d} 点")
        self.log(f">>> [前期沉淀折算] 改革锐度值({self.ra})换算改革开拓开局修正: {r_inj:+d} 点")

        # Baseline adjustments from Stage 1 flags
        if "边缘平调序列" in self.tags:
            self.c -= 3
            self.log(">>> [边缘平调序列] 结算：中央信任初始扣减 3 点")
        if "报批越界通报" in self.tags:
            self.c -= 2
            self.log(">>> [报批越界通报] 结算：中央信任初始扣减 2 点")

        self.c, self.l, self.f, self.r = clamp(self.c), clamp(self.l), clamp(self.f), clamp(self.r)

    # ------------------ VOLUME 4 ------------------
    def vol4_run(self):
        self.print_header("第四卷：主政江淮与两会大考 (2000-2007)")
        self.print_status()

        # Scene 07 AP
        self.log("\n【场景 07 前置 · 2001年春 南京 北京西路省委大院】")
        self.log("上任伊始，机关作风散漫，‘门难进、脸难看’积弊甚深。你有 2 点精力(AP)排查线索：")
        
        ap_choices = []
        def ap4_a():
            self.tags.add("公交录像带")
            self.log("\n>>> 你派人暗访市属公交热线与窗口排队实况，获取了多段一手录像。")
        def ap4_b():
            f_pen = 3 if any(k in self.tags for k in ("苏南经济底稿", "经贸法治底盘")) else 5
            self.f -= f_pen
            self.tags.add("城投挪用线索")
            self.log(f"\n>>> 调阅城投基建账目，发现拆迁隐性亏空，财政健康度 -{f_pen}。")
        def ap4_c():
            bonus = 3 if any(k in self.tags for k in ("老辈训诫", "老同志的信赖档案")) else 0
            self.l += 5 + bonus
            self.tags.add("老同志口风")
            self.log(f"\n>>> 走访省政协老领导，探知老干部对新班子的态度，地方向心力 +{5+bonus}。")

        # Let user pick 2
        for i in range(2):
            opts = []
            if "公交录像带" not in self.tags:
                opts.append(("A", "派出暗访组携摄像机记录南京窗口排队实况 (获取：[公交录像带])", ap4_a))
            if "城投挪用线索" not in self.tags:
                opts.append(("B", "调阅市建委与城投公司城建隐性账目 (获取：[城投挪用线索])", ap4_b))
            if "老同志口风" not in self.tags:
                opts.append(("C", "拜访省政协退休老常委，探听老部下口风 (获取：[老同志口风])", ap4_c))
            self.choose(f"【调查阶段 · 第 {i+1} 点精力 (剩余 {2-i} AP)】", opts)

        # Scene 08 Choice
        self.log("\n【场景 08 · 2001年4月 南京 人民大会堂 全市万人作风整顿大会】")
        def s08_a():
            self.c += 5; self.r += 5; self.l -= 10
            self.tags.add("机关震荡反弹")
            self.log("\n>>> 当场播放暗访录像，问责多名分局局长，机关震动。")
        def s08_b():
            self.l += 5; self.c += 1; self.r -= 5
            self.tags.add("整顿流于形式")
            self.log("\n>>> 闭门通报整改，机关上下松了一口气，但整顿流于形式。")
        def s08_c():
            self.r += 8; self.f -= 10; self.l -= 5
            self.tags.add("土地融资依赖")
            self.log("\n>>> 宣布推行‘万人评议机关’末位淘汰制，强推数字化政务窗口。")
        def s08_d():
            bonus = 1 if any(k in self.tags for k in ("双轨探索者", "现代治理工具箱")) else 0
            self.r += 5 + bonus; self.f += 6; self.l -= 4
            self.tags.add("建委隐形积怨")
            self.log("\n>>> 宣布收紧城投城建发包权，集中财权，建委系统心生不满。")

        s08_opts = [
            ("1-B", "只作内部闭门通报，要求限期自查自纠，不在万人大会上公开点名", s08_b),
            ("1-C", "当场宣布推行‘万人评议机关’末位淘汰制，推行行政审批服务承诺制", s08_c)
        ]
        if "公交录像带" in self.tags:
            s08_opts.insert(0, ("1-A", "直接播放暗访录像，现场免去排队严重、吃拿卡要的区房管局副局长职务", s08_a))
        if "城投挪用线索" in self.tags:
            s08_opts.append(("1-D", "以此为突破口，下令市审计局全面进驻城投公司与建委，截断资金违规外流", s08_d))

        if any(k in self.tags for k in ("破格外放序列", "不务正业非议", "脱离工农议论", "清高孤僻风评")):
            self.l -= 2
        self.choose("【场景 08 决策】", s08_opts)
        self.c, self.l, self.f, self.r = clamp(self.c), clamp(self.l), clamp(self.f), clamp(self.r)
        self.print_status()

        # Scene 09
        self.log("\n【场景 09 · 2004年春 常州 铁本钢铁项目紧急常委会】")
        self.log("发改委、监察部等九部委联合调查组进驻常州。江淮大地正处于宏观调控的风口浪尖。")
        def s09_a():
            self.c += 10; self.l -= 15; self.f -= 10
            self.tags.update(["彻底停工", "省府裂痕"])
            self.log("\n>>> 铁本工程全面停工停贷，彻查违规用地，与省府及常州地方主官产生深刻裂痕。")
        def s09_b():
            self.l += 10; self.f += 5; self.c -= 10
            self.tags.add("地方重组意向")
            self.log("\n>>> 极力争取部委理解，提出宝钢联合兼并重组方案，承担中央宏观调控疑虑。")
        def s09_c():
            self.r += 4; self.f += 5; self.c -= 5; self.l -= 5
            self.tags.update(["设备共管方案", "折中敷衍疑虑"])
            self.log("\n>>> 对违规占地严肃查处，但将已订购的高炉设备予以保全，方案折中。")

        self.choose("【场景 09 决策】", [
            ("2-A", "坚决与中央保持高度一致，指令常州市全面停工停贷，立案查处涉案干部", s09_a),
            ("2-B", "力保苏南工业血脉，进京当面陈情，争取以宝钢重组铁本的名义保全高炉", s09_b),
            ("2-C", "采取资产保全折中案：查处责任人与违规土地，但将高炉设备封存移交国资监管", s09_c)
        ])
        self.c, self.l, self.f, self.r = clamp(self.c), clamp(self.l), clamp(self.f), clamp(self.r)
        self.print_status()

        # Scene 10
        self.log("\n【场景 10 · 2004年夏 铁本案部委九部委专项座谈会】")
        if "土地融资依赖" in self.tags: self.f -= 3
        if "折中敷衍疑虑" in self.tags or "滑头避险定性" in self.tags: self.c -= 2

        def s10_a():
            self.c += 15; self.l -= 10
            self.tags.add("连带问责留档")
            self.log("\n>>> 主动承担省委领导责任，严肃免去常州市委主要负责人职务。")
        def s10_b():
            bonus = 2 if any(k in self.tags for k in ("苏南经济底稿", "经贸法治底盘")) else 0
            pen = 5 if "地方重组意向" in self.tags else 0
            self.l += 15; self.f += 5 + bonus; self.c -= (10 + pen)
            self.tags.add("抗辩部委记名")
            self.log("\n>>> 列席部委汇报，直陈苏南制造业用地现实矛盾，部委高层神情严肃。")
        def s10_c():
            bonus = 2 if any(k in self.tags for k in ("苏南经济底稿", "经贸法治底盘")) else 0
            pen = 5 if "地方重组意向" in self.tags else 0
            self.f += 10 + bonus; self.l -= 3; self.c -= (5 + pen)
            self.tags.add("资产切割审计尾账")
            self.log("\n>>> 提出土地与债权精算剥离方案，获发改委初步技术认可。")

        s10_opts = [
            ("3-A", "完全接受九部委定性，主动承担省委第一责任，免去涉案地方分管常委职务", s10_a)
        ]
        if "城投挪用线索" in self.tags or self.f >= 60:
            s10_opts.append(("3-B", "当面向部委抗辩：拿出长三角用地数据，说明宏观调控与实体制造的结构性矛盾", s10_b))
        if "设备共管方案" in self.tags:
            s10_opts.append(("3-C", "拿出资产切割审计方案：土地无偿退回村民，高炉转让给省属国企作为抵押物", s10_c))

        self.choose("【场景 10 决策】", s10_opts)
        self.c, self.l, self.f, self.r = clamp(self.c), clamp(self.l), clamp(self.f), clamp(self.r)
        self.print_status()

        # Scene 11
        self.log("\n【场景 11 · 2005年春 苏北某县农村税费改革后‘化解乡村债务’上访事件】")
        if "建委隐形积怨" in self.tags or "省府裂痕" in self.tags: self.l -= 2
        half11 = (self.l <= 35)

        def s11_a():
            self.c += 5; self.l += 20; self.f -= 12
            self.tags.add("预备费见底")
            self.log("\n>>> 省财政全额贴息垫付乡村债务，平息上访，但财政预备费见底。")
        def s11_b():
            r_add = 2 if half11 else 5
            self.f += 5; self.r += r_add; self.l -= 15
            self.tags.add("雨中聚众影像")
            self.log("\n>>> 强行并村减员，压减乡村干部职数，村民在县委雨中静坐。")
        def s11_c():
            self.c += 5; self.l -= 10; self.r -= 5
            self.tags.add("官场寒蝉效应")
            self.log("\n>>> 叫停激进债务重组，责成县委书记就地整肃，官场产生寒蝉效应。")

        s11_opts = [
            ("4-B", "不给新增贴息，推行强力并村减员与村级财务阳光直报，倒逼村官退赔挪用款", s11_b),
            ("4-C", "责令县委限期息访息诉，下调当年该县考核等次，暂缓全省税费配套改革进程", s11_c)
        ]
        if self.f > 40:
            s11_opts.insert(0, ("4-A", "省财政紧急下拨两亿元专项化债贴息基金，彻底买断历年乡村公益白条", s11_a))

        self.choose("【场景 11 决策】", s11_opts)
        self.c, self.l, self.f, self.r = clamp(self.c), clamp(self.l), clamp(self.f), clamp(self.r)
        self.print_status()

        # Scene 12
        self.log("\n【场景 12 · 2006年夏 宿迁 干部‘公推公选’改革试点】")
        if "抗辩部委记名" in self.tags: self.c -= 2
        if "官场寒蝉效应" in self.tags: self.r -= 2
        half12 = (self.l <= 35)

        def s12_a():
            r_add = 7 if half12 else 15
            l_sub = 5 if "老同志口风" in self.tags else 10
            self.r += r_add; self.c -= 15; self.l -= l_sub
            self.tags.update(["激进政改旗手", "党管干部质疑"])
            self.log("\n>>> 直推县处级主官党内竞选，被保守舆论质疑突破‘党管干部’红线。")
        def s12_b():
            self.c += 5
            base_r = 2 if half12 else 5
            bonus_r = (1 if half12 else 2) if any(k in self.tags for k in ("双轨探索者", "现代治理工具箱")) else 0
            self.r += base_r + bonus_r
            l_add = 3 if any(k in self.tags for k in ("老同志口风", "老同志的信赖档案")) else -5
            self.l += l_add
            self.tags.update(["制度精算样本", "形式主义诟病"])
            self.log("\n>>> 引入结构化面试与民调打分，形成精算矩阵，但也遭基层指责繁琐。")
        def s12_c():
            self.c += 5; self.l += 5; self.r -= 10
            self.tags.add("改革保守退缩")
            self.log("\n>>> 严格限制在副处级群团与老干部门试点，改革锋芒迅速收敛。")

        s12_opts = [
            ("5-B", "引入现代公文与结构化面试精算体系，结合民意打分与常委会终审", s12_b),
            ("5-C", "将试点严格限定在副处级群团岗位，不出通稿，低调收场", s12_c)
        ]
        if self.c > 40:
            s12_opts.insert(0, ("5-A", "全县放开直选正职，允许党员代表无记名预选与电视辩论", s12_a))

        self.choose("【场景 12 决策】", s12_opts)
        self.c, self.l, self.f, self.r = clamp(self.c), clamp(self.l), clamp(self.f), clamp(self.r)
        self.print_status()

        # Scene 13: 3 rounds
        self.log("\n【场景 13 · 2006年十届全国人大四次会议 江苏团对境外媒体开放日】")
        self.log("北京人民大会堂江苏厅，外媒记者长枪短炮林立。")
        
        can_1c = ("设备共管方案" in self.tags or "彻底停工" in self.tags)
        has_fx = any(k in self.tags for k in ("外宣基本功", "精准反制经验"))
        can_2c = ("制度精算样本" in self.tags)
        p1_c = False
        p2_c = False

        # Round 1
        if "雨中聚众影像" in self.tags: self.c -= 2
        def r1_a():
            self.r += 3; self.c -= 6
            self.log("\n>>> 回应直率坦诚，引起外媒头条轰动，但涉嫌否定宏观调控大局。")
        def r1_b():
            self.c += 1; self.r -= 2
            self.log("\n>>> 严格念诵发改委联合整肃通稿，外媒反响冷淡。")
        def r1_c():
            nonlocal p1_c
            p1_c = True
            bonus = 1 if has_fx else 0
            self.r += 3; self.c += 2 + bonus; self.f -= 1
            self.log("\n>>> 给出常州产业转型实绩，举重若轻，博得满堂喝彩。")

        r1_opts = [
            ("1-A", "直面发难，指出传统重工业盲目扩张教训，承诺彻底淘汰落后产能", r1_a),
            ("1-B", "官样文章回应：重申发改委联合通报，不展开任何未经通报的具体细节", r1_b)
        ]
        if can_1c:
            r1_opts.append(("1-C", "举重若轻化解：以常州环保转型数据为盾，借‘长者语录’从容笑对外媒", r1_c))
        self.choose("【两会大考 · 第一轮：华尔街日报就‘铁本案’发难】", r1_opts)

        # Round 2
        def r2_a():
            self.r += 4; self.c -= 8
            self.tags.add("党管干部质疑")
            self.log("\n>>> 宣称干部公选是党内民主必由之路，引发高层组织原则质询。")
        def r2_b():
            self.c += 2; self.r -= 3; self.l -= 2
            self.log("\n>>> 强调公选只是个别贫困县实验，不代表普遍政策。")
        def r2_c():
            nonlocal p2_c
            p2_c = True
            bonus = 1 if has_fx else 0
            self.r += 3; self.c += 2 + bonus; self.l -= 1
            self.log("\n>>> 阐明党管干部与群众公认的有机统一，逻辑缜密。")

        r2_opts = [
            ("2-A", "大谈民主政治试验，宣称基层公开竞争是执政党自我革新的唯一出路", r2_a),
            ("2-B", "淡化政治色彩：说明这只是个别后进县市为选拔青年干部的技术性探索", r2_b)
        ]
        if can_2c:
            r2_opts.append(("2-C", "以法治与制度化解构：强调‘党管干部与群众公认相统一’的程序规范", r2_c))
        self.choose("【两会大考 · 第二轮：路透社就‘宿迁干部直选’追问】", r2_opts)

        # Round 3
        def r3_a():
            self.r -= 2; self.c -= 2
            self.log("\n>>> 称发展是第一要务，环保须兼顾民生，遭到环保阵营批评。")
        def r3_b():
            self.c += 1; self.r -= 2
            self.log("\n>>> 宣读省太湖污染防治硬指标规划，平淡过关。")
        def r3_c():
            pen = 1 if "预备费见底" in self.tags else 0
            self.r += 4; self.c += 2; self.l -= (4 + pen)
            self.tags.add("地方抵制环保考核")
            if p1_c and p2_c:
                self.r += 2
                self.tags.add("外宣高手")
                self.log("\n>>> 三连精彩应答！获得核心勋章：[外宣高手]！")
            self.log("\n>>> 宣布将水质断面达标纳入县市党政‘一票否决’，沿湖县委主官脸色煞白。")

        self.choose("【两会大考 · 第三轮：法新社就‘太湖水污染与化工厂包围’发问】", [
            ("3-A", "坦言发展中代价难免，承诺在十一五期间稳步推进治理", r3_a),
            ("3-B", "严格按照省环保局五年规划通稿作答，列举已关闭小化工厂数字", r3_b),
            ("3-C", "当场宣布：将太湖水质断面考核纳入县市主官政绩‘一票否决’硬指标", r3_c)
        ])

        self.c, self.l, self.f, self.r = clamp(self.c), clamp(self.l), clamp(self.f), clamp(self.r)
        self.print_status()

        # Scene 14
        self.log("\n【场景 14 · 2007年秋 重庆 南山宾馆 庭院夜谈】")
        self.log("十七大前夕，两位同龄主政大员在南山桂花树下负手而立。")
        self.log("‘源潮同志，长三角风头正劲。可中枢的棋局，走快半步是先锋，走快一步可就是深渊了。’")

        def s14_a():
            self.r += 1; self.c -= 2
            self.tags.update(["改革盟约", "派系结盟猜忌"])
            self.log("\n>>> 你与其深谈现代干部制度，达成改革默契，但也种下了结盟猜忌隐患。")
        def s14_b():
            self.c += 2; self.r -= 2
            self.tags.update(["无暇履历", "程序本位掣肘"])
            self.log("\n>>> 你谨守组织程序底线，不谈宏观人事，展现了无可挑剔的党性定力。")
        def s14_c():
            self.c += 1; self.r -= 1
            self.tags.update(["宏观定力", "锋芒收敛过甚"])
            self.log("\n>>> 你以江浙沿海产业承接与宏观调控切题，深谈东部反哺西部大局。")

        self.choose("【场景 14 抉择】", [
            ("6-A", "与其深谈干部人事制度深水区改革，达成体制内少壮派共识", s14_a),
            ("6-B", "谨守组织纪律，仅交流两地产业协作，对中枢人事变动绝口不提", s14_b),
            ("6-C", "纵论东部沿海反哺西部开发大局，探讨长三角资本西进与跨周期宏观调控", s14_c)
        ])

        self.c, self.l, self.f, self.r = clamp(self.c), clamp(self.l), clamp(self.f), clamp(self.r)
        self.print_status()

        # 17th Congress Settlement
        self.print_header("【十七大前夕 · 中枢组织考察节点独立网关结算】")
        e17 = self.evaluate_17th_congress()
        self.log(f"\n>>> 考察综合评定结果：{e17}")
        return e17

    def evaluate_17th_congress(self):
        if self.c < 45 or self.f < 35:
            return "Ending C (改革折翼 · 全国人大)"
        if "激进政改旗手" in self.tags and self.c >= 50 and self.r >= 60:
            return "Ending D (顺水推舟 · 政研社科)"
        if self.c >= 65 and self.l >= 38 and self.r >= 50:
            return "PROCEED_TO_VOL5"
        return "Ending E (留任守成 · 异地平调)"

    # ------------------ VOLUME 5 ------------------
    def vol5_run(self):
        self.current_vol = 5
        self.print_header("第五卷：大木仓胡同的算局 (2007-2012)")
        self.log("十七届一中全会，李源潮当选中央政治局委员、中央书记处书记，兼任中央组织部部长。")
        self.log("西单大木仓胡同的中组部大楼内，一幅涉及数万名副厅级以上文官的考核算局铺展开来。")
        self.print_status()

        # Scene 15 AP
        self.log("\n【场景 15 前置 · 2007年底 大木仓胡同 干部监督局研判室】")
        self.log("你有 2 点精力(AP)排查案卷：")
        
        for i in range(2):
            opts = []
            if "监督局带病档案" not in self.tags:
                opts.append(("A", "抽查近年来‘带病提拔’与非正常离岗典型卷宗 (获取：[监督局带病档案])", lambda: self.tags.add("监督局带病档案")))
            if "基层测评原始样表" not in self.tags:
                opts.append(("B", "调阅中西部省份党政干部民主测评真实样表 (获取：[基层测评原始样表])", lambda: self.tags.add("基层测评原始样表")))
            if "使节团提问清单" not in self.tags:
                opts.append(("C", "审定境外主流媒体对‘党内民主’的焦点提问单 (获取：[使节团提问清单])", lambda: self.tags.add("使节团提问清单")))
            self.choose(f"【调查阶段 · 第 {i+1} 点精力 (剩余 {2-i} AP)】", opts)

        # Scene 15 Choice: 2009年 地方党政干部考核“民主测评”权重改革
        self.log("\n【场景 15 · 2009年春 地方党政干部考核‘民主测评’权重改革】")
        if "形式主义诟病" in self.tags or "滑头风评" in self.tags: self.r -= 2

        def s15_a():
            self.r += 6; self.c -= 8; self.l -= 5
            self.log("\n>>> 强推民意打分一票否决，遭到地方省市委书记联名反弹。")
        def s15_b():
            bonus = 2 if any(k in self.tags for k in ("基层测评原始样表", "无暇履历", "宏观定力")) else 0
            self.c += 5 + bonus; self.r += 5; self.l -= 2
            self.tags.update(["加权考核矩阵", "加权考核执行损耗"])
            self.log("\n>>> 推出综合加权考核矩阵，兼顾中央考核、地方实绩与民调。")
        def s15_c():
            self.c += 4; self.l += 4; self.r -= 8
            self.tags.add("测评退回旧轨失望")
            self.log("\n>>> 维持传统考选体制，民主测评结果退回内部参考。")

        self.choose("【场景 15 决策】", [
            ("15-A", "大幅提高民意测评与社会满意度权重，不合格者实行一票否决", s15_a),
            ("15-B", "建立综合加权矩阵：兼顾发展实绩、中央调控遵从度与党风廉政综合打分", s15_b),
            ("15-C", "维持传统推荐考核体制，民主测评结果仅作内部参考、不作硬性挂钩", s15_c)
        ])
        self.c, self.l, self.f, self.r = clamp(self.c), clamp(self.l), clamp(self.f), clamp(self.r)
        self.print_status()

        # Scene 16: 2010年秋 深圳等特区新一轮深化改革主官选任
        self.log("\n【场景 16 · 2010年秋 深圳等特区新一轮深化改革主官选任】")
        if "监督局带病档案" in self.tags:
            self.c += 2
            self.log(">>> [监督局带病档案] 规避潜在政治风险，中央信任度 +2")

        def s16_a():
            self.c += 3; self.l += 4; self.r -= 4
            self.tags.add("粤系地方阻力")
            self.log("\n>>> 本地干部就地顺位升任，平稳但改革动力不足。")
        def s16_b():
            pen = 1 if any(k in self.tags for k in ("派系结盟猜忌", "地方招商宿怨")) else 0
            self.r += 7; self.c += 2; self.l -= (2 + pen)
            self.tags.update(["特区新局", "跨省空降派系芥蒂"])
            self.log("\n>>> 从江浙调派懂产业、懂高科技的少壮派跨省空降，特区新局开启。")
        def s16_c():
            self.c += 4; self.r += 2; self.l -= 3
            self.log("\n>>> 由发改、商务部委选派综合司长空降主政。")

        s16_opts = [
            ("16-A", "尊重地方推荐序列，选任深耕特区多年的本土实干型干部", s16_a),
            ("16-C", "从中枢宏观经济部委选派精通现代法治与国际贸易的骨干空降任职", s16_c)
        ]
        if "改革盟约" in self.tags and self.c > 40:
            s16_opts.insert(1, ("16-B", "打破地域界限：从长三角跨省选拔锐意改革的少壮派技术官僚破格主政", s16_b))

        self.choose("【场景 16 决策】", s16_opts)
        self.c, self.l, self.f, self.r = clamp(self.c), clamp(self.l), clamp(self.f), clamp(self.r)
        self.print_status()

        # Scene 17: 2010年6月30日 西单大木仓胡同吹风会
        self.log("\n【场景 17 · 2010年6月30日 中组部对外媒体吹风会（压轴吹风会）】")
        if "大院子弟标签" in self.tags:
            self.c -= 2
            self.log(">>> [大院子弟标签] 引发外媒追问高干后代晋升顺位，中央信任度 -2")

        def s17_a():
            self.c += 3; self.r -= 4
            self.tags.add("密闭保稳惯性")
            self.log("\n>>> 严词照念保密与民主集中制原则，保稳过关。")
        def s17_b():
            bonus = 2 if "使节团提问清单" in self.tags else 0
            self.r += 7 + bonus; self.c += 2; self.l -= 2
            self.tags.update(["执政党阳光化象征", "系统内保守派侧目"])
            if "加权考核矩阵" in self.tags:
                self.log("\n>>> 援引公推差选与双轨加权矩阵做程序拆解：分毫不差，外媒高度好评！")
            else:
                self.log("\n>>> 援引公推差选做程序拆解，执政党阳光化获外媒肯定，系统内保守派侧目。")
        def s17_c():
            self.r += 5; self.c -= 4
            self.tags.add("自揭家丑非议")
            self.log("\n>>> 直陈带病提拔倒查追责机制，引发党内自揭家丑非议。")

        s17_opts = [
            ("17-A", "严词照念保密与民主集中制原则，拒绝展开数字", s17_a),
            ("17-C", "不避短板：直陈‘带病提拔’倒查与实绩考核改革", s17_c)
        ]
        if "外宣高手" in self.tags or self.r >= 60:
            s17_opts.insert(1, ("17-B", "援引公推差选、测评加权与特区点将做程序拆解", s17_b))

        self.choose("【场景 17 决策】", s17_opts)
        self.c, self.l, self.f, self.r = clamp(self.c), clamp(self.l), clamp(self.f), clamp(self.r)
        self.print_status()

        # Scene 17-结: 2012年十八大换届总结算节点
        self.print_header("【2012年十八大换届总结算节点 · 中枢考察独立网关核验】")
        e18 = self.evaluate_18th_congress()
        self.log(f"\n>>> 十八大换届总核验评定结果：{e18}")
        return e18

    def evaluate_18th_congress(self):
        if self.c >= 85 and self.r >= 75 and "自揭家丑非议" not in self.tags and "连带问责留档" not in self.tags:
            return "Ending A1 (巅峰折冲 · 核心统筹)"
        if self.c < 50 or self.l < 35:
            return "Ending A3 (提前淡出 · 倚楼晚照)"
        return "PROCEED_TO_VOL6"

    # ------------------ VOLUME 6 ------------------
    def vol6_run(self):
        self.current_vol = 6
        self.print_header("第六卷：晚晴长风与历史行程 (2013-2018+)")
        self.log("十二届全国人大一次会议上当选国家副主席。")
        self.log("四维属性进入脱敏软着陆模式，界面警戒条淡出，转入【晚晴手记与案头器物】收集模式。")
        self.print_status()

        # Scene 17-A AP
        self.log("\n【场景 17-A 前置 · 2013年12月 中南海办公区外事值班室】")
        def ap6_a():
            self.tags.add("群团基层调研底表")
            self.log("\n>>> 细读《社会组织与群团基层调研底表》，圈出虚报项目。")
        def ap6_b():
            self.tags.add("外事礼宾密电")
            self.log("\n>>> 审阅《约翰内斯堡多边会见密电汇编》，掌握涉华敏感点预设口径。")

        self.choose("【出访前案卷核查 (AP=1)】", [
            ("A", "细读工青妇联合递交的《社会组织与群团基层调研底表》 (获取：[群团基层调研底表])", ap6_a),
            ("B", "审阅外交部与礼宾司汇总的《约翰内斯堡多边会见密电汇编》 (获取：[外事礼宾密电])", ap6_b)
        ])

        # Passive checks
        if "密闭保稳惯性" in self.tags or "自揭家丑非议" in self.tags: self.r -= 2
        if "系统内保守派侧目" in self.tags or "跨省空降派系芥蒂" in self.tags: self.l -= 2
        if "测评退回旧轨失望" in self.tags or "青年统战滞后" in self.tags or "粤系地方阻力" in self.tags: self.r -= 2

        # Desk track 1: 外事
        self.log("\n【场景 18 第 1 轮 · 冷雨中的多边外事备忘录】")
        def s18_1a():
            bonus = 2 if "外事礼宾密电" in self.tags else 0
            self.c += 4 + bonus; self.r -= 3
            self.tags.add("端方国士")
            self.log("\n>>> 严守外交礼宾口径，做稳妥克制的大国代表。获得标记：[端方国士]。")
        def s18_1b():
            self.r += 4; self.c -= 3
            self.log("\n>>> 在达沃斯与双边简报中主动阐释中国市场准入与环保硬考核。")
        self.choose("【场景 18-1 外事抉择】", [
            ("18-1A", "严守外交礼宾口径，做稳妥克制的大国代表", s18_1a),
            ("18-1B", "在达沃斯与双边简报中主动阐释中国市场准入与环保硬考核", s18_1b)
        ])

        # Desk track 2: 群团
        self.log("\n【场景 18 第 2 轮 · 回国批复群团改革与个人权力边界】")
        def s18_2a():
            bonus = 2 if "群团基层调研底表" in self.tags else 0
            self.r += 5 + bonus; self.l -= 2; self.c -= 2
            self.tags.add("未竞的改革之弦")
            self.log("\n>>> 试行取消机关化会议，项目化社会评估买单。获得标记：[未竞的改革之弦]。")
        def s18_2b():
            self.c += 4; self.r -= 3
            self.tags.add("云淡风轻")
            self.log("\n>>> 划死个人权力退场边界，谢绝制度外过问与人事推荐。获得标记：[云淡风轻]。")
        self.choose("【场景 18-2 群团与退场抉择】", [
            ("18-2A", "借群团改革推‘非政府组织社会评估’与项目化买单", s18_2a),
            ("18-2B", "划死个人权力退场边界，谢绝制度外过问与人事推荐", s18_2b)
        ])

        self.c, self.l, self.f, self.r = clamp(self.c), clamp(self.l), clamp(self.f), clamp(self.r)
        self.print_status()

        # 终章回响：海淀旧院
        self.log("\n【终章回响 · 2018年深秋 海淀旧院】")
        self.log("黄昏时分，斜阳挂在老槐树梢。六十八岁的他坐在书桌前，按灭了电视遥控器。")
        self.log("书桌左侧放着《偏微分方程进展》，右侧是伴随三十余年的旧牛皮笔记本。")
        if "端方国士" in self.tags:
            self.log("  [案头器物] 书柜第二格整齐码着多边外事照会册，烫金国徽封皮纤尘不染。")
        if "未竞的改革之弦" in self.tags:
            self.log("  [案头器物] 笔筒旁压着未曾最终印发的《群团社团社会化评估试行稿》清样，留着红铅笔修改痕迹。")
        if "云淡风轻" in self.tags:
            self.log("  [案头器物] 靠墙的铁皮文件柜全部腾空，柜门钥匙放在笔洗旁，只留下一叠私人读书札记。")
        self.log("翻开笔记本最后一页空白处，拧开钢笔帽，落下一行小字：")
        self.log("  ‘胜地不常，盛筵难再。’")
        self.log("合上钢笔帽，窗外秋风扫过干槐叶，发出沙沙轻响。")

        return "Ending A2 (端方晚晴 · 稳健执印)"

    def render_grand_ending(self, ending_key):
        self.print_header("【全剧终局 · 历史行程结算】")
        self.log(f"结算终局归宿：{ending_key}\n")

        if "Ending A1" in ending_key:
            self.log("【终局 A1：巅峰折冲 · 核心统筹（高难 IF 线）】")
            self.log("2012年秋，十八届一中全会上当选中央政治局常委，兼任中央书记处常务书记，翌年兼任中央全面深化改革领导小组副组长。")
            self.log("在京城主持十八届三中全会文件起草与落地督察，在放权清单与跨省督办之间往来协调。")
            self.log("2018年秋，机要室送来最后一卷改革督查评估报告，他在内参封皮上落下最后一道红笔批示，合上钢笔帽放到笔架上。")
        elif "Ending A2" in ending_key:
            self.log("【终局 A2：端方晚晴 · 稳健执印（正史主线）】")
            self.log("2018年3月，十三届全国人大一次会议。")
            self.log("交卸国家副主席职务后，李源潮微笑着与代表们握手告别。")
            self.log("海淀旧院的书房里，砚台尚润，窗外青松挺拔。")
            self.log("四十年间，从复旦的算纸，到前门的晨风；从东华门的笔墨，到玄武湖的烟波；")
            self.log("再到大木仓胡同的算局与多边外交的从容。")
            self.log("你以学者的缜密与文官的忍耐，在历史的有限空间内，推演出了最周全的行程。")
            self.log("‘胜地不常，盛筵难再；兰亭已矣，梓泽丘墟。’")
            self.log("笔锋停在旧稿纸上，墨迹干透。历史已然注脚。")
        elif "Ending A3" in ending_key:
            self.log("【终局 A3：提前淡出 · 倚楼晚照（中组部失分线）】")
            self.log("2012年秋，因中组部任内测评指标引发基层反弹，或吹风会发言留有口实，未能顺位出任国家副主席，提前转任全国政协副主席兼专门委员会主任。")
            self.log("此后五年坐镇太平桥大街全国政协礼堂西侧院落，分管侨联与社会福利调研。")
            self.log("2018年春办理退休手续离开办公室时，他把整理的文官制度旧稿捆上麻绳，放进纸箱封口。")
        elif "Ending B" in ending_key:
            self.log("【终局 B：象牙塔的余生 · 纯粹清白】")
            self.log("你从未跨进前门东大街那座机关大楼的大门。")
            self.log("八十年代的偏微分方程讲义泛黄，九十年代的学术专著摆满复旦数学系的书架。")
            self.log("没有红头文件，没有常委会的机锋，也没有晚晴长风的叹息。")
            self.log("你在黑板前写下最后一串公式，粉笔灰落满两鬓。清白一身，不负所学。")
        elif "Ending C" in ending_key:
            self.log("【终局 C：改革折翼 · 全国人大】")
            self.log("因关键阶段信任折损或财政债务链断裂，仕途在省部级节点戛然而止。")
            self.log("2007年秋，未进中央书记处，调任全国人大专门委员会副主任委员。")
            self.log("每年三月，你坐在代表团后排翻看厚厚的预算报告，圈出当年的老数据。")
            self.log("‘关山难越，谁悲失路之人？’推门时木门合页发出轻响，一切皆成定局。")
        elif "Ending D" in ending_key:
            self.log("【终局 D：顺水推舟 · 政研社科】")
            self.log("因鲜明的党内民主改革旗手标签，未能接任中组部部长，转入最高智库。")
            self.log("出任中央政策研究室常务副主任兼中国社会科学院党组书记。")
            self.log("在建国门内大街的社科院大楼主持党内民主与国家治理课题组十年，撰写数十篇未公开内参报告。")
            self.log("虽无生杀予夺之权，却为后来者的行政制度演进留下了最厚重的底稿。")
        else:
            self.log("【终局 E：留任守成 · 异地平调】")
            self.log("在宏观调控与激进改革的撕扯中选择了保守避险。")
            self.log("2007年秋平调另一东部沿海大省出任省委书记，主抓港口外贸与省内平衡，再未跻身中央核心部委序列。")
            self.log("任满一届后按年龄界限退居二线，在海边疗养院整理地方志稿件。合上年鉴，扣回茶杯盖。")

        self.log("\n" + "=" * 68)
        self.log("  游戏体验结束。感谢演练《浪潮与行程：李源潮仕途模拟器》。")
        self.log("=" * 68 + "\n")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--baseline":
        # Run historical baseline route
        baseline = [
            "C", "1-B", "2-A",  # Vol 1: 摸底C + 1-B + 2-A
            "A", "3-C", "A-2", "B-1", "4-1B", "4-B", # Vol 2: 摸底A + 3-C + A-2 + B-1 + 4-1B + 4-B
            "B", "5-B", "C-1", "D-2", "6-B", # Vol 3: 摸底B + 5-B + C-1 + D-2 + 6-B
            "A", "C", "1-A", "2-A", "3-A", "4-A", "5-B", "1-C", "2-C", "3-C", "6-A", # Vol 4
            "B", "C", "15-B", "16-B", "17-B", # Vol 5
            "A", "18-1A", "18-2A" # Vol 6
        ]
        engine = GameEngine(auto_choices=baseline)
        engine.play()
    else:
        engine = GameEngine()
        engine.play()
