import { describe, expect, it } from 'vitest'
import compiled from '../generated/story.json'
import { sceneSchema } from '../story/schema'
import { applyAction, createStory, currentScene, startGame } from './engine'

const story = createStory(sceneSchema.array().parse(compiled))

const routes: Record<string, string> = {
  'v01-ending-b': 'c d',
  'v06-ending-a1': 'b b c b a a1 b2 b a b a c1 d1 a audit+visit private a b c b c c c b a+c b c c b',
  'v06-ending-a2': 'a b b b b a1 b2 a c a a c1 d1 a bus+visit screening b a a b b a c b c+a a a a b a a a',
  'v06-ending-a3': 'a c b a b a2 b2 a a b b c1 d2 a visit+bus screening b a b b b a b b b+c a a b c',
  'v06-ending-c': 'c c a a c a2 b1 a c a b c2 d1 b bus+audit screening a a a c c a a b',
  'v06-ending-d': 'a b b b c a1 b1 a a a c c2 d1 b visit+bus screening a a a a a a b b',
  'v06-ending-e': 'c a b b b a1 b2 b b b a c1 d1 b audit+visit private c a a c c a a b',
}

describe('结局可达性', () => {
  for (const [ending, choices] of Object.entries(routes)) {
    it(`从开局到达 ${ending}`, () => {
      let state = startGame(story)
      const pending = choices.split(' ')
      let steps = 0
      while (state.phase !== 'ending' && steps++ < 150) {
        const scene = currentScene(story, state)
        if (state.phase === 'result' || scene.type === 'passage') {
          state = applyAction(story, state, { type: 'continue' })
        } else {
          const next = pending.shift()
          expect(next, `缺少 ${scene.id} 的选择`).toBeDefined()
          state = applyAction(story, state, { type: 'choose', choices: next!.split('+') })
        }
      }
      expect(state.sceneId).toBe(ending)
      expect(state.phase).toBe('ending')
      expect(pending).toEqual([])
    })
  }
})
