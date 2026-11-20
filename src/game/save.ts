import { z } from 'zod'
import { applyAction, available, currentScene, startGame, type GameAction, type GameState, type Story } from './engine'

const actionSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('choose'), choices: z.array(z.string()).min(1) }).strict(),
  z.object({ type: z.literal('continue') }).strict(),
])

const saveSchema = z.object({
  format: z.literal(1),
  rules: z.enum(['slice-1', 'full-1', 'full-2']),
  start: z.enum(['v04-s07', 'v01-s00a']),
  actions: z.array(actionSchema).max(1000),
  draft: z.array(z.string()).max(20),
}).strict()

export type Save = z.infer<typeof saveSchema>
export const SAVE_KEY = 'langchao-yu-xingcheng.save'

export function newSave(): Save {
  return { format: 1, rules: 'full-2', start: 'v01-s00a', actions: [], draft: [] }
}

export function storyForSave(story: Story, save: Save): Story {
  if (save.rules !== 'slice-1') return story
  const replayStory = new Map(story)
  const meeting = replayStory.get('v04-s08')
  if (meeting) replayStory.set(meeting.id, { ...meeting, next: 'v04-slice-end' })
  return replayStory
}

export function replay(story: Story, raw: unknown): { save: Save; state: GameState } {
  const save = saveSchema.parse(raw)
  if ((save.rules === 'slice-1') !== (save.start === 'v04-s07')) throw new Error('存档版本与入口不匹配')
  const replayStory = storyForSave(story, save)
  let state = startGame(replayStory, save.start)
  for (const action of save.actions) {
    // Older full-game saves passed through the briefing without making a choice.
    if (save.rules === 'full-1' && state.sceneId === 'v04-brief' && state.phase === 'scene' && action.type === 'continue') {
      const legacyStory = new Map(replayStory)
      const briefing = currentScene(replayStory, state)
      legacyStory.set(briefing.id, { ...briefing, type: 'passage', choices: [] })
      state = applyAction(legacyStory, state, action)
    } else {
      state = applyAction(replayStory, state, action as GameAction)
    }
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
