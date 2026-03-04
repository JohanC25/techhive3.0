<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="landing">
    <nav class="navbar">
      <h1>MySaaS</h1>
      <button @click="goToLogin">Admin Login</button>
    </nav>

    <section class="hero">
      <h2>Multi-Tenant Business Management Platform</h2>
      <p>
        Create secure, independent systems for every company.
      </p>

      <button class="cta" @click="goToLogin">
        Get Started
      </button>
    </section>
  </div>
</template>

<style scoped>
.landing {
  font-family: Arial, sans-serif;
  text-align: center;
}

.navbar {
  display: flex;
  justify-content: space-between;
  padding: 20px 40px;
}

.hero {
  margin-top: 120px;
}

.cta {
  margin-top: 20px;
  padding: 12px 24px;
  font-size: 16px;
  cursor: pointer;
}
</style>