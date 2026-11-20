import { describe, expect, it } from 'vitest'
import compiled from '../generated/story.json'
import { sceneSchema } from '../story/schema'
import { applyAction, createStory, currentScene, meetsCondition, startGame } from './engine'

const story = createStory(sceneSchema.array().parse(compiled))

// Reach scene 17-A on the A2 route
function reachVol6Scene17A() {
  const choices = 'a b b b b a1 b2 a c a a c1 d1 a bus+visit screening land b a a b b a c b c+a a a a b'.split(' ')
  let state = startGame(story)
  let steps = 0
  while (state.sceneId !== 'v06-s17a' && steps++ < 150) {
    const scene = currentScene(story, state)
    if (state.phase === 'result' || scene.type === 'passage') {
      state = applyAction(story, state, { type: 'continue' })
    } else {
      const next = choices.shift()
      if (!next) throw new Error(`Ran out of choices before v06-s17a, currently at ${scene.id}`)
      state = applyAction(story, state, { type: 'choose', choices: next.split('+') })
    }
  }
  expect(state.sceneId).toBe('v06-s17a')
  return state
}

describe('卷六终章叙事回报四维分流', () => {
  it('双改革路线 (18-1B + 18-2A) 展开长篇改革心路回忆', () => {
    let state = reachVol6Scene17A()
    // 17-A choose a
    state = applyAction(story, state, { type: 'choose', choices: ['a'] })
    state = applyAction(story, state, { type: 'continue' })

    // 18-1 choose b (达沃斯主动阐释准入与环保硬考核) -> 获得 坦陈求是
    expect(state.sceneId).toBe('v06-s18r1')
    state = applyAction(story, state, { type: 'choose', choices: ['b'] })
    state = applyAction(story, state, { type: 'continue' })

    // 18-2 choose a (群团改革推非政府组织社会评估) -> 获得 未竞的改革之弦
    expect(state.sceneId).toBe('v06-s18r2')
    state = applyAction(story, state, { type: 'choose', choices: ['a'] })
    state = applyAction(story, state, { type: 'continue' })

    // 到达 场景 19 (海淀旧院)
    expect(state.sceneId).toBe('v06-s19')
    const scene19 = currentScene(story, state)
    const activeAdditions = scene19.additions.filter((a) => meetsCondition(state, a.when)).map((a) => a.body)

    // 验证包含双改革长篇回忆与达沃斯发言速记
    expect(activeAdditions.some((body) => body.includes('四十年跋涉便不算虚掷'))).toBe(true)
    expect(activeAdditions.some((body) => body.includes('达沃斯世界经济论坛'))).toBe(true)
    // 验证不包含双审慎回忆
    expect(activeAdditions.some((body) => body.includes('约翰内斯堡冷雨中九万人瞩目的体育场看台'))).toBe(false)
  })

  it('双审慎路线 (18-1A + 18-2B) 展开长篇大国礼宾与权力退场纪律回忆', () => {
    let state = reachVol6Scene17A()
    // 17-A choose b
    state = applyAction(story, state, { type: 'choose', choices: ['b'] })
    state = applyAction(story, state, { type: 'continue' })

    // 18-1 choose a (严守外事礼宾口径) -> 获得 端方国士
    expect(state.sceneId).toBe('v06-s18r1')
    state = applyAction(story, state, { type: 'choose', choices: ['a'] })
    state = applyAction(story, state, { type: 'continue' })

    // 18-2 choose b (划死个人权力退场边界) -> 获得 云淡风轻
    expect(state.sceneId).toBe('v06-s18r2')
    state = applyAction(story, state, { type: 'choose', choices: ['b'] })
    state = applyAction(story, state, { type: 'continue' })

    // 到达 场景 19 (海淀旧院)
    expect(state.sceneId).toBe('v06-s19')
    const scene19 = currentScene(story, state)
    const activeAdditions = scene19.additions.filter((a) => meetsCondition(state, a.when)).map((a) => a.body)

    // 验证包含双审慎大国礼宾与彻底清空文件柜回忆
    expect(activeAdditions.some((body) => body.includes('把手洗得干干净净交还给体制'))).toBe(true)
    expect(activeAdditions.some((body) => body.includes('外事照会册'))).toBe(true)
    // 验证不包含双改革回忆
    expect(activeAdditions.some((body) => body.includes('四十年跋涉便不算虚掷'))).toBe(false)
  })

  it('混合路线 A (18-1A + 18-2A) 展开外事审慎与对内改革折冲回忆', () => {
    let state = reachVol6Scene17A()
    state = applyAction(story, state, { type: 'choose', choices: ['a'] })
    state = applyAction(story, state, { type: 'continue' })

    // 18-1 choose a
    state = applyAction(story, state, { type: 'choose', choices: ['a'] })
    state = applyAction(story, state, { type: 'continue' })

    // 18-2 choose a
    state = applyAction(story, state, { type: 'choose', choices: ['a'] })
    state = applyAction(story, state, { type: 'continue' })

    expect(state.sceneId).toBe('v06-s19')
    const scene19 = currentScene(story, state)
    const activeAdditions = scene19.additions.filter((a) => meetsCondition(state, a.when)).map((a) => a.body)

    expect(activeAdditions.some((body) => body.includes('外圆内方、在守规矩与求突破之间极力折冲'))).toBe(true)
  })

  it('混合路线 B (18-1B + 18-2B) 展开涉外开诚与退场清明回忆', () => {
    let state = reachVol6Scene17A()
    state = applyAction(story, state, { type: 'choose', choices: ['a'] })
    state = applyAction(story, state, { type: 'continue' })

    // 18-1 choose b
    state = applyAction(story, state, { type: 'choose', choices: ['b'] })
    state = applyAction(story, state, { type: 'continue' })

    // 18-2 choose b
    state = applyAction(story, state, { type: 'choose', choices: ['b'] })
    state = applyAction(story, state, { type: 'continue' })

    expect(state.sceneId).toBe('v06-s19')
    const scene19 = currentScene(story, state)
    const activeAdditions = scene19.additions.filter((a) => meetsCondition(state, a.when)).map((a) => a.body)

    expect(activeAdditions.some((body) => body.includes('能争时不避难，当退处不恋权'))).toBe(true)
  })
})
