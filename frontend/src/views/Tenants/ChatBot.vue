<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const message = ref('')
const chatHistory = ref([
  { role: 'ai', text: '¡Hola! Soy tu asistente IA. ¿En qué puedo ayudarte hoy?' }
])

const sendMessage = () => {
  if (!message.value.trim()) return
  
  // Agregar mensaje del usuario
  chatHistory.value.push({ role: 'user', text: message.value })
  
  // Simulación de respuesta (Aquí conectarías con tu API de Django + Gemini/GPT)
  setTimeout(() => {
    chatHistory.value.push({ role: 'ai', text: 'Estoy procesando tu solicitud sobre: ' + message.value })
  }, 1000)
  
  message.value = ''
}

const goBack = () => router.push('/dashboard')
</script>

<template>
  <div class="chat-container">
    <header>
      <button class="back-btn" @click="goBack">← Volver al Panel</button>
      <h2>Asistente ChatBot IA</h2>
    </header>

    <div class="chat-window">
      <div v-for="(msg, index) in chatHistory" :key="index" :class="['message', msg.role]">
        <div class="bubble">{{ msg.text }}</div>
      </div>
    </div>

    <div class="input-area">
      <input 
        v-model="message" 
        @keyup.enter="sendMessage" 
        placeholder="Escribe tu consulta aquí..." 
      />
      <button @click="sendMessage">Enviar</button>
    </div>
  </div>
</template>

<style scoped>
.chat-container {
  max-width: 800px;
  margin: 20px auto;
  display: flex;
  flex-direction: column;
  height: 85vh;
  border: 1px solid #ddd;
  border-radius: 12px;
  background: white;
}

header {
  padding: 15px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 20px;
}

.chat-window {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 15px;
  background: #f9fafb;
}

.message { display: flex; }
.message.user { justify-content: flex-end; }
.bubble {
  max-width: 70%;
  padding: 12px;
  border-radius: 15px;
  font-size: 0.95rem;
}
.ai .bubble { background: #e5e7eb; color: #1f2937; }
.user .bubble { background: #3b82f6; color: white; }

.input-area {
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 10px;
}

input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.back-btn {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-weight: bold;
}
</style>