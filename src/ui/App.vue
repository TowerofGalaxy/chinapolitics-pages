<script setup lang="ts">
import { computed, ref } from 'vue'
import DOMPurify from 'dompurify'
import { marked, Renderer } from 'marked'
import compiled from '../generated/story.json'
import { sceneSchema } from '../story/schema'
import { applyAction, available, createStory, currentScene, meetsCondition, startGame, type GameAction } from '../game/engine'
import { newSave, replay, SAVE_KEY, storyForSave, type Save } from '../game/save'

const story = createStory(sceneSchema.array().parse(compiled))
const renderer = new Renderer()
renderer.html = () => ''

function markdown(text: string): string {
  return DOMPurify.sanitize(marked.parse(text, { async: false, renderer }), {
    ALLOWED_TAGS: ['p', 'br', 'strong', 'em', 'blockquote', 'ul', 'ol', 'li'],
    ALLOWED_ATTR: [],
  })
}

let initialSave: Save = newSave()
let initialState = startGame(story)
let initialNotice = ''
try {
  const existing = window.localStorage.getItem(SAVE_KEY)
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
  local_cohesion: '省内向心力',
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

function changesText(changes: Record<string, number>): string {
  return Object.entries(changes)
    .map(([id, amount]) => `${id === 'local_cohesion' && scene.value.volume >= 5 ? '系统协同度' : statLabels[id] ?? id} ${amount > 0 ? '+' : '−'}${Math.abs(amount)}`)
    .join('　')
}

function persist() {
  try {
    window.localStorage.setItem(SAVE_KEY, JSON.stringify(save.value))
    notice.value = ''
  } catch {
    notice.value = '无法自动保存，刷新页面后进度可能丢失。'
  }
}

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
    state.value = applyAction(storyForSave(story, save.value), state.value, action)
    save.value = { ...save.value, actions: [...save.value.actions, action], draft: [] }
    draft.value = []
    persist()
    window.scrollTo({ top: 0, behavior: 'instant' })
  } catch {
    notice.value = '当前选择无法提交，请重新选择。'
  }
}

function restart() {
  if (!window.confirm('重新开始会清除当前进度，确定吗？')) return
  state.value = startGame(story)
  save.value = newSave()
  draft.value = []
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
      <article class="scene" aria-labelledby="scene-title">
        <p v-if="scene.time || scene.location" class="dateline">
          {{ [scene.time, scene.location].filter(Boolean).join(' · ') }}
        </p>
        <h1 id="scene-title">{{ scene.title }}</h1>
        <div v-if="state.phase !== 'result'" class="prose" v-html="markdown(sceneBody)"></div>
        <template v-if="state.phase !== 'result'">
          <div v-for="addition in scene.additions.filter((item) => meetsCondition(state, item.when))" :key="addition.body" class="prose addition" v-html="markdown(addition.body)"></div>
        </template>
        <p v-if="Object.keys(state.entryChanges).length" class="changes">{{ changesText(state.entryChanges) }}</p>
        <div v-if="state.phase === 'result'" class="outcomes" aria-live="polite">
          <div v-for="(text, index) in state.result?.texts" :key="index" class="prose outcome" v-html="markdown(text)"></div>
          <p v-if="state.result && Object.keys(state.result.changes).length" class="changes">{{ changesText(state.result.changes) }}</p>
        </div>
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
          <span>{{ choice.label }} <small v-if="!available(state, choice)">{{ choice.reason }}</small></span>
        </label>
        <button type="button" :disabled="draft.length !== scene.select" @click="dispatch({ type: 'choose', choices: draft })">确认决定</button>
      </section>
      <div v-else-if="state.phase === 'result' || (state.phase === 'scene' && scene.type === 'passage')" class="continue">
        <button type="button" @click="dispatch({ type: 'continue' })">继续</button>
      </div>
    </main>

    <footer><button class="restart" type="button" @click="restart">重新开始</button></footer>
  </div>
</template>
