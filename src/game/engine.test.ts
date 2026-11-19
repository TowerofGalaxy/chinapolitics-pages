import { describe, expect, it } from 'vitest'
import scenes from '../generated/story.json'
import { sceneSchema } from '../story/schema'
import { applyAction, available, createStory, currentScene, startGame, type GameState } from './engine'
import { newSave, replay } from './save'

const story = createStory(sceneSchema.array().parse(scenes))

function investigate(choices: string[], state = startGame(story)): GameState {
  return applyAction(story, state, { type: 'choose', choices })
}

function meeting(choices: string[], state = startGame(story)): GameState {
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
    const start = startGame(story)
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
    const start = startGame(story)
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
    save.actions.push({ type: 'choose', choices: ['audit', 'visit'] }, { type: 'continue' })
    save.draft = ['screening']
    expect(() => replay(story, save)).toThrow()
    save.draft = []
    save.actions.push({ type: 'choose', choices: ['screening'] })
    expect(() => replay(story, save)).toThrow()
  })
})
