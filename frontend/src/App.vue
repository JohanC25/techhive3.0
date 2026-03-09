<template>
  <div>
    <router-view />
    <ChatBot v-if="auth.isAuthenticated" />
  </div>
</template>

<script setup lang="ts">
import ChatBot from '@/components/ChatBot.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>
