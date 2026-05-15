<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits<{
  (e: 'scan', code: string): void
}>()

const isActive = ref(false)
let buffer = ''
let timeout: number | null = null

function handleKeydown(e: KeyboardEvent) {
  if (!isActive.value) return

  if (e.key === 'Tab') {
    e.preventDefault()
    e.stopPropagation()
    console.log('CODE:', buffer)

    if (buffer.length > 0) {
      emit('scan', buffer)
      buffer = ''
    }
    return
  }

  if (timeout) clearTimeout(timeout)

  if (/^[0-9]$/.test(e.key)) {
    buffer += e.key
  }

  timeout = window.setTimeout(() => {
    buffer = ''
  }, 100)
}

function openScanner() {
  isActive.value = true
}

function closeScanner() {
  isActive.value = false
  buffer = ''
  
  // 🔥 limpiar posibles residuos
  setTimeout(() => {
    buffer = ''
  }, 50)
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown, true)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown, true)
})

defineExpose({
  openScanner
})
</script>

<template>
  
  <!-- Modal -->
  <div v-if="isActive" class="scanner-modal">
    <div class="scanner-box">
      <h3>Escaneando...</h3>

      <div class="loader"></div>

      <p>Pasa los códigos de barras</p>

      <button class="btn-danger" @click="closeScanner">
        Finalizar
      </button>
    </div>
  </div>
</template>

<style scoped>
.scanner-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.scanner-box {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
}

.loader {
  margin: 20px auto;
  width: 40px;
  height: 40px;
  border: 4px solid #ccc;
  border-top-color: black;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>