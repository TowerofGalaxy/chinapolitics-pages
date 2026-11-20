import { describe, expect, it } from 'vitest'
import scenes from '../generated/story.json'
import { sceneSchema } from '../story/schema'
import { applyAction, createStory, currentScene, startGame, type GameAction } from './engine'
import { newSave, replay, storyForSave, type Save } from './save'

const story = createStory(sceneSchema.array().parse(scenes))

describe('上版存档兼容', () => {
  it('旧版承担责任并落实善后进入 A1 的存档，更新后保持原结局', () => {
    const save: Save = { ...newSave(), rules: 'full-3' }
    const previousStory = storyForSave(story, save)
    const choices = 'c a a a a a1 b1 b b a a c2 d2 c visit+audit criticism land a a a b a c c b a+c a c c b'.split(' ')
    let state = startGame(previousStory)
    for (let step = 0; state.phase !== 'ending' && step < 150; step++) {
      const scene = currentScene(previousStory, state)
      const next = state.phase === 'result' || scene.type === 'passage' ? undefined : choices.shift()
      if (state.phase === 'scene' && scene.type === 'choice' && !next) throw new Error(`缺少 ${scene.id} 的选择`)
      const action: GameAction = next ? { type: 'choose', choices: next.split('+') } : { type: 'continue' }
      state = applyAction(previousStory, state, action)
      save.actions.push(action)
    }
    expect(state.sceneId).toBe('v06-ending-a1')
    expect(state.tags).toContain('连带问责留档')
    expect(state.tags).toContain('问责善后落实')

    const restored = replay(story, save).state
    expect(restored.sceneId).toBe('v06-ending-a1')
    expect(restored.stats).toEqual(state.stats)
    expect(restored.tags).toContain('问责善后落实')

    // 新档案使用当前剧情设定：同样的留档会进入 A2 线。
    const current = replay(story, { ...save, rules: 'full-4' }).state
    expect(current.sceneId).toBe('v06-s17a')
    expect(current.tags).not.toContain('问责善后落实')
  })

  it('上版交锋选择和数值在更新后仍能回放', () => {
    const save: Save = { ...newSave(), rules: 'full-3' }
    const previousStory = storyForSave(story, save)
    const choices = 'b b c b a a1 b2 b a b a c1 d1 a audit+visit'.split(' ')
    let state = startGame(previousStory)
    for (let step = 0; state.sceneId !== 'v04-s08' && step < 100; step++) {
      const scene = currentScene(previousStory, state)
      const next = state.phase === 'result' || scene.type === 'passage' ? undefined : choices.shift()
      if (state.phase === 'scene' && scene.type === 'choice' && !next) throw new Error(`缺少 ${scene.id} 的选择`)
      const action: GameAction = next ? { type: 'choose', choices: next.split('+') } : { type: 'continue' }
      state = applyAction(previousStory, state, action)
      save.actions.push(action)
    }
    expect(state.sceneId).toBe('v04-s08')
    const duel: GameAction = { type: 'duel', round: 0, tactic: 'firm' }
    state = applyAction(previousStory, state, duel)
    save.actions.push(duel)
    const restored = replay(story, save).state
    expect(restored.duelPicks).toEqual(state.duelPicks)
    expect(restored.stats).toEqual(state.stats)
  })
})
