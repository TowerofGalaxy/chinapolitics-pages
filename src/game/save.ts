import { z } from 'zod'
import { applyAction, available, currentScene, startGame, type GameAction, type GameState, type Story } from './engine'
import { sceneSchema } from '../story/schema'
import legacyRules from './legacy-full-2.json'
import previousRules from './legacy-full-3.json'

const actionSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('choose'), choices: z.array(z.string()).min(1) }).strict(),
  z.object({ type: z.literal('continue') }).strict(),
  z.object({ type: z.literal('duel'), round: z.number().int().nonnegative(), tactic: z.string().min(1) }).strict(),
])

const saveSchema = z.object({
  format: z.literal(1),
  rules: z.enum(['slice-1', 'full-1', 'full-2', 'full-3', 'full-4']),
  start: z.enum(['v04-s07', 'v01-s00a']),
  actions: z.array(actionSchema).max(1000),
  draft: z.array(z.string()).max(20),
}).strict()

export type Save = z.infer<typeof saveSchema>
export const SAVE_KEY = 'langchao-yu-xingcheng.save'

export function newSave(): Save {
  return { format: 1, rules: 'full-4', start: 'v01-s00a', actions: [], draft: [] }
}

export function storyForSave(story: Story, save: Save): Story {
  if (save.rules === 'full-4') return story
  const replayStory = new Map(story)
  if (save.rules === 'full-3') {
    const response = replayStory.get('v04-s11')
    if (response) {
      const choices = response.choices.map((choice) => choice.id === 'a'
        ? { ...choice, effects: previousRules['v04-s11'].choiceAEffects }
        : choice)
      replayStory.set(response.id, sceneSchema.parse({ ...response, choices }))
    }
    const gate = replayStory.get('v05-gate18')
    if (gate) replayStory.set(gate.id, sceneSchema.parse({ ...gate, ...previousRules['v05-gate18'] }))
    return replayStory
  }
  // 旧存档继续沿用发布时的结局门槛和效果，避免回放后换线或失去进度。
  for (const [id, snapshot] of Object.entries(legacyRules)) {
    const scene = replayStory.get(id)
    if (!scene) continue
    const choices = 'choiceAEffects' in snapshot
      ? scene.choices.map((choice) => choice.id === 'a' ? { ...choice, effects: snapshot.choiceAEffects } : choice)
      : scene.choices
    replayStory.set(id, sceneSchema.parse({ ...scene, enter: snapshot.enter, routes: snapshot.routes, choices }))
  }
  const transition = replayStory.get('v04-transition')
  if (transition) {
    replayStory.set(transition.id, {
      ...transition,
      enter: transition.enter.map((effect) => effect.type === 'stage-two' ? { type: 'stage-two-legacy' as const } : effect),
    })
  }
  if (save.rules === 'slice-1') {
    const meeting = replayStory.get('v04-s08')
    if (meeting) replayStory.set(meeting.id, { ...meeting, next: 'v04-slice-end' })
  }
  return replayStory
}

function applySavedAction(story: Story, save: Save, state: GameState, action: GameAction): GameState {
  // Older full-game saves passed through the briefing without making a choice.
  if (save.rules === 'full-1' && state.sceneId === 'v04-brief' && state.phase === 'scene' && action.type === 'continue') {
    const legacyStory = new Map(story)
    const briefing = currentScene(story, state)
    legacyStory.set(briefing.id, { ...briefing, type: 'passage', choices: [] })
    return applyAction(legacyStory, state, action)
  }
  return applyAction(story, state, action)
}

export function replay(story: Story, raw: unknown): { save: Save; state: GameState } {
  const save = saveSchema.parse(raw)
  if ((save.rules === 'slice-1') !== (save.start === 'v04-s07')) throw new Error('存档版本与入口不匹配')
  const replayStory = storyForSave(story, save)
  let state = startGame(replayStory, save.start)
  for (const action of save.actions) {
    state = applySavedAction(replayStory, save, state, action as GameAction)
  }
  const scene = currentScene(replayStory, state)
  if (save.draft.length && (state.phase !== 'scene' || scene.type !== 'choice')) throw new Error('存档中的选择不适用于当前场景')
  const choices = new Map(scene.choices.map((choice) => [choice.id, choice]))
  if (new Set(save.draft).size !== save.draft.length || save.draft.length > scene.select || save.draft.some((id) => {
    const choice = choices.get(id)
    return !choice || !available(state, choice)
  })) {
    throw new Error('存档中的选择无效')
  }
  return { save, state }
}

const chapterStarts: Record<string, string> = {
  'v01-s00a': '第一卷 · 书斋与激流',
  'v02-s02a': '第二卷 · 前门东大街的风',
  'v03-s04a': '第三卷 · 东华门沉潜与外宣破冰',
  'v04-s07': '第四卷 · 主政江淮与两会大考',
  'v05-start': '第五卷 · 大木仓胡同的算局',
  'v06-s17a': '第六卷 · 晚晴长风与历史行程',
}

export function checkpoints(story: Story, save: Save): { title: string; actionCount: number }[] {
  const replayStory = storyForSave(story, save)
  let state = startGame(replayStory, save.start)
  const result: { title: string; actionCount: number }[] = []
  function record(actionCount: number) {
    const title = chapterStarts[state.sceneId]
    if (title && state.phase === 'scene' && actionCount < save.actions.length) result.push({ title, actionCount })
  }
  record(0)
  for (const [index, action] of save.actions.entries()) {
    state = applySavedAction(replayStory, save, state, action)
    record(index + 1)
  }
  return result
}
