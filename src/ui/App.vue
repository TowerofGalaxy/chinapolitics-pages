<script setup lang="ts">
import { computed, ref } from 'vue'
import DOMPurify from 'dompurify'
import { marked, Renderer } from 'marked'
import compiled from '../generated/story.json'
import { sceneSchema } from '../story/schema'
import { applyAction, available, createStory, currentScene, meetsCondition, startGame, type GameAction, type GameState } from '../game/engine'
import { checkpoints, newSave, replay, SAVE_KEY, storyForSave, type Save } from '../game/save'
import { getActiveEchoes } from './tagsMeta'
import { DUELS, type DuelTactic } from './duels'

const story = createStory(sceneSchema.array().parse(compiled))
const renderer = new Renderer()
renderer.html = () => ''

function markdown(text: string): string {
  return DOMPurify.sanitize(marked.parse(text, { async: false, renderer }), {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'blockquote', 'ul', 'ol', 'li', 'h2', 'h3'],
    ALLOWED_ATTR: [],
  })
}

let initialSave: Save = newSave()
let initialState = startGame(story)
let initialNotice = ''
let lastStoredValue: string | null = null
try {
  const existing = window.localStorage.getItem(SAVE_KEY)
  lastStoredValue = existing
  if (existing) {
    const restored = replay(story, JSON.parse(existing))
    initialSave = restored.save
    initialState = restored.state
  }
} catch {
  initialNotice = '存档暂时无法读取，当前从头开始。'
}

const save = ref(initialSave)
const state = ref(initialState)
const draft = ref([...initialSave.draft])
const notice = ref(initialNotice)
const reachedChapters = computed(() => checkpoints(story, save.value))
const scene = computed(() => currentScene(story, state.value))
const sceneBody = computed(() => scene.value.bodyVariants.find((variant) => meetsCondition(state.value, variant.when))?.body ?? scene.value.body)
const visibleChoices = computed(() => scene.value.choices.filter((choice) =>
  available(state.value, choice) || choice.unavailable === 'locked',
))
const volumeTitles = ['书斋与激流', '前门东大街的风', '东华门沉潜与外宣破冰', '主政江淮与两会大考', '大木仓胡同的算局', '晚晴长风与历史行程']
const volumeNumbers = ['一', '二', '三', '四', '五', '六']
const clueNames = ['退稿油印刊物', '导师推荐信底稿', '第三梯队座谈纪要', '温州调研原件', '预审口径单', '文官制度底稿', '外宣案例剪报', '公交录像带', '城投挪用线索', '老同志口风', '监督局带病档案', '基层测评原始样表', '使节团提问清单', '群团基层调研底表', '外事礼宾密电']
const clues = computed(() => state.value.tags.filter((tag) => clueNames.includes(tag)))
const statLabels: Record<string, string> = {
  cadre_trust: '组织信任度',
  reform_acumen: '改革锐度值',
  central_trust: '中央信任度',
  local_cohesion: '地方向心力',
  fiscal_stability: '财政稳态值',
  reform_drive: '改革开拓度',
}
const stats = computed(() => Object.entries(statLabels).filter(([id]) =>
  scene.value.volume < 4 ? ['cadre_trust', 'reform_acumen'].includes(id) : !['cadre_trust', 'reform_acumen'].includes(id),
).map(([id, label]) => ({
  id,
  label: id === 'local_cohesion' && scene.value.volume >= 5 ? '系统协同度' : label,
  value: state.value.stats[id],
})))

// 历史回响与跨卷 Flag 检测
const echoes = computed(() => getActiveEchoes(scene.value, state.value))

// 案头机要卷宗与公文场景判定
const isDocumentScene = computed(() => [
  'v04-brief', 'v05-s15', 'v06-s18r1', 'v06-s18r2',
  'v01-s00a', 'v02-s02a', 'v03-s04a', 'v04-s07', 'v05-start', 'v06-s17a',
].includes(scene.value.id))

function getStampText(sceneId: string): string {
  if (sceneId === 'v04-brief') return '【重点质询】'
  if (scene.value.volume >= 5) return '【呈批同意】'
  if (scene.value.volume === 4) return '【批示落实】'
  return '【圈阅】'
}

// 三轮交锋实机对决状态
const currentDuel = computed(() => DUELS[scene.value.id])
const duelStep = ref<Record<string, number>>({})
const duelExpanded = ref<Record<string, boolean>>({})

function getDuelRound(sceneId: string): number {
  return duelStep.value[sceneId] ?? state.value.duelPicks[sceneId]?.length ?? 0
}

function getDuelPick(sceneId: string, roundIdx: number): string | undefined {
  return state.value.duelPicks[sceneId]?.[roundIdx]?.id
}

function getDuelChanges(sceneId: string, roundIdx: number): Record<string, number> {
  return state.value.duelPicks[sceneId]?.[roundIdx]?.changes ?? {}
}

function chooseTactic(sceneId: string, roundIdx: number, tactic: DuelTactic) {
  try {
    if (scene.value.id !== sceneId) return
    const action: GameAction = { type: 'duel', round: roundIdx, tactic: tactic.id }
    duelStep.value[sceneId] = getDuelRound(sceneId)
    state.value = applyAction(storyForSave(story, save.value), state.value, action)
    save.value = { ...save.value, actions: [...save.value.actions, action] }
    persist()
  } catch {
    notice.value = '当前交锋无法选择，请刷新后重试。'
  }
}

function nextDuelRound(sceneId: string) {
  const current = getDuelRound(sceneId)
  duelStep.value[sceneId] = current + 1
}

function toggleDuelExpand(sceneId: string) {
  duelExpanded.value[sceneId] = !duelExpanded.value[sceneId]
}

function displayChoiceLabel(label: string): string {
  return label.replace(/[（\(](?:大义灭亲|私心护短)[）\)]/g, '').trim()
}

function changesText(changes: Record<string, number>): string {
  return Object.entries(changes)
    .map(([id, amount]) => `${id === 'local_cohesion' && scene.value.volume >= 5 ? '系统协同度' : statLabels[id] ?? id} ${amount > 0 ? '+' : '−'}${Math.abs(amount)}`)
    .join('　')
}

// 已读记录与存档分开保存，选择、不同正文和不同结果都不会被自动跳过。
const READ_KEY = 'langchao-yu-xingcheng.read'
let initialRead: string[] = []
try {
  const parsed: unknown = JSON.parse(window.localStorage.getItem(READ_KEY) ?? '[]')
  if (Array.isArray(parsed)) initialRead = parsed.filter((item): item is string => typeof item === 'string')
} catch { /* 读取记录损坏时只影响快进，不影响存档。 */ }
const readKeys = ref(new Set(initialRead))

function readingKey(current: GameState): string | undefined {
  const currentSceneData = currentScene(story, current)
  if (current.phase === 'result' && current.result) {
    return JSON.stringify([current.sceneId, 'result', current.result.choices, current.result.texts, current.result.changes])
  }
  if (current.phase === 'scene' && currentSceneData.type === 'passage') {
    const body = currentSceneData.bodyVariants.find((variant) => meetsCondition(current, variant.when))?.body ?? currentSceneData.body
    const additions = currentSceneData.additions.filter((item) => meetsCondition(current, item.when)).map((item) => item.body)
    return JSON.stringify([current.sceneId, 'passage', body, additions, current.entryChanges])
  }
  return undefined
}

function rememberRead(key: string | undefined) {
  if (!key || readKeys.value.has(key)) return
  readKeys.value.add(key)
  try { window.localStorage.setItem(READ_KEY, JSON.stringify([...readKeys.value])) } catch { /* 不阻碍继续游戏。 */ }
}

const canSkipRead = computed(() => {
  const key = readingKey(state.value)
  return !!key && readKeys.value.has(key)
})

function persist() {
  try {
    if (window.localStorage.getItem(SAVE_KEY) !== lastStoredValue) {
      notice.value = '另一个页面更新了存档，请刷新页面继续。'
      return
    }
    const serialized = JSON.stringify(save.value)
    window.localStorage.setItem(SAVE_KEY, serialized)
    lastStoredValue = serialized
    notice.value = ''
  } catch {
    notice.value = '无法自动保存，刷新页面后进度可能丢失。'
  }
}

window.addEventListener('storage', (event) => {
  if ((event.key === SAVE_KEY || event.key === null) && event.newValue !== lastStoredValue) {
    notice.value = '另一个页面更新了存档，请刷新页面继续。'
  }
})

function setDraft(id: string, checked: boolean) {
  const choice = scene.value.choices.find((item) => item.id === id)
  if (!choice || !available(state.value, choice)) return
  if (scene.value.select === 1) draft.value = checked ? [id] : []
  else if (checked && draft.value.length < scene.value.select) draft.value = [...draft.value, id]
  else if (!checked) draft.value = draft.value.filter((item) => item !== id)
  save.value = { ...save.value, draft: [...draft.value] }
  persist()
}

function dispatch(action: GameAction) {
  try {
    const read = action.type === 'continue' ? readingKey(state.value) : undefined
    state.value = applyAction(storyForSave(story, save.value), state.value, action)
    save.value = { ...save.value, actions: [...save.value.actions, action], draft: [] }
    draft.value = []
    rememberRead(read)
    persist()
    window.scrollTo({ top: 0, behavior: 'instant' })
  } catch {
    notice.value = '当前选择无法提交，请重新选择。'
  }
}

function skipRead() {
  try {
    const activeStory = storyForSave(story, save.value)
    let next = state.value
    const actions: GameAction[] = []
    for (let count = 0; count < 100; count++) {
      const key = readingKey(next)
      if (!key || !readKeys.value.has(key)) break
      const action: GameAction = { type: 'continue' }
      next = applyAction(activeStory, next, action)
      actions.push(action)
    }
    if (!actions.length) return
    state.value = next
    save.value = { ...save.value, actions: [...save.value.actions, ...actions], draft: [] }
    draft.value = []
    persist()
    window.scrollTo({ top: 0, behavior: 'instant' })
  } catch {
    notice.value = '暂时无法快进，请继续阅读。'
  }
}

function rewindTo(actionCount: number) {
  if (!window.confirm('回到这一卷会覆盖当前进度，确定吗？')) return
  try {
    const restored = replay(story, { ...save.value, actions: save.value.actions.slice(0, actionCount), draft: [] })
    save.value = restored.save
    state.value = restored.state
    draft.value = []
    duelStep.value = {}
    duelExpanded.value = {}
    persist()
    window.scrollTo({ top: 0, behavior: 'instant' })
  } catch {
    notice.value = '暂时无法回到该章节，当前进度没有改变。'
  }
}

function restart() {
  if (!window.confirm('重新开始会清除当前进度，确定吗？')) return
  state.value = startGame(story)
  save.value = newSave()
  draft.value = []
  duelStep.value = {}
  duelExpanded.value = {}
  persist()
  window.scrollTo({ top: 0, behavior: 'instant' })
}
</script>

<template>
  <div class="reading-page">
    <header class="running-head">
      <div class="book">
        <strong>浪潮与行程</strong>
        <span>第{{ volumeNumbers[scene.volume - 1] }}卷 · {{ volumeTitles[scene.volume - 1] }}</span>
      </div>
      <details class="dossier">
        <summary>局势<span v-if="clues.length"> · {{ clues.length }} 条线索</span></summary>
        <div class="dossier-sheet">
          <dl>
            <div v-for="stat in stats" :key="stat.id">
              <dt>{{ stat.label }}</dt>
              <dd>{{ stat.value }}</dd>
            </div>
          </dl>
          <p>{{ clues.length ? clues.join('、') : '暂无线索' }}</p>
        </div>
      </details>
    </header>

    <main>
      <p v-if="notice" class="notice" role="status">{{ notice }}</p>
      <p v-if="save.rules !== 'full-4'" class="notice">当前存档沿用原版数值规则；重新开始后采用新的平衡设置。</p>

      <!-- 历史回响（跨卷 Flag 高感知印章提示条） -->
      <aside v-if="echoes.length && state.phase !== 'result'" class="echo-banner" aria-label="历史回响">
        <div v-for="echo in echoes" :key="echo.tag" class="echo-stamp">
          <span class="echo-seal">「 印 」</span>
          <span class="echo-year">{{ echo.year }} 年</span>
          <span class="echo-name">【{{ echo.tag }}】</span>
          <span class="echo-tag-label">{{ echo.label }}</span>
        </div>
      </aside>

      <!-- 案头机要公文红头标识 -->
      <div v-if="isDocumentScene && state.phase !== 'result'" class="doc-classified-banner">
        ★ 内部机密 · 案头呈阅卷宗 ★
      </div>
      <div v-if="isDocumentScene && state.phase !== 'result'" class="red-header-rule"></div>

      <article class="scene" aria-labelledby="scene-title">
        <p v-if="scene.time || scene.location" class="dateline">
          {{ [scene.time, scene.location].filter(Boolean).join(' · ') }}
        </p>
        <h1 id="scene-title">{{ scene.title }}</h1>

        <!-- 三轮交锋实机对决模块（场景 08、12、16 专属互动体验） -->
        <template v-if="currentDuel && state.phase !== 'result' && !duelExpanded[scene.id]">
          <div class="duel-container">
            <div class="duel-header">
              <div class="duel-opponent-box">
                <span class="duel-opponent">{{ currentDuel.opponent }}</span>
                <span class="duel-opponent-title">{{ currentDuel.opponentTitle }}</span>
              </div>
              <span class="duel-location">{{ currentDuel.location }}</span>
            </div>
            <p class="duel-intro">{{ currentDuel.intro }}</p>

            <div
              v-for="(round, rIdx) in currentDuel.rounds.slice(0, getDuelRound(scene.id) + 1)"
              :key="round.title"
              class="duel-round-block"
            >
              <div class="duel-round-title">{{ round.title }}</div>
              <div class="duel-challenge">{{ round.challenge }}</div>

              <!-- 尚未接招时显示两个话术按钮 -->
              <template v-if="round.tactics && !getDuelPick(scene.id, rIdx)">
                <div class="duel-tactics-prompt">我的接招话术（点击选择切入角度）：</div>
                <div class="duel-tactics-grid">
                  <button
                    v-for="tactic in round.tactics"
                    :key="tactic.id"
                    type="button"
                    class="tactic-btn"
                    @click="chooseTactic(scene.id, rIdx, tactic)"
                  >
                    <span class="tactic-label">{{ tactic.label }}</span>
                    <span class="tactic-preview">{{ tactic.speech }}</span>
                  </button>
                </div>
              </template>

              <!-- 已接招显示说话与对方微表情 -->
              <div v-else-if="round.tactics && getDuelPick(scene.id, rIdx)" class="duel-response-block">
                <div class="duel-response-speech">
                  <strong>我</strong>：{{ round.tactics.find(t => t.id === getDuelPick(scene.id, rIdx))?.speech }}
                </div>
                <div class="duel-reaction">
                  {{ round.tactics.find(t => t.id === getDuelPick(scene.id, rIdx))?.reaction }}
                </div>
                <span
                  v-if="Object.keys(getDuelChanges(scene.id, rIdx)).length"
                  class="duel-delta-badge"
                >
                  {{ changesText(getDuelChanges(scene.id, rIdx)) }}
                </span>
              </div>

              <!-- 进入下一轮按钮 -->
              <button
                v-if="round.tactics && getDuelPick(scene.id, rIdx) && getDuelRound(scene.id) === rIdx && rIdx < currentDuel.rounds.length - 1"
                type="button"
                class="duel-next-btn"
                @click="nextDuelRound(scene.id)"
              >
                进入第 {{ rIdx + 2 }} 轮交锋 →
              </button>

              <!-- 第 3 轮转场定局 -->
              <div v-if="round.climax" class="duel-climax-block">
                {{ round.climax }}
              </div>
            </div>

            <button type="button" class="duel-toggle-link" @click="toggleDuelExpand(scene.id)">
              展开三轮交锋全文
            </button>
          </div>
        </template>

        <!-- 普通场景正文或交锋展开全文 -->
        <div v-else-if="state.phase !== 'result'" class="prose" v-html="markdown(sceneBody)"></div>

        <button
          v-if="currentDuel && state.phase !== 'result' && duelExpanded[scene.id]"
          type="button"
          class="duel-toggle-link"
          style="margin-bottom: 14px;"
          @click="toggleDuelExpand(scene.id)"
        >
          返回分轮对决接招模式
        </button>

        <template v-if="state.phase !== 'result'">
          <div v-for="addition in scene.additions.filter((item) => meetsCondition(state, item.when))" :key="addition.body" class="prose addition" v-html="markdown(addition.body)"></div>
        </template>
        <p v-if="Object.keys(state.entryChanges).length" class="changes">{{ changesText(state.entryChanges) }}</p>
        <div v-if="state.phase === 'result'" class="outcomes" aria-live="polite">
          <div v-for="(text, index) in state.result?.texts" :key="index" class="prose outcome" v-html="markdown(text)"></div>
          <p v-if="state.result && Object.keys(state.result.changes).length" class="changes">{{ changesText(state.result.changes) }}</p>
        </div>
        <p v-if="state.phase === 'ending'" class="ending-label">故事结束</p>
      </article>

      <section v-if="state.phase === 'scene' && scene.type === 'choice'" class="decision" aria-labelledby="choice-title">
        <div class="decision-head">
          <h2 id="choice-title">{{ scene.prompt }}</h2>
          <span v-if="scene.select > 1" aria-live="polite">已选 {{ draft.length }} / {{ scene.select }}</span>
        </div>
        <label v-for="choice in visibleChoices" :key="choice.id" class="choice">
          <input
            :type="scene.select > 1 ? 'checkbox' : 'radio'"
            name="choice"
            :value="choice.id"
            :checked="draft.includes(choice.id)"
            :disabled="!available(state, choice) || (scene.select > 1 && draft.length >= scene.select && !draft.includes(choice.id))"
            @change="setDraft(choice.id, ($event.target as HTMLInputElement).checked)"
          >
          <span class="choice-content">
            <span class="choice-title">{{ displayChoiceLabel(choice.label) }}</span>
            <small v-if="choice.hint" class="choice-hint">{{ choice.hint }}</small>
            <small v-if="!available(state, choice)" class="choice-reason">{{ choice.reason }}</small>
          </span>
          <span v-if="draft.includes(choice.id)" class="stamp-mark">{{ getStampText(scene.id) }}</span>
        </label>
        <button type="button" :disabled="draft.length !== scene.select" @click="dispatch({ type: 'choose', choices: draft })">确认决定</button>
      </section>
      <div v-else-if="state.phase === 'result' || (state.phase === 'scene' && scene.type === 'passage')" class="continue">
        <button type="button" @click="dispatch({ type: 'continue' })">继续</button>
        <button v-if="canSkipRead" type="button" class="skip-read" @click="skipRead">跳过已读</button>
      </div>
    </main>

    <footer>
      <details v-if="reachedChapters.length" class="chapter-menu">
        <summary>回到已读章节</summary>
        <p>回到章节开头会覆盖当前进度。</p>
        <button v-for="chapter in reachedChapters" :key="chapter.actionCount" type="button" @click="rewindTo(chapter.actionCount)">{{ chapter.title }}</button>
      </details>
      <button class="restart" type="button" @click="restart">重新开始</button>
    </footer>
  </div>
</template>
