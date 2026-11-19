import { z } from 'zod'

export type Condition =
  | { tag: string }
  | { stat: string; op: 'lt' | 'lte' | 'eq' | 'gte' | 'gt'; value: number }
  | { all: Condition[] }
  | { any: Condition[] }
  | { not: Condition }
  | { choice: { scene: string; id: string } }

export const conditionSchema: z.ZodType<Condition> = z.lazy(() =>
  z.union([
    z.object({ tag: z.string().min(1) }).strict(),
    z.object({
      stat: z.string().min(1),
      op: z.enum(['lt', 'lte', 'eq', 'gte', 'gt']),
      value: z.number().int(),
    }).strict(),
    z.object({ all: z.array(conditionSchema).min(1) }).strict(),
    z.object({ any: z.array(conditionSchema).min(1) }).strict(),
    z.object({ not: conditionSchema }).strict(),
    z.object({ choice: z.object({ scene: z.string(), id: z.string() }).strict() }).strict(),
  ]),
)

const effectSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('change'), stat: z.string(), amount: z.number().int(), when: conditionSchema.optional() }).strict(),
  z.object({ type: z.literal('add-tag'), tag: z.string(), when: conditionSchema.optional() }).strict(),
  z.object({ type: z.literal('remove-tag'), tag: z.string(), when: conditionSchema.optional() }).strict(),
  z.object({ type: z.literal('stage-two') }).strict(),
])

const choiceSchema = z.object({
  id: z.string().min(1),
  label: z.string().min(1),
  hint: z.string().optional(),
  condition: conditionSchema.optional(),
  unavailable: z.enum(['hidden', 'locked']).default('hidden'),
  reason: z.string().optional(),
  outcome: z.string().min(1),
  outcomeVariants: z.array(z.object({ when: conditionSchema, body: z.string().min(1) }).strict()).default([]),
  effects: z.array(effectSchema).default([]),
  next: z.string().optional(),
}).strict()

export const sceneSchema = z.object({
  id: z.string().regex(/^v\d{2}-[a-z0-9-]+$/),
  volume: z.number().int().min(1).max(6),
  source: z.string().min(1),
  title: z.string().min(1),
  time: z.string().optional(),
  location: z.string().optional(),
  body: z.string().min(1),
  bodyVariants: z.array(z.object({ when: conditionSchema, body: z.string().min(1) }).strict()).default([]),
  additions: z.array(z.object({ when: conditionSchema, body: z.string().min(1) }).strict()).default([]),
  type: z.enum(['choice', 'passage', 'ending']),
  prompt: z.string().optional(),
  select: z.number().int().min(1).default(1),
  ap: z.string().optional(),
  enter: z.array(effectSchema).default([]),
  choices: z.array(choiceSchema).default([]),
  routes: z.array(z.object({ when: conditionSchema, next: z.string() }).strict()).default([]),
  next: z.string().optional(),
}).strict().superRefine((scene, context) => {
  if (scene.type === 'choice' && (scene.choices.length < scene.select || !scene.prompt)) {
    context.addIssue({ code: 'custom', message: '选择场景需要提示和足够的选项' })
  }
  if (scene.type !== 'choice' && scene.choices.length) {
    context.addIssue({ code: 'custom', message: '只有选择场景可以包含选项' })
  }
  if (scene.type === 'passage' && !scene.next) {
    context.addIssue({ code: 'custom', message: '阅读场景需要后续场景' })
  }
  if (scene.type === 'ending' && scene.next) {
    context.addIssue({ code: 'custom', message: '结尾不能设置后续场景' })
  }
  if (scene.type !== 'passage' && scene.routes.length) {
    context.addIssue({ code: 'custom', message: '条件分流只能用于阅读场景' })
  }
  if (scene.type === 'choice' && !scene.next && scene.choices.some((choice) => !choice.next)) {
    context.addIssue({ code: 'custom', message: '每个选项都需要后续场景' })
  }
  if (scene.select > 1 && scene.choices.some((choice) => choice.next)) {
    context.addIssue({ code: 'custom', message: '多选场景需要使用共同的后续场景' })
  }
})

export type Scene = z.infer<typeof sceneSchema>
export type Choice = Scene['choices'][number]
export type Effect = Scene['enter'][number]
