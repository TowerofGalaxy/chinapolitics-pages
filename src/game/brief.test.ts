import { describe, expect, it } from 'vitest'
import scenes from '../generated/story.json'
import { sceneSchema } from '../story/schema'
import { applyAction, createStory, currentScene, meetsCondition, startGame } from './engine'
import { newSave, replay } from './save'

const story = createStory(sceneSchema.array().parse(scenes))

describe('第四卷案头质询', () => {
  it.each([
    { choice: 'land', own: '土地申报表', other: '信贷穿透审计报告' },
    { choice: 'credit', own: '信贷穿透审计报告', other: '土地申报表' },
  ])('选择 $choice 后常委会只出现对应的开场回应', ({ choice, own, other }) => {
    const before = startGame(story, 'v04-brief')
    const result = applyAction(story, before, { type: 'choose', choices: [choice] })
    expect(result.stats).toEqual(before.stats)
    const meeting = applyAction(story, result, { type: 'continue' })
    expect(meeting.sceneId).toBe('v04-s09')
    const additions = currentScene(story, meeting).additions
      .filter((item) => meetsCondition(meeting, item.when))
      .map((item) => item.body)
      .join('\n')
    expect(additions).toContain(own)
    expect(additions).not.toContain(other)
  })

  it('旧存档已读过卷宗时保留原进度，不凭空替玩家选择', () => {
    const legacyStory = new Map(story)
    const briefing = legacyStory.get('v04-brief')!
    legacyStory.set(briefing.id, { ...briefing, type: 'passage', choices: [] })
    const save = newSave()
    save.rules = 'full-1'
    let state = startGame(legacyStory)
    const choices = 'b b c b a a1 b2 b a b a c1 d1 a audit+visit private'.split(' ')
    let steps = 0
    while (state.sceneId !== 'v04-s09' && steps++ < 100) {
      const scene = currentScene(legacyStory, state)
      const action = state.phase === 'result' || scene.type === 'passage'
        ? { type: 'continue' as const }
        : { type: 'choose' as const, choices: choices.shift()!.split('+') }
      save.actions.push(action)
      state = applyAction(legacyStory, state, action)
    }
    expect(state.sceneId).toBe('v04-s09')
    expect(choices).toEqual([])
    const restored = replay(story, save).state
    expect(restored.sceneId).toBe('v04-s09')
    expect(restored.stats).toEqual(state.stats)
    expect(restored.history['v04-brief']).toBeUndefined()
    save.actions.push({ type: 'choose', choices: ['a'] }, { type: 'continue' })
    expect(replay(story, save).state.sceneId).toBe('v04-s10')
  })

  it('选择质询点 land：免疫土地融资依赖扣分，且选项 3-A 额外获得中央信任度 +2', () => {
    let state = startGame(story, 'v04-brief')
    state.tags.push('土地融资依赖')
    const initialFiscal = state.stats.fiscal_stability
    const initialCentral = state.stats.central_trust

    // 选 land
    state = applyAction(story, state, { type: 'choose', choices: ['land'] })
    state = applyAction(story, state, { type: 'continue' }) // 进入 v04-s09
    state = applyAction(story, state, { type: 'choose', choices: ['a'] }) // s09 选 a
    state = applyAction(story, state, { type: 'continue' }) // 进入 v04-s10

    // 检查进入 s10 时，财政稳态值并未扣除 -3（免疫了土地融资依赖扣分）
    // （注意：s09 选 a 本身扣了 fiscal_stability -10，初始 60 - 10 = 50）
    expect(state.stats.fiscal_stability).toBe(initialFiscal - 10)

    // 选 3-A
    const preCentral = state.stats.central_trust
    state = applyAction(story, state, { type: 'choose', choices: ['a'] })
    // central_trust 应增加 15 + 2 = 17
    expect(state.result?.changes.central_trust).toBe(17)
  })

  it('选择质询点 credit：即使无城投挪用线索且财政不达标，亦直接解锁选项 3-B', () => {
    let state = startGame(story, 'v04-brief')
    state.stats.fiscal_stability = 40 // 低于 60
    state.tags = state.tags.filter((t) => t !== '城投挪用线索')

    // 选 credit
    state = applyAction(story, state, { type: 'choose', choices: ['credit'] })
    state = applyAction(story, state, { type: 'continue' }) // 进入 v04-s09
    state = applyAction(story, state, { type: 'choose', choices: ['a'] }) // s09 选 a
    state = applyAction(story, state, { type: 'continue' }) // 进入 v04-s10

    const scene10 = currentScene(story, state)
    const choiceB = scene10.choices.find((c) => c.id === 'b')!
    expect(meetsCondition(state, choiceB.condition)).toBe(true)
  })
})
