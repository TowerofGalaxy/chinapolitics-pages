import { z } from 'zod'
import { applyAction, available, currentScene, startGame, type GameAction, type GameState, type Story } from './engine'

const actionSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('choose'), choices: z.array(z.string()).min(1) }).strict(),
  z.object({ type: z.literal('continue') }).strict(),
])

const saveSchema = z.object({
  format: z.literal(1),
  rules: z.literal('slice-1'),
  start: z.literal('v04-s07'),
  actions: z.array(actionSchema).max(1000),
  draft: z.array(z.string()).max(20),
}).strict()

export type Save = z.infer<typeof saveSchema>
export const SAVE_KEY = 'langchao-yu-xingcheng.save'

export function newSave(): Save {
  return { format: 1, rules: 'slice-1', start: 'v04-s07', actions: [], draft: [] }
}

export function replay(story: Story, raw: unknown): { save: Save; state: GameState } {
  const save = saveSchema.parse(raw)
  let state = startGame(story, save.start)
  for (const action of save.actions) state = applyAction(story, state, action as GameAction)
  const scene = currentScene(story, state)
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
