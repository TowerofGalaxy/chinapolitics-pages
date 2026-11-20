import dictionary from '../../variables.json'
import { DUELS } from '../ui/duels'
import type { Choice, Condition, Effect, Scene } from '../story/schema'

export type GameAction =
  | { type: 'choose'; choices: string[] }
  | { type: 'continue' }
  | { type: 'duel'; round: number; tactic: string }

export interface DuelPick {
  id: string
  changes: Record<string, number>
}

export interface GameState {
  sceneId: string
  phase: 'scene' | 'result' | 'ending'
  stats: Record<string, number>
  actionPoints: Record<string, number>
  tags: string[]
  history: Record<string, string[]>
  duelPicks: Record<string, DuelPick[]>
  result?: { choices: string[]; texts: string[]; changes: Record<string, number>; next: string }
  entryChanges: Record<string, number>
}

export type Story = Map<string, Scene>

export function createStory(scenes: Scene[]): Story {
  return new Map(scenes.map((scene) => [scene.id, scene]))
}

export function currentScene(story: Story, state: GameState): Scene {
  const scene = story.get(state.sceneId)
  if (!scene) throw new Error(`找不到场景 ${state.sceneId}`)
  return scene
}

export function meetsCondition(state: GameState, condition?: Condition): boolean {
  if (!condition) return true
  if ('tag' in condition) return state.tags.includes(condition.tag)
  if ('all' in condition) return condition.all.every((child) => meetsCondition(state, child))
  if ('any' in condition) return condition.any.some((child) => meetsCondition(state, child))
  if ('not' in condition) return !meetsCondition(state, condition.not)
  if ('choice' in condition) return state.history[condition.choice.scene]?.includes(condition.choice.id) ?? false
  const actual = state.stats[condition.stat]
  if (actual === undefined) throw new Error(`找不到属性 ${condition.stat}`)
  switch (condition.op) {
    case 'lt': return actual < condition.value
    case 'lte': return actual <= condition.value
    case 'eq': return actual === condition.value
    case 'gte': return actual >= condition.value
    case 'gt': return actual > condition.value
  }
}

function copyState(state: GameState): GameState {
  return {
    ...state,
    stats: { ...state.stats },
    actionPoints: { ...state.actionPoints },
    tags: [...state.tags],
    history: Object.fromEntries(Object.entries(state.history).map(([id, choices]) => [id, [...choices]])),
    duelPicks: Object.fromEntries(Object.entries(state.duelPicks).map(([id, picks]) => [id, picks.map((pick) => ({ ...pick, changes: { ...pick.changes } }))])),
    result: state.result && {
      ...state.result,
      choices: [...state.result.choices],
      texts: [...state.result.texts],
      changes: { ...state.result.changes },
    },
    entryChanges: { ...state.entryChanges },
  }
}

function applyEffects(state: GameState, effects: Effect[]): Record<string, number> {
  const before = copyState(state)
  const deltas: Record<string, { positive: number; negative: number }> = {}
  for (const effect of effects) {
    if (effect.type === 'stage-two' || effect.type === 'stage-two-legacy') {
      const limit = effect.type === 'stage-two' ? 6 : 4
      const centralInjection = Math.max(-limit, Math.min(limit, Math.floor((before.stats.cadre_trust - 50) / 4)))
      const reformInjection = Math.max(-limit, Math.min(limit, Math.floor((before.stats.reform_acumen - 50) / 4)))
      const centralPenalty = (before.tags.includes('边缘平调序列') ? 3 : 0) + (before.tags.includes('报批越界通报') ? 2 : 0)
      state.stats.central_trust = Math.max(0, Math.min(100, 55 + centralInjection - centralPenalty))
      state.stats.reform_drive = Math.max(0, Math.min(100, 50 + reformInjection))
      continue
    }
    if (!meetsCondition(before, effect.when)) continue
    if (effect.type === 'change') {
      const total = deltas[effect.stat] ?? { positive: 0, negative: 0 }
      if (effect.amount >= 0) total.positive += effect.amount
      else total.negative += effect.amount
      deltas[effect.stat] = total
    } else if (effect.type === 'add-tag') {
      if (!state.tags.includes(effect.tag)) state.tags.push(effect.tag)
    } else {
      state.tags = state.tags.filter((tag) => tag !== effect.tag)
    }
  }
  const changes: Record<string, number> = {}
  for (const [stat, delta] of Object.entries(deltas)) {
    if (state.stats[stat] === undefined) throw new Error(`找不到属性 ${stat}`)
    const positive = stat === 'reform_drive' && before.stats.local_cohesion <= 35
      ? Math.floor(delta.positive / 2)
      : delta.positive
    const value = Math.max(0, Math.min(100, before.stats[stat] + positive + delta.negative))
    state.stats[stat] = value
    if (value !== before.stats[stat]) changes[stat] = value - before.stats[stat]
  }
  for (const [stat, value] of Object.entries(state.stats)) {
    if (value !== before.stats[stat]) changes[stat] = value - before.stats[stat]
  }
  return changes
}

function enterScene(story: Story, state: GameState, sceneId: string): GameState {
  const next = copyState(state)
  next.sceneId = sceneId
  const scene = currentScene(story, next)
  next.phase = scene.type === 'ending' ? 'ending' : 'scene'
  next.result = undefined
  next.entryChanges = applyEffects(next, scene.enter)
  return next
}

export function startGame(story: Story, sceneId = 'v01-s00a'): GameState {
  const stage1 = Object.fromEntries(Object.entries(dictionary.stage_1_variables).map(([key, value]) => [key, value.baseline]))
  const stage2 = Object.fromEntries(Object.entries(dictionary.stage_2_variables).map(([key, value]) => [key, value.baseline]))
  const actionPoints = Object.fromEntries(Object.entries(dictionary.action_points).map(([key, value]) => [key, value.initial]))
  return enterScene(story, {
    sceneId,
    phase: 'scene',
    stats: { ...stage1, ...stage2 },
    actionPoints,
    tags: sceneId.startsWith('v01-') ? ['纯粹知识分子底色'] : [],
    history: {},
    duelPicks: {},
    entryChanges: {},
  }, sceneId)
}

export function available(state: GameState, choice: Choice): boolean {
  return meetsCondition(state, choice.condition)
}

export function applyAction(story: Story, previous: GameState, action: GameAction): GameState {
  const scene = currentScene(story, previous)
  if (action.type === 'duel') {
    if (previous.phase !== 'scene') throw new Error('当前无法交锋')
    const duel = DUELS[scene.id]
    const picks = previous.duelPicks[scene.id] ?? []
    const round = duel?.rounds[action.round]
    const tactic = round?.tactics?.find((item) => item.id === action.tactic)
    if (!Number.isInteger(action.round) || action.round !== picks.length || !tactic) throw new Error('交锋选择无效')
    const next = copyState(previous)
    const changes = tactic.statDelta
      ? applyEffects(next, [{ type: 'change', stat: tactic.statDelta.stat, amount: tactic.statDelta.amount }])
      : {}
    next.duelPicks[scene.id] = [...picks, { id: tactic.id, changes }]
    return next
  }
  if (action.type === 'continue') {
    const target = previous.phase === 'result'
      ? previous.result?.next
      : scene.type === 'passage'
        ? scene.routes.find((route) => meetsCondition(previous, route.when))?.next ?? scene.next
        : undefined
    if (!target) throw new Error('当前无法继续')
    return enterScene(story, previous, target)
  }
  if (previous.phase !== 'scene' || scene.type !== 'choice') throw new Error('当前无法选择')
  if (action.choices.length !== scene.select || new Set(action.choices).size !== action.choices.length) {
    throw new Error('选择数量不符合要求')
  }
  const selected = scene.choices.filter((choice) => action.choices.includes(choice.id))
  if (selected.length !== action.choices.length || selected.some((choice) => !available(previous, choice))) {
    throw new Error('选项无效或尚未解锁')
  }
  if (scene.ap && (previous.actionPoints[scene.ap] ?? 0) < selected.length) throw new Error('行动点不足')
  const nextId = selected[0]?.next ?? scene.next
  if (!nextId || !story.has(nextId)) throw new Error('缺少后续场景')
  const next = copyState(previous)
  const initialStats = { ...next.stats }
  const texts = selected.map((choice) => choice.outcomeVariants.find((variant) => meetsCondition(previous, variant.when))?.body ?? choice.outcome)
  for (const choice of selected) {
    applyEffects(next, choice.effects)
    if (scene.ap) next.actionPoints[scene.ap]--
  }
  next.history[scene.id] = selected.map((choice) => choice.id)
  const changes: Record<string, number> = {}
  for (const [name, value] of Object.entries(next.stats)) {
    if (value !== initialStats[name]) changes[name] = value - initialStats[name]
  }
  next.phase = 'result'
  next.result = { choices: selected.map((choice) => choice.id), texts, changes, next: nextId }
  next.entryChanges = {}
  return next
}
