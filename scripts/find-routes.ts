import compiled from '../src/generated/story.json'
import { sceneSchema } from '../src/story/schema'
import { applyAction, available, createStory, currentScene, startGame } from '../src/game/engine'

const story = createStory(sceneSchema.array().parse(compiled))
const endingIds = new Set(['v01-ending-b', 'v06-ending-c', 'v06-ending-d', 'v06-ending-e', 'v06-ending-a1', 'v06-ending-a2', 'v06-ending-a3'])
const found = new Map<string, string[]>()
let seed = 0x671b9

function random(max: number): number {
  seed ^= seed << 13
  seed ^= seed >>> 17
  seed ^= seed << 5
  return (seed >>> 0) % max
}

for (let run = 0; run < 200_000 && found.size < endingIds.size; run++) {
  let state = startGame(story)
  const route: string[] = []
  for (let step = 0; step < 150; step++) {
    const scene = currentScene(story, state)
    if (state.phase === 'ending') {
      if (endingIds.has(scene.id) && !found.has(scene.id)) found.set(scene.id, route)
      break
    }
    if (state.phase === 'result' || scene.type === 'passage') {
      state = applyAction(story, state, { type: 'continue' })
      continue
    }
    const options = scene.choices.filter((choice) => available(state, choice))
    if (options.length < scene.select) throw new Error(`${scene.id}: 没有足够可选项`)
    const choices: string[] = []
    for (let index = 0; index < scene.select; index++) {
      choices.push(options.splice(random(options.length), 1)[0].id)
    }
    route.push(`${scene.id}=${choices.join('+')}`)
    state = applyAction(story, state, { type: 'choose', choices })
  }
}

for (const ending of [...endingIds].sort()) {
  const route = found.get(ending)
  console.log(`${ending}: ${route ? route.join(' ') : '未找到'}`)
}
if (found.size !== endingIds.size) process.exitCode = 1
