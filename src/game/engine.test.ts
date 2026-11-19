import { describe, expect, it } from 'vitest'
import scenes from '../generated/story.json'
import { sceneSchema } from '../story/schema'
import { applyAction, available, createStory, currentScene, startGame, type GameState } from './engine'
import { newSave, replay } from './save'

const story = createStory(sceneSchema.array().parse(scenes))
const startSlice = () => startGame(story, 'v04-s07')

function investigate(choices: string[], state = startSlice()): GameState {
  return applyAction(story, state, { type: 'choose', choices })
}

function meeting(choices: string[], state = startSlice()): GameState {
  return applyAction(story, investigate(choices, state), { type: 'continue' })
}

describe('第四卷调查和大会', () => {
  it.each([
    { choices: ['bus', 'audit'], fiscal: 55, local: 60, screening: true, private: true },
    { choices: ['bus', 'visit'], fiscal: 60, local: 65, screening: true, private: false },
    { choices: ['audit', 'visit'], fiscal: 55, local: 65, screening: false, private: true },
  ])('根据调查结果解锁选择 $choices', ({ choices, fiscal, local, screening, private: privateChoice }) => {
    const state = meeting(choices)
    expect(state.stats.fiscal_stability).toBe(fiscal)
    expect(state.stats.local_cohesion).toBe(local)
    expect(state.actionPoints.vol4_ap).toBe(0)
    const options = currentScene(story, state).choices
    expect(available(state, options.find((choice) => choice.id === 'screening')!)).toBe(screening)
    expect(available(state, options.find((choice) => choice.id === 'private')!)).toBe(privateChoice)
    expect(available(state, options.find((choice) => choice.id === 'criticism')!)).toBe(true)
    expect(available(state, options.find((choice) => choice.id === 'taskforce')!)).toBe(true)
  })

  it.each([
    { choice: 'screening', stats: [60, 50, 55, 55], tag: '机关震荡反弹' },
    { choice: 'criticism', stats: [56, 65, 55, 45], tag: '整顿流于形式' },
    { choice: 'taskforce', stats: [55, 55, 45, 58], tag: '土地融资依赖' },
    { choice: 'private', stats: [55, 56, 61, 55], tag: '建委隐形积怨' },
  ])('会场 $choice 按剧本结算数值和标记', ({ choice, stats, tag }) => {
    const result = applyAction(story, meeting(['bus', 'audit']), { type: 'choose', choices: [choice] })
    expect([result.stats.central_trust, result.stats.local_cohesion, result.stats.fiscal_stability, result.stats.reform_drive]).toEqual(stats)
    expect(result.tags).toContain(tag)
  })

  it('前卷标记影响调查成本、入场效果和选项加成', () => {
    const start = startSlice()
    start.tags.push('苏南经济底稿', '老辈训诫', '不务正业非议', '现代治理工具箱')
    const state = meeting(['audit', 'visit'], start)
    expect(state.stats.fiscal_stability).toBe(57)
    expect(state.stats.local_cohesion).toBe(66)
    const result = applyAction(story, state, { type: 'choose', choices: ['private'] })
    expect(result.stats.reform_drive).toBe(56)
  })

  it('向心力警戒按选择前状态将改革正收益减半并向下取整', () => {
    const state = meeting(['bus', 'audit'])
    state.stats.local_cohesion = 35
    state.tags.push('现代治理工具箱')
    const result = applyAction(story, state, { type: 'choose', choices: ['private'] })
    expect(result.stats.reform_drive).toBe(53)
    expect(result.stats.local_cohesion).toBe(31)
  })

  it('非法选择不修改原状态', () => {
    const start = startSlice()
    const original = structuredClone(start)
    expect(() => investigate(['bus', 'bus'], start)).toThrow()
    expect(() => investigate(['bus'], start)).toThrow()
    expect(() => investigate(['bus', 'missing'], start)).toThrow()
    expect(start).toEqual(original)
    const state = meeting(['audit', 'visit'])
    expect(() => applyAction(story, state, { type: 'choose', choices: ['screening'] })).toThrow()
  })
})

describe('存档回放', () => {
  it('恢复选择草稿、结果页和下一场，且效果只结算一次', () => {
    const save = newSave()
    save.start = 'v04-s07'
    save.rules = 'slice-1'
    save.draft = ['bus']
    expect(replay(story, save).save.draft).toEqual(['bus'])
    save.draft = []
    save.actions.push({ type: 'choose', choices: ['bus', 'audit'] })
    expect(replay(story, save).state.stats.fiscal_stability).toBe(55)
    expect(replay(story, save).state.phase).toBe('result')
    save.actions.push({ type: 'continue' }, { type: 'choose', choices: ['private'] })
    const restored = replay(story, save).state
    expect(restored.phase).toBe('result')
    expect(restored.stats.fiscal_stability).toBe(61)
    expect(restored.tags.filter((tag) => tag === '建委隐形积怨')).toHaveLength(1)
  })

  it('拒绝损坏或不符合剧情条件的存档', () => {
    expect(() => replay(story, { ...newSave(), rules: 'unknown' })).toThrow()
    const save = newSave()
    save.start = 'v04-s07'
    save.rules = 'slice-1'
    save.actions.push({ type: 'choose', choices: ['audit', 'visit'] }, { type: 'continue' })
    save.draft = ['screening']
    expect(() => replay(story, save)).toThrow()
    save.draft = []
    save.actions.push({ type: 'choose', choices: ['screening'] })
    expect(() => replay(story, save)).toThrow()
  })
})

describe('前三卷与阶段转换', () => {
  function chooseAndContinue(state: GameState, ...choices: string[]): GameState {
    const result = applyAction(story, state, { type: 'choose', choices })
    return applyAction(story, result, { type: 'continue' })
  }

  it('第一卷学界选项直接进入 B 结局', () => {
    let state = startGame(story)
    expect(state.tags).toContain('纯粹知识分子底色')
    state = chooseAndContinue(state, 'b')
    state = chooseAndContinue(state, 'd')
    expect(state.sceneId).toBe('v01-ending-b')
    expect(state.phase).toBe('ending')
    expect(state.tags).toContain('象牙塔学者')
  })

  it('前三卷主线能衔接第四卷，保留前置标记', () => {
    let state = startGame(story)
    for (const choice of ['c', 'b', 'a']) state = chooseAndContinue(state, choice)
    expect(state.sceneId).toBe('v01-close')
    state = applyAction(story, state, { type: 'continue' })
    for (const choice of ['a', 'c', 'a2', 'b1', 'b', 'b']) state = chooseAndContinue(state, choice)
    expect(state.sceneId).toBe('v02-close')
    state = applyAction(story, state, { type: 'continue' })
    for (const choice of ['b', 'b', 'c1', 'd2', 'b']) state = chooseAndContinue(state, choice)
    expect(state.sceneId).toBe('v03-close')
    state = applyAction(story, state, { type: 'continue' })
    expect(state.sceneId).toBe('v04-transition')
    expect(state.tags).toContain('老同志的信赖档案')
    state = applyAction(story, state, { type: 'continue' })
    expect(state.sceneId).toBe('v04-s07')
    expect(state.actionPoints.vol4_ap).toBe(2)
    const investigation = investigate(['audit', 'visit'], state)
    expect(investigation.stats.local_cohesion).toBe(68)
    expect(investigation.tags).toContain('老同志口风')
  })

  it('按向下取整、上下限和既有标记转换阶段属性', () => {
    const state = startGame(story, 'v03-s06')
    state.stats.cadre_trust = 46
    state.stats.reform_acumen = 47
    state.tags.push('边缘平调序列', '报批越界通报')
    const afterChoice = chooseAndContinue(state, 'b')
    const transition = applyAction(story, afterChoice, { type: 'continue' })
    expect(transition.sceneId).toBe('v04-transition')
    expect(transition.stats.central_trust).toBe(51)
    expect(transition.stats.reform_drive).toBe(48)
  })

  it('对话根据选项提交前的标记变化', () => {
    let state = startGame(story)
    state = chooseAndContinue(state, 'c')
    state = chooseAndContinue(state, 'c')
    const result = applyAction(story, state, { type: 'choose', choices: ['a'] })
    expect(result.result?.texts[0]).toContain('业余讨论班的事')
    expect(result.result?.texts[0]).not.toContain('若持有')
  })
})
