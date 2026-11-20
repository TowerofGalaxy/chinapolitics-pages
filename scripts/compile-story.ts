import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises'
import { createHash } from 'node:crypto'
import path from 'node:path'
import { parse } from 'yaml'
import { sceneSchema, type Condition, type Effect, type Scene } from '../src/story/schema'
import dictionary from '../variables.json'
import sourceRevisions from '../content/source-revisions.json'

const root = process.cwd()
const contentRoot = path.join(root, 'content')
const knownStats = new Set([
  ...Object.keys(dictionary.stage_1_variables),
  ...Object.keys(dictionary.stage_2_variables),
])
const knownActionPoints = new Set(Object.keys(dictionary.action_points))
const knownTags = new Set(Object.keys(dictionary.tags))

async function findYaml(directory: string): Promise<string[]> {
  const entries = await readdir(directory, { withFileTypes: true })
  const nested = await Promise.all(entries.map(async (entry) => {
    const filename = path.join(directory, entry.name)
    if (entry.isDirectory()) return findYaml(filename)
    return entry.isFile() && /\.ya?ml$/i.test(entry.name) ? [filename] : []
  }))
  return nested.flat().sort()
}

function validateCondition(condition: Condition | undefined, source: string): void {
  if (!condition) return
  if ('tag' in condition && !knownTags.has(condition.tag)) throw Error(`${source}: 未定义标记 ${condition.tag}`)
  if ('stat' in condition && !knownStats.has(condition.stat)) throw Error(`${source}: 未定义属性 ${condition.stat}`)
  if ('all' in condition) condition.all.forEach((child) => validateCondition(child, source))
  if ('any' in condition) condition.any.forEach((child) => validateCondition(child, source))
  if ('not' in condition) validateCondition(condition.not, source)
}

function validateEffects(effects: Effect[], source: string): void {
  for (const effect of effects) {
    if (effect.type === 'stage-two' || effect.type === 'stage-two-legacy') continue
    validateCondition(effect.when, source)
    if (effect.type === 'change' && !knownStats.has(effect.stat)) throw Error(`${source}: 未定义属性 ${effect.stat}`)
    if (effect.type !== 'change' && !knownTags.has(effect.tag)) throw Error(`${source}: 未定义标记 ${effect.tag}`)
  }
}

async function readMarkdown(directory: string, reference: string): Promise<string> {
  const filename = path.resolve(directory, reference)
  const relative = path.relative(contentRoot, filename)
  if (relative.startsWith('..') || path.isAbsolute(relative) || path.extname(filename) !== '.md') {
    throw Error(`正文路径不在 content 中: ${reference}`)
  }
  const text = await readFile(filename, 'utf8')
  if (!text.trim()) throw Error(`正文为空: ${filename}`)
  return text.trim()
}

async function main() {
  for (const [filename, expected] of Object.entries(sourceRevisions)) {
    try {
      const source = (await readFile(path.join(root, filename), 'utf8')).replace(/\r\n/g, '\n')
      const actual = createHash('sha256').update(source).digest('hex')
      if (actual !== expected) console.warn(`分卷剧本与网页接入快照不同，请核对：${filename}`)
    } catch {
      console.warn(`找不到分卷剧本，请核对网页内容：${filename}`)
    }
  }
  const files = await findYaml(contentRoot)
  if (!files.length) throw Error('没有找到场景配置')
  const scenes: Scene[] = []
  for (const file of files) {
    const scene = sceneSchema.parse(parse(await readFile(file, 'utf8')))
    const source = path.relative(root, file)
    if (scene.ap && !knownActionPoints.has(scene.ap)) throw Error(`${source}: 未定义行动点 ${scene.ap}`)
    if (scene.ap && (scene.type !== 'choice' || scene.select > dictionary.action_points[scene.ap as keyof typeof dictionary.action_points].initial)) {
      throw Error(`${source}: 行动点不足以完成当前选择`)
    }
    validateEffects(scene.enter, source)
    for (const variant of scene.bodyVariants) {
      validateCondition(variant.when, source)
      variant.body = await readMarkdown(path.dirname(file), variant.body)
    }
    for (const addition of scene.additions) {
      validateCondition(addition.when, source)
      addition.body = await readMarkdown(path.dirname(file), addition.body)
    }
    for (const route of scene.routes) validateCondition(route.when, source)
    const choiceIds = new Set<string>()
    for (const choice of scene.choices) {
      if (choiceIds.has(choice.id)) throw Error(`${source}: 选项 ID 重复 ${choice.id}`)
      choiceIds.add(choice.id)
      validateCondition(choice.condition, source)
      validateEffects(choice.effects, source)
      for (const variant of choice.outcomeVariants) {
        validateCondition(variant.when, source)
        variant.body = await readMarkdown(path.dirname(file), variant.body)
      }
      choice.outcome = await readMarkdown(path.dirname(file), choice.outcome)
    }
    scene.body = await readMarkdown(path.dirname(file), scene.body)
    scenes.push(scene)
  }

  const byId = new Map<string, Scene>()
  for (const scene of scenes) {
    if (byId.has(scene.id)) throw Error(`场景 ID 重复: ${scene.id}`)
    byId.set(scene.id, scene)
  }
  function checkChoiceReferences(condition: Condition | undefined, owner: string): void {
    if (!condition) return
    if ('choice' in condition) {
      const target = byId.get(condition.choice.scene)
      if (!target?.choices.some((choice) => choice.id === condition.choice.id)) {
        throw Error(`${owner}: 找不到引用的选择 ${condition.choice.scene} / ${condition.choice.id}`)
      }
    }
    if ('all' in condition) condition.all.forEach((child) => checkChoiceReferences(child, owner))
    if ('any' in condition) condition.any.forEach((child) => checkChoiceReferences(child, owner))
    if ('not' in condition) checkChoiceReferences(condition.not, owner)
  }
  for (const scene of scenes) {
    for (const next of [scene.next, ...scene.routes.map((route) => route.next), ...scene.choices.map((choice) => choice.next)].filter((id): id is string => Boolean(id))) {
      if (!byId.has(next)) throw Error(`${scene.id}: 找不到后续场景 ${next}`)
    }
    const conditions: (Condition | undefined)[] = [
      ...scene.routes.map((route) => route.when),
      ...scene.bodyVariants.map((variant) => variant.when),
      ...scene.additions.map((addition) => addition.when),
      ...scene.enter.map((effect) => 'when' in effect ? effect.when : undefined),
    ]
    for (const choice of scene.choices) {
      conditions.push(choice.condition, ...choice.outcomeVariants.map((variant) => variant.when))
      conditions.push(...choice.effects.map((effect) => 'when' in effect ? effect.when : undefined))
    }
    conditions.forEach((condition) => checkChoiceReferences(condition, scene.id))
  }

  const first = 'v01-s00a'
  const reachable = new Set<string>()
  function visit(id: string) {
    if (reachable.has(id)) return
    reachable.add(id)
    const scene = byId.get(id)
    if (!scene) throw Error(`找不到起点 ${id}`)
    if (scene.next) visit(scene.next)
    scene.routes.forEach((route) => visit(route.next))
    scene.choices.forEach((choice) => { if (choice.next) visit(choice.next) })
  }
  visit(first)
  visit('v04-slice-end')
  const orphaned = scenes.filter((scene) => !reachable.has(scene.id))
  if (orphaned.length) throw Error(`场景无法从入口到达: ${orphaned.map((scene) => scene.id).join(', ')}`)

  const output = path.join(root, 'src', 'generated')
  await mkdir(output, { recursive: true })
  await writeFile(path.join(output, 'story.json'), JSON.stringify(scenes, null, 2) + '\n')
  console.log(`剧情检查通过，共 ${scenes.length} 个场景。`)
}

main().catch((error: unknown) => {
  console.error(error)
  process.exitCode = 1
})
