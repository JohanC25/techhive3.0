<template>
  <div>
    <router-view />
    <ChatBot />
  </div>
</template>

<script setup lang="ts">
import ChatBot from '@/components/ChatBot.vue'
</script>