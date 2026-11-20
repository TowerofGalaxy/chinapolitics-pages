import { expect, it } from 'vitest'
import scenes from '../generated/story.json'
import { sceneSchema } from '../story/schema'
import { applyAction, createStory, currentScene, startGame } from './engine'

it('A3 不把玩家没有经历的改革反弹和外媒争议写成既成事实', () => {
  const story = createStory(sceneSchema.array().parse(scenes))
  const choices = 'a b a b b a2 b1 b b a c c2 d2 a bus+visit taskforce land b a a c a b b a b+c c c b a'.split(' ')
  let state = startGame(story)
  for (let step = 0; state.phase !== 'ending' && step < 150; step++) {
    const scene = currentScene(story, state)
    if (state.phase === 'result' || scene.type === 'passage') {
      state = applyAction(story, state, { type: 'continue' })
      continue
    }
    const choice = choices.shift()
    expect(choice, `缺少 ${scene.id} 的选择`).toBeDefined()
    state = applyAction(story, state, { type: 'choose', choices: choice!.split('+') })
  }
  expect(state.sceneId).toBe('v06-ending-a3')
  expect(state.tags).not.toContain('民意过半硬杠反弹')
  expect(state.tags).not.toContain('自揭家丑非议')
  expect(state.tags).not.toContain('系统内保守派侧目')
  expect(currentScene(story, state).body).not.toContain('干部考评改革激化了多省抵触')
  expect(currentScene(story, state).body).not.toContain('外媒吹风会上的答问亦被部分老同志存底非议')
})
