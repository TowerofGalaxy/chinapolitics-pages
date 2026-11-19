import compiled from '../src/generated/story.json'
import dictionary from '../variables.json'
import { sceneSchema, type Scene } from '../src/story/schema'
import { createStory } from '../src/game/engine'

const story = createStory(sceneSchema.array().parse(compiled))
const start = 'v01-s00a'
const visiting = new Set<string>()
const visited = new Set<string>()
const order: string[] = []

function targets(scene: Scene): string[] {
  return [...new Set([
    scene.next,
    ...scene.routes.map((route) => route.next),
    ...scene.choices.map((choice) => choice.next),
  ].filter((id): id is string => Boolean(id)))]
}

function walk(id: string): void {
  if (visiting.has(id)) throw new Error(`剧情存在循环：${id}`)
  if (visited.has(id)) return
  const scene = story.get(id)
  if (!scene) throw new Error(`找不到场景：${id}`)
  visiting.add(id)
  for (const target of targets(scene)) walk(target)
  visiting.delete(id)
  visited.add(id)
  order.push(id)
}

walk(start)
order.reverse()

type Spending = Record<string, number>
const spending = new Map<string, Spending>([[start, {}]])
let choiceScenes = 0
let endings = 0

for (const id of order) {
  const scene = story.get(id)!
  const incoming = spending.get(id)!
  const outgoing = { ...incoming }
  if (scene.type === 'ending') endings++
  if (scene.type === 'choice') {
    choiceScenes++
    const unconditional = scene.choices.filter((choice) => !choice.condition).length
    if (unconditional < scene.select) {
      throw new Error(`${id} 没有足够的无条件选项，无法证明每个状态都能继续`)
    }
    if (scene.ap) {
      const initial = dictionary.action_points[scene.ap as keyof typeof dictionary.action_points]?.initial
      outgoing[scene.ap] = (outgoing[scene.ap] ?? 0) + scene.select
      if (initial === undefined || outgoing[scene.ap] > initial) {
        throw new Error(`${id} 可能没有足够的行动点`)
      }
    }
  }
  if (scene.type !== 'ending' && !targets(scene).length) throw new Error(`${id} 没有后续场景`)
  for (const next of targets(scene)) {
    const targetSpending = spending.get(next) ?? {}
    for (const [ap, used] of Object.entries(outgoing)) {
      targetSpending[ap] = Math.max(targetSpending[ap] ?? 0, used)
    }
    spending.set(next, targetSpending)
  }
}

console.log(`检查 ${visited.size} 个场景、${choiceScenes} 个选择节点和 ${endings} 个结局。`)
console.log('所有路径无循环，行动点充足，每个选择节点至少有足够的无条件选项。')
