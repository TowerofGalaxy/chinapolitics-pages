import type { Condition, Scene } from '../story/schema'
import type { GameState } from '../game/engine'

export interface TagMeta {
  year: number
  vol: number
  name: string
}

export const TAG_METADATA: Record<string, TagMeta> = {
  // 卷一 (1977-1982)
  '纯粹知识分子底色': { year: 1977, vol: 1, name: '纯粹知识分子底色' },
  '象牙塔学者': { year: 1981, vol: 1, name: '象牙塔学者' },
  '退稿油印刊物': { year: 1981, vol: 1, name: '退稿油印刊物' },
  '导师推荐信底稿': { year: 1981, vol: 1, name: '导师推荐信底稿' },
  '第三梯队座谈纪要': { year: 1981, vol: 1, name: '第三梯队座谈纪要' },
  '书生执拗': { year: 1981, vol: 1, name: '书生执拗' },
  '考察保留': { year: 1981, vol: 1, name: '考察保留' },
  '双轨探索者': { year: 1981, vol: 1, name: '双轨探索者' },
  '大院子弟标签': { year: 1982, vol: 1, name: '大院子弟标签' },
  '法治骨气': { year: 1982, vol: 1, name: '法治骨气' },
  '老辈训诫': { year: 1982, vol: 1, name: '老辈训诫' },

  // 卷二 (1983-1990)
  '温州调研原件': { year: 1985, vol: 2, name: '温州调研原件' },
  '预审口径单': { year: 1985, vol: 2, name: '预审口径单' },
  '风骨编辑部': { year: 1985, vol: 2, name: '风骨编辑部' },
  '中宣部挂号': { year: 1985, vol: 2, name: '中宣部挂号' },
  '滑头风评': { year: 1985, vol: 2, name: '滑头风评' },
  '商品经济探索先声': { year: 1985, vol: 2, name: '商品经济探索先声' },
  '筹会透支': { year: 1985, vol: 2, name: '筹会透支' },
  '地方招商宿怨': { year: 1986, vol: 2, name: '地方招商宿怨' },
  '脱离工农议论': { year: 1986, vol: 2, name: '脱离工农议论' },
  '青年统战滞后': { year: 1986, vol: 2, name: '青年统战滞后' },
  '铁腕履历': { year: 1989, vol: 2, name: '铁腕履历' },
  '破格外放序列': { year: 1989, vol: 2, name: '破格外放序列' },
  '经贸法治底盘': { year: 1989, vol: 2, name: '经贸法治底盘' },
  '冷酷官僚风评': { year: 1989, vol: 2, name: '冷酷官僚风评' },
  '庇护者的契约': { year: 1989, vol: 2, name: '庇护者的契约' },
  '十年冷板凳': { year: 1989, vol: 2, name: '十年冷板凳' },
  '边缘平调序列': { year: 1989, vol: 2, name: '边缘平调序列' },
  '滑头避险定性': { year: 1989, vol: 2, name: '滑头避险定性' },

  // 卷三 (1990-2000)
  '文官制度底稿': { year: 1993, vol: 3, name: '文官制度底稿' },
  '外宣案例剪报': { year: 1993, vol: 3, name: '外宣案例剪报' },
  '外宣基本功': { year: 1993, vol: 3, name: '外宣基本功' },
  '精准反制经验': { year: 1993, vol: 3, name: '精准反制经验' },
  '涉外政治风险': { year: 1993, vol: 3, name: '涉外政治风险' },
  '外宣僵化印象': { year: 1993, vol: 3, name: '外宣僵化印象' },
  '涉外口径微瑕': { year: 1994, vol: 3, name: '涉外口径微瑕' },
  '报批越界通报': { year: 1993, vol: 3, name: '报批越界通报' },
  '现代治理工具箱': { year: 1994, vol: 3, name: '现代治理工具箱' },
  '不务正业非议': { year: 1995, vol: 3, name: '不务正业非议' },
  '老同志的信赖档案': { year: 1994, vol: 3, name: '老同志的信赖档案' },
  '守旧平庸标签': { year: 1994, vol: 3, name: '守旧平庸标签' },
  '苏南经济底稿': { year: 1995, vol: 3, name: '苏南经济底稿' },
  '清高孤僻风评': { year: 1993, vol: 3, name: '清高孤僻风评' },

  // 卷四 (2000-2007)
  '公交录像带': { year: 2000, vol: 4, name: '公交录像带' },
  '城投挪用线索': { year: 2000, vol: 4, name: '城投挪用线索' },
  '老同志口风': { year: 2000, vol: 4, name: '老同志口风' },
  '机关震荡反弹': { year: 2001, vol: 4, name: '机关震荡反弹' },
  '整顿流于形式': { year: 2001, vol: 4, name: '整顿流于形式' },
  '土地融资依赖': { year: 2001, vol: 4, name: '土地融资依赖' },
  '建委隐形积怨': { year: 2001, vol: 4, name: '建委隐形积怨' },
  '彻底停工': { year: 2004, vol: 4, name: '彻底停工' },
  '省府裂痕': { year: 2004, vol: 4, name: '省府裂痕' },
  '地方重组意向': { year: 2004, vol: 4, name: '地方重组意向' },
  '设备共管方案': { year: 2004, vol: 4, name: '设备共管方案' },
  '折中敷衍疑虑': { year: 2004, vol: 4, name: '折中敷衍疑虑' },
  '连带问责留档': { year: 2004, vol: 4, name: '连带问责留档' },
  '抗辩部委记名': { year: 2004, vol: 4, name: '抗辩部委记名' },
  '资产切割审计尾账': { year: 2004, vol: 4, name: '资产切割审计尾账' },
  '预备费见底': { year: 2004, vol: 4, name: '预备费见底' },
  '雨中聚众影像': { year: 2004, vol: 4, name: '雨中聚众影像' },
  '官场寒蝉效应': { year: 2004, vol: 4, name: '官场寒蝉效应' },
  '激进政改旗手': { year: 2005, vol: 4, name: '激进政改旗手' },
  '党管干部质疑': { year: 2005, vol: 4, name: '党管干部质疑' },
  '制度精算样本': { year: 2005, vol: 4, name: '制度精算样本' },
  '形式主义诟病': { year: 2005, vol: 4, name: '形式主义诟病' },
  '改革保守退缩': { year: 2005, vol: 4, name: '改革保守退缩' },
  '外宣高手': { year: 2006, vol: 4, name: '外宣高手' },
  '地方抵制环保考核': { year: 2006, vol: 4, name: '地方抵制环保考核' },
  '改革盟约': { year: 2006, vol: 4, name: '改革盟约' },
  '派系结盟猜忌': { year: 2006, vol: 4, name: '派系结盟猜忌' },
  '无暇履历': { year: 2006, vol: 4, name: '无暇履历' },
  '程序本位掣肘': { year: 2006, vol: 4, name: '程序本位掣肘' },
  '宏观定力': { year: 2006, vol: 4, name: '宏观定力' },
  '锋芒收敛过甚': { year: 2006, vol: 4, name: '锋芒收敛过甚' },
  '基层测评原始样表': { year: 2007, vol: 4, name: '基层测评原始样表' },

  // 卷五 (2007-2012)
  '监督局带病档案': { year: 2007, vol: 5, name: '监督局带病档案' },
  '使节团提问清单': { year: 2007, vol: 5, name: '使节团提问清单' },
  '民意过半硬杠反弹': { year: 2008, vol: 5, name: '民意过半硬杠反弹' },
  '加权考核矩阵': { year: 2008, vol: 5, name: '加权考核矩阵' },
  '加权考核执行损耗': { year: 2008, vol: 5, name: '加权考核执行损耗' },
  '测评退回旧轨失望': { year: 2008, vol: 5, name: '测评退回旧轨失望' },
  '粤系地方阻力': { year: 2009, vol: 5, name: '粤系地方阻力' },
  '特区新局': { year: 2009, vol: 5, name: '特区新局' },
  '跨省空降派系芥蒂': { year: 2009, vol: 5, name: '跨省空降派系芥蒂' },
  '部委空降磨合成本': { year: 2009, vol: 5, name: '部委空降磨合成本' },
  '密闭保稳惯性': { year: 2009, vol: 5, name: '密闭保稳惯性' },
  '执政党阳光化象征': { year: 2009, vol: 5, name: '执政党阳光化象征' },
  '系统内保守派侧目': { year: 2009, vol: 5, name: '系统内保守派侧目' },
  '自揭家丑非议': { year: 2009, vol: 5, name: '自揭家丑非议' },
  '大义灭亲': { year: 2010, vol: 5, name: '大义灭亲' },
  '大秘隐雷': { year: 2010, vol: 5, name: '大秘隐雷' },

  // 卷六 (2013-2018)
  '群团基层调研底表': { year: 2013, vol: 6, name: '群团基层调研底表' },
  '外事礼宾密电': { year: 2013, vol: 6, name: '外事礼宾密电' },
  '端方国士': { year: 2015, vol: 6, name: '端方国士' },
  '坦陈求是': { year: 2013, vol: 6, name: '坦陈求是' },
  '未竞的改革之弦': { year: 2015, vol: 6, name: '未竞的改革之弦' },
  '云淡风轻': { year: 2015, vol: 6, name: '云淡风轻' },
}

function extractTagsFromCondition(cond?: Condition): string[] {
  if (!cond) return []
  if ('tag' in cond) return [cond.tag]
  if ('all' in cond) return cond.all.flatMap(extractTagsFromCondition)
  if ('any' in cond) return cond.any.flatMap(extractTagsFromCondition)
  if ('not' in cond) return extractTagsFromCondition(cond.not)
  return []
}

export interface EchoItem {
  tag: string
  year: number
  vol: number
  label: string
}

/**
 * 扫描当前场景中所有被检定/激活的跨卷 Flag 或关键线索
 */
export function getActiveEchoes(scene: Scene, state: GameState): EchoItem[] {
  const referencedTags = new Set<string>()

  // 1. Scene enter effects
  for (const eff of scene.enter) {
    if ('when' in eff && eff.when) {
      extractTagsFromCondition(eff.when).forEach((t) => referencedTags.add(t))
    }
  }

  // 2. Scene body variants & additions
  for (const bv of scene.bodyVariants) {
    extractTagsFromCondition(bv.when).forEach((t) => referencedTags.add(t))
  }
  for (const add of scene.additions) {
    extractTagsFromCondition(add.when).forEach((t) => referencedTags.add(t))
  }

  // 3. Choices (conditions, outcomes, effects)
  for (const choice of scene.choices) {
    extractTagsFromCondition(choice.condition).forEach((t) => referencedTags.add(t))
    for (const ov of choice.outcomeVariants) {
      extractTagsFromCondition(ov.when).forEach((t) => referencedTags.add(t))
    }
    for (const eff of choice.effects) {
      if ('when' in eff && eff.when) {
        extractTagsFromCondition(eff.when).forEach((t) => referencedTags.add(t))
      }
    }
  }

  const echoes: EchoItem[] = []
  for (const tag of state.tags) {
    if (!referencedTags.has(tag)) continue
    const meta = TAG_METADATA[tag]
    if (!meta) continue

    // 跨卷回响 (meta.vol < scene.volume) 或 同卷侦查关键线索回响
    const isCrossVolume = meta.vol < scene.volume
    const isKeyClue = ['城投挪用线索', '公交录像带', '老同志口风', '温州调研原件', '预审口径单'].includes(tag)

    if (isCrossVolume || isKeyClue) {
      echoes.push({
        tag,
        year: meta.year,
        vol: meta.vol,
        label: isCrossVolume ? '触发回响' : '已激活',
      })
    }
  }

  // 按年份升序排序
  return echoes.sort((a, b) => a.year - b.year)
}
