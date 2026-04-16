<template>
  <div class="chatbot-wrapper">
    <!-- Botón flotante para abrir/cerrar -->
    <button class="chat-toggle" @click="toggleChat" :class="{ open: isOpen }">
      <span v-if="!isOpen">💬</span>
      <span v-else>✕</span>
    </button>

    <!-- Ventana del chat -->
    <Transition name="chat-slide">
      <div v-if="isOpen" class="chat-window">
        <!-- Header -->
        <div class="chat-header">
          <div class="chat-header-info">
            <div class="chat-avatar">🤖</div>
            <div>
              <div class="chat-title">{{ chatTitulo }}</div>
              <div class="chat-subtitle">{{ statusText }}</div>
            </div>
          </div>
          <button class="btn-limpiar" @click="limpiarChat" title="Nuevo chat">🗑️</button>
        </div>

        <!-- Mensajes -->
        <div class="chat-messages" ref="messagesContainer">
          <!-- Mensaje de bienvenida -->
          <div v-if="mensajes.length === 0" class="mensaje-bienvenida">
            <p>{{ bienvenidaTexto }}</p>
            <div class="sugerencias">
              <button
                v-for="sug in sugerencias"
                :key="sug"
                class="sugerencia-btn"
                @click="enviarSugerencia(sug)"
              >{{ sug }}</button>
            </div>
          </div>

          <!-- Lista de mensajes -->
          <div
            v-for="(msg, idx) in mensajes"
            :key="idx"
            class="mensaje"
            :class="msg.role"
          >
            <div class="mensaje-burbuja" v-html="renderMarkdown(msg.content)"></div>
            <div class="mensaje-tiempo">{{ msg.time }}</div>
          </div>

          <!-- Indicador de escritura -->
          <div v-if="cargando" class="mensaje bot">
            <div class="mensaje-burbuja typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="chat-input-area">
          <textarea
            v-model="inputText"
            @keydown.enter.exact.prevent="enviarMensaje"
            :disabled="cargando"
            placeholder="Escribe tu pregunta..."
            class="chat-input"
            ref="inputRef"
            rows="1"
          />
          <button
            @click="enviarMensaje"
            :disabled="cargando || !inputText.trim()"
            class="btn-enviar"
          >
            ➤
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, computed } from 'vue'
import api from '@/services/api'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

// ─── Estado ───────────────────────────────────
const isOpen = ref(false)
const cargando = ref(false)
const inputText = ref('')
const sessionId = ref('')
const messagesContainer = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLTextAreaElement | null>(null)

interface Mensaje {
  role: 'user' | 'bot'
  content: string
  time: string
  intent?: string
}

const mensajes = ref<Mensaje[]>([])

// ─── Rol del usuario ──────────────────────────
const esCliente = computed(() => auth.user?.role === 'client')

const chatTitulo = computed(() =>
  esCliente.value ? 'Asistente de Compras' : 'Asistente TechHive'
)

const bienvenidaTexto = computed(() =>
  esCliente.value
    ? '¡Hola! Puedo ayudarte a buscar productos, consultar precios y verificar disponibilidad.'
    : '¡Hola! Soy tu asistente comercial. Puedes preguntarme sobre ventas, productos y tendencias.'
)

const sugerencias = computed(() =>
  esCliente.value
    ? [
        '¿Cuánto cuesta el laptop?',
        '¿Qué categorías tienen?',
        '¿Hay auriculares disponibles?',
        'Muéstrame productos de audio',
      ]
    : [
        '¿Cuánto vendimos hoy?',
        'Top productos de este mes',
        'Ventas de esta semana',
        'Comparar este mes vs anterior',
      ]
)

// ─── Computed ─────────────────────────────────
const statusText = computed(() => {
  if (cargando.value) return 'Escribiendo...'
  return 'En línea'
})

// ─── Métodos ──────────────────────────────────
function toggleChat() {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    nextTick(() => inputRef.value?.focus())
  }
}

function horaActual(): string {
  return new Date().toLocaleTimeString('es-EC', { hour: '2-digit', minute: '2-digit' })
}

async function enviarMensaje() {
  const texto = inputText.value.trim()
  if (!texto || cargando.value) return

  // Agregar mensaje del usuario
  mensajes.value.push({ role: 'user', content: texto, time: horaActual() })
  inputText.value = ''
  cargando.value = true
  scrollAbajo()

  try {
    const { data } = await api.post('/chatbot/mensaje/', {
      mensaje: texto,
      session_id: sessionId.value,
    })

    sessionId.value = data.session_id

    mensajes.value.push({
      role: 'bot',
      content: data.respuesta,
      time: horaActual(),
      intent: data.intent,
    })
  } catch (error: any) {
    mensajes.value.push({
      role: 'bot',
      content: '⚠️ No pude conectarme al servidor. Intenta de nuevo.',
      time: horaActual(),
    })
  } finally {
    cargando.value = false
    await nextTick()
    scrollAbajo()
    inputRef.value?.focus()
  }
}

function enviarSugerencia(texto: string) {
  inputText.value = texto
  enviarMensaje()
}

async function limpiarChat() {
  if (sessionId.value) {
    try {
      await api.delete(`/chatbot/historial/${sessionId.value}/limpiar/`)
    } catch {}
  }
  mensajes.value = []
  sessionId.value = ''
}

function scrollAbajo() {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// Render básico de markdown (negritas y saltos de línea)
function renderMarkdown(texto: string): string {
  return texto
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped>
/* ── Variables ── */
:root {
  --chat-primary: #2563eb;
  --chat-bg: #ffffff;
  --chat-user-bg: #2563eb;
  --chat-bot-bg: #f1f5f9;
  --chat-border: #e2e8f0;
  --chat-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

/* ── Wrapper ── */
.chatbot-wrapper {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  font-family: 'Segoe UI', system-ui, sans-serif;
}

/* ── Botón flotante ── */
.chat-toggle {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #2563eb;
  border: none;
  cursor: pointer;
  font-size: 24px;
  color: white;
  box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.chat-toggle:hover {
  transform: scale(1.08);
  box-shadow: 0 6px 24px rgba(37, 99, 235, 0.5);
}
.chat-toggle.open {
  background: #64748b;
  box-shadow: 0 4px 20px rgba(100, 116, 139, 0.4);
}

/* ── Ventana principal ── */
.chat-window {
  position: absolute;
  bottom: 68px;
  right: 0;
  width: 360px;
  height: 520px;
  background: white;
  border-radius: 16px;
  box-shadow: var(--chat-shadow);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--chat-border);
}

/* ── Header ── */
.chat-header {
  background: #2563eb;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: white;
}
.chat-header-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.chat-avatar {
  width: 36px;
  height: 36px;
  background: rgba(255,255,255,0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}
.chat-title {
  font-weight: 600;
  font-size: 14px;
}
.chat-subtitle {
  font-size: 11px;
  opacity: 0.8;
}
.btn-limpiar {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 16px;
  opacity: 0.7;
  transition: opacity 0.2s;
}
.btn-limpiar:hover { opacity: 1; }

/* ── Mensajes ── */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: #f8fafc;
}
.chat-messages::-webkit-scrollbar { width: 4px; }
.chat-messages::-webkit-scrollbar-track { background: transparent; }
.chat-messages::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }

/* ── Bienvenida ── */
.mensaje-bienvenida {
  text-align: center;
  color: #64748b;
  font-size: 13px;
  padding: 8px;
}
.sugerencias {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
  margin-top: 10px;
}
.sugerencia-btn {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 5px 12px;
  font-size: 12px;
  cursor: pointer;
  color: #2563eb;
  transition: background 0.2s;
}
.sugerencia-btn:hover {
  background: #eff6ff;
}

/* ── Burbuja de mensaje ── */
.mensaje {
  display: flex;
  flex-direction: column;
  max-width: 80%;
}
.mensaje.user {
  align-self: flex-end;
  align-items: flex-end;
}
.mensaje.bot {
  align-self: flex-start;
  align-items: flex-start;
}
.mensaje-burbuja {
  padding: 10px 14px;
  border-radius: 16px;
  font-size: 13.5px;
  line-height: 1.5;
}
.mensaje.user .mensaje-burbuja {
  background: #2563eb;
  color: white;
  border-bottom-right-radius: 4px;
}
.mensaje.bot .mensaje-burbuja {
  background: white;
  color: #1e293b;
  border-bottom-left-radius: 4px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.mensaje-tiempo {
  font-size: 10px;
  color: #94a3b8;
  margin-top: 3px;
  padding: 0 4px;
}

/* ── Typing indicator ── */
.typing-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 12px 16px;
}
.typing-indicator span {
  width: 7px;
  height: 7px;
  background: #94a3b8;
  border-radius: 50%;
  animation: typing 1.2s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
  0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
  40% { transform: scale(1.1); opacity: 1; }
}

/* ── Input ── */
.chat-input-area {
  padding: 12px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  gap: 8px;
  background: white;
}
.chat-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  font-size: 13.5px;
  outline: none;
  background: #f8fafc;
  transition: border-color 0.2s;
  resize: none;
  min-height: 38px;
  max-height: 100px;
  overflow-y: auto;
  line-height: 1.5;
  font-family: inherit;
  word-break: break-word;
  white-space: pre-wrap;
}
.chat-input:focus {
  border-color: #2563eb;
  background: white;
}
.chat-input:disabled {
  opacity: 0.6;
}
.btn-enviar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #2563eb;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.15s;
  flex-shrink: 0;
}
.btn-enviar:hover:not(:disabled) {
  background: #1d4ed8;
  transform: scale(1.05);
}
.btn-enviar:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* ── Transición ── */
.chat-slide-enter-active,
.chat-slide-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.chat-slide-enter-from,
.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.97);
}

/* ── Responsive ── */
@media (max-width: 420px) {
  .chat-window {
    width: calc(100vw - 32px);
    right: -8px;
  }
}
</style>
