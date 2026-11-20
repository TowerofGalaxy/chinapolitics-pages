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
})
