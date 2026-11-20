// 均匀随机模拟用于比较规则版本，不代表真实玩家的行为或结局概率。
import scenes from '../src/generated/story.json'
import { sceneSchema } from '../src/story/schema'
import { applyAction, available, createStory, currentScene, startGame, type Story } from '../src/game/engine'
import { newSave, storyForSave } from '../src/game/save'
import { DUELS } from '../src/ui/duels'

const runs = Number(process.argv[2] ?? 25_000)
if (!Number.isInteger(runs) || runs < 1 || runs > 1_000_000) throw new Error('模拟次数必须是 1 至 1000000 的整数')
const story = createStory(sceneSchema.array().parse(scenes))
const legacy = storyForSave(story, { ...newSave(), rules: 'full-2' })
const previous = storyForSave(story, { ...newSave(), rules: 'full-3' })

function simulate(activeStory: Story, withDuels: boolean) {
  let seed = 0x5eeda123
  const endings: Record<string, number> = {}
  let fifth = 0
  let decisiveRecord = 0
  let rectifiedRecord = 0
  function random(max: number): number {
    seed ^= seed << 13
    seed ^= seed >>> 17
    seed ^= seed << 5
    return Math.floor(((seed >>> 0) / 4_294_967_296) * max)
  }
  for (let run = 0; run < runs; run++) {
    let state = startGame(activeStory)
    let steps = 0
    while (state.phase !== 'ending' && steps++ < 200) {
      const scene = currentScene(activeStory, state)
      if (scene.id === 'v05-start' && state.phase === 'scene') fifth++
      if (scene.id === 'v05-gate18' && state.phase === 'scene') {
        if (state.tags.includes('连带问责留档')) decisiveRecord++
        if (state.tags.includes('问责善后落实')) rectifiedRecord++
      }
      if (state.phase === 'result' || scene.type === 'passage') {
        state = applyAction(activeStory, state, { type: 'continue' })
        continue
      }
      if (withDuels && DUELS[scene.id] && !state.duelPicks[scene.id]) {
        for (const [round, data] of DUELS[scene.id].rounds.entries()) {
          if (!data.tactics?.length) continue
          const tactic = data.tactics[random(data.tactics.length)]
          state = applyAction(activeStory, state, { type: 'duel', round, tactic: tactic.id })
        }
      }
      const options = scene.choices.filter((choice) => available(state, choice))
      if (options.length < scene.select) throw new Error(`${scene.id}: 可选项不足`)
      const selected: string[] = []
      for (let index = 0; index < scene.select; index++) selected.push(options.splice(random(options.length), 1)[0].id)
      state = applyAction(activeStory, state, { type: 'choose', choices: selected })
    }
    if (state.phase !== 'ending') throw new Error('模拟未能抵达结局')
    endings[state.sceneId] = (endings[state.sceneId] ?? 0) + 1
  }
  return { runs, fifth, decisiveRecord, rectifiedRecord, endings }
}

console.log(JSON.stringify({
  assumption: '均匀随机选择当前可用选项；结果不是实际玩家的结局概率',
  olderV2WithoutDuels: simulate(legacy, false),
  previousV3WithoutDuels: simulate(previous, false),
  currentV4WithoutDuels: simulate(story, false),
  currentV4WithDuels: simulate(story, true),
}, null, 2))
