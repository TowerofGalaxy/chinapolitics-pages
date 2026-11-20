import { describe, expect, it } from 'vitest'
import scenes from '../generated/story.json'
import { sceneSchema } from '../story/schema'
import { applyAction, createStory, currentScene, startGame, type GameAction, type GameState, type Story } from './engine'
import { checkpoints, newSave, replay, storyForSave, type Save } from './save'

const story = createStory(sceneSchema.array().parse(scenes))

function playTo(currentStory: Story, save: Save, target: string, selections: string): GameState {
  let state = startGame(currentStory, save.start)
  const pending = selections.split(' ')
  for (let step = 0; step < 150 && state.sceneId !== target; step++) {
    const scene = currentScene(currentStory, state)
    const choice = state.phase === 'result' || scene.type === 'passage' ? undefined : pending.shift()
    if (state.phase !== 'result' && scene.type === 'choice' && !choice) throw new Error(`缺少 ${scene.id} 的选择`)
    const action: GameAction = choice ? { type: 'choose', choices: choice.split('+') } : { type: 'continue' }
    state = applyAction(currentStory, state, action)
    save.actions.push(action)
  }
  expect(state.sceneId).toBe(target)
  return state
}

describe('数值与结局平衡', () => {
  it.each([
    { fiscal: 30, reform: 45, result: 'v05-start' },
    { fiscal: 29, reform: 45, result: 'v06-ending-c' },
    { fiscal: 30, reform: 44, result: 'v06-ending-e' },
  ])('十七大在财政 $fiscal、改革 $reform 时分流至 $result', ({ fiscal, reform, result }) => {
    const state = startGame(story, 'v04-gate17')
    Object.assign(state.stats, { central_trust: 62, local_cohesion: 35, fiscal_stability: fiscal, reform_drive: reform })
    expect(applyAction(story, state, { type: 'continue' }).sceneId).toBe(result)
  })

  it('承担责任后动用预备费垫付，保留档案并消耗财政', () => {
    const before = startGame(story, 'v04-s10')
    const tookResponsibility = applyAction(story, before, { type: 'choose', choices: ['a'] })
    const response = applyAction(story, tookResponsibility, { type: 'continue' })
    const paidCompensation = applyAction(story, response, { type: 'choose', choices: ['a'] })
    expect(paidCompensation.tags).toContain('连带问责留档')
    expect(paidCompensation.tags).toContain('预备费见底')
    expect(paidCompensation.result?.texts[0]).toContain('善后清单')
    expect(paidCompensation.result?.changes.fiscal_stability).toBe(-12)

    const noCompensation = applyAction(story, response, { type: 'choose', choices: ['b'] })
    expect(noCompensation.tags).toContain('连带问责留档')
    expect(noCompensation.tags).not.toContain('预备费见底')
  })

  it('A1 不覆盖协同度不足的 A3，连带问责留档硬阻断 A1 并稳妥导向 A2', () => {
    const state = startGame(story, 'v05-gate18')
    Object.assign(state.stats, { central_trust: 85, local_cohesion: 29, reform_drive: 75 })
    expect(applyAction(story, state, { type: 'continue' }).sceneId).toBe('v06-ending-a3')
    state.stats.local_cohesion = 30
    expect(applyAction(story, state, { type: 'continue' }).sceneId).toBe('v06-ending-a1')
    state.tags.push('连带问责留档')
    expect(applyAction(story, state, { type: 'continue' }).sceneId).toBe('v06-s17a')
    state.tags.push('大秘隐雷')
    expect(applyAction(story, state, { type: 'continue' }).sceneId).not.toBe('v06-ending-a1')
  })

  it('主动担责写检讨后，正史路线稳妥进入第六卷（v06-s17a）展开 A2', () => {
    const save = newSave()
    const route = 'c a a a a a1 b1 b b a a c2 d2 c visit+audit criticism land a a a b a c c b a+c a c c b'
    const state = playTo(story, save, 'v06-s17a', route)
    expect(state.tags).toContain('连带问责留档')
    expect(state.tags).toContain('预备费见底')
  })

  it('新旧存档分别使用对应的阶段转换和结局门槛', () => {
    const oldSave: Save = { ...newSave(), rules: 'full-2' }
    const oldStory = storyForSave(story, oldSave)
    const transition = (activeStory: Story) => {
      const before = startGame(activeStory, 'v03-close')
      Object.assign(before.stats, { cadre_trust: 90, reform_acumen: 90 })
      return applyAction(activeStory, before, { type: 'continue' }).stats
    }
    expect(transition(story)).toMatchObject({ central_trust: 61, reform_drive: 56 })
    expect(transition(oldStory)).toMatchObject({ central_trust: 59, reform_drive: 54 })

    const gate = (activeStory: Story) => {
      const before = startGame(activeStory, 'v04-gate17')
      Object.assign(before.stats, { central_trust: 62, local_cohesion: 35, fiscal_stability: 30, reform_drive: 45 })
      return applyAction(activeStory, before, { type: 'continue' }).sceneId
    }
    expect(gate(story)).toBe('v05-start')
    expect(gate(oldStory)).toBe('v06-ending-c')
  })

  it('旧版 E 结局存档按旧规则回放，不因门槛调整跳进第五卷', () => {
    const save: Save = { ...newSave(), rules: 'full-2' }
    const oldStory = storyForSave(story, save)
    const route = 'c a b b b a1 b2 b b b a c1 d1 b audit+visit private credit c a a c c a a b'
    const before = playTo(oldStory, save, 'v06-ending-e', route)
    const restored = replay(story, save).state
    expect(restored.sceneId).toBe('v06-ending-e')
    expect(restored.stats).toEqual(before.stats)
  })
})

describe('交锋记录与章节回退', () => {
  it('交锋数值和选择可以回放，不能重复领取奖励', () => {
    const save = newSave()
    const opening = 'b b c b a a1 b2 b a b a c1 d1 a audit+visit'
    const state = playTo(story, save, 'v04-s08', opening)
    const action: GameAction = { type: 'duel', round: 0, tactic: 'firm' }
    const after = applyAction(story, state, action)
    save.actions.push(action)
    const restored = replay(story, save).state
    expect(restored.stats).toEqual(after.stats)
    expect(restored.duelPicks).toEqual(after.duelPicks)
    expect(restored.duelPicks['v04-s08'][0].id).toBe('firm')
    expect(() => applyAction(story, restored, action)).toThrow()
    expect(() => applyAction(story, restored, { type: 'duel', round: 2, tactic: 'firm' })).toThrow()
  })

  it('交锋加分遵守向心力警戒，显示实际变化', () => {
    const state = startGame(story, 'v04-s08')
    state.stats.local_cohesion = 35
    const after = applyAction(story, state, { type: 'duel', round: 0, tactic: 'firm' })
    expect(after.stats.reform_drive).toBe(state.stats.reform_drive)
    expect(after.duelPicks['v04-s08'][0].changes).toEqual({})
  })

  it('只能回到实际抵达过的章节，并按当时的选择恢复状态', () => {
    const save = newSave()
    const opening = 'b b c b a a1 b2 b a b a c1 d1 a audit+visit'
    playTo(story, save, 'v04-s08', opening)
    const chapters = checkpoints(story, save)
    expect(chapters.map((chapter) => chapter.title)).toEqual([
      '第一卷 · 书斋与激流', '第二卷 · 前门东大街的风', '第三卷 · 东华门沉潜与外宣破冰', '第四卷 · 主政江淮与两会大考',
    ])
    const fourth = chapters[3]
    const restored = replay(story, { ...save, actions: save.actions.slice(0, fourth.actionCount), draft: [] }).state
    expect(restored.sceneId).toBe('v04-s07')
    expect(restored.actionPoints.vol4_ap).toBe(2)
    expect(restored.history['v04-s07']).toBeUndefined()
  })
})
