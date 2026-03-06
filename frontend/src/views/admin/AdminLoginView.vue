<template>
  <div class="login-page">
    <div class="login-card">
      <!-- Brand -->
      <div class="brand">
        <div class="brand-icon">T</div>
        <div>
          <h1 class="brand-name">TechHive Admin</h1>
          <p class="brand-sub">Portal de administración</p>
        </div>
      </div>

      <!-- Form -->
      <form class="login-form" @submit.prevent="handleLogin">
        <div class="form-group">
          <label class="form-label">Clave maestra</label>
          <div class="input-password">
            <input
              v-model="key"
              :type="showKey ? 'text' : 'password'"
              class="form-input"
              :class="{ 'form-input--error': error }"
              placeholder="Ingresa la clave de administrador"
              autofocus
            />
            <button type="button" class="btn-eye" @click="showKey = !showKey">
              <svg v-if="!showKey" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
              <svg v-else width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
              </svg>
            </button>
          </div>
        </div>

        <Transition name="slide">
          <div v-if="error" class="error-box">
            <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10"/><path stroke-linecap="round" d="M12 8v4m0 4h.01"/>
            </svg>
            {{ error }}
          </div>
        </Transition>

        <button type="submit" class="btn-submit" :disabled="loading || !key">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Acceder</span>
        </button>
      </form>
    </div>

    <div class="bg-deco">
      <div class="deco-circle deco-1"></div>
      <div class="deco-circle deco-2"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/adminStore'

const admin = useAdminStore()
const router = useRouter()

const key = ref('')
const error = ref('')
const loading = ref(false)
const showKey = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await admin.login(key.value)
    router.push('/')
  } catch (e: any) {
    if (e.response?.status === 401) {
      error.value = 'Clave incorrecta.'
    } else {
      error.value = 'No se pudo conectar al servidor.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
}
.login-card {
  background: white;
  border-radius: 20px;
  padding: 44px 40px;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 25px 60px rgba(0,0,0,0.35);
  position: relative;
  z-index: 1;
}
.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 36px;
}
.brand-icon {
  width: 52px; height: 52px;
  background: #7c3aed;
  border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 26px; font-weight: 800; color: white;
  box-shadow: 0 8px 20px rgba(124,58,237,0.4);
}
.brand-name { font-size: 24px; font-weight: 800; color: #0f172a; margin: 0; line-height: 1.1; }
.brand-sub { font-size: 13px; color: #94a3b8; margin: 2px 0 0 0; }
.login-form { display: flex; flex-direction: column; gap: 20px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 13px; font-weight: 600; color: #374151; }
.form-input {
  width: 100%; padding: 12px 14px;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  font-size: 14px; color: #1e293b; outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box; background: #f8fafc;
}
.form-input:focus { border-color: #7c3aed; background: white; box-shadow: 0 0 0 3px rgba(124,58,237,0.1); }
.form-input--error { border-color: #ef4444; }
.input-password { position: relative; }
.input-password .form-input { padding-right: 44px; }
.btn-eye {
  position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer; color: #94a3b8; display: flex; padding: 4px;
}
.btn-eye:hover { color: #64748b; }
.error-box {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px;
  background: #fef2f2; border: 1px solid #fecaca;
  border-radius: 8px; font-size: 13px; color: #b91c1c;
}
.btn-submit {
  padding: 13px; background: #7c3aed; color: white;
  border: none; border-radius: 10px; font-size: 15px; font-weight: 600;
  cursor: pointer; transition: background 0.2s, transform 0.15s, box-shadow 0.2s;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  box-shadow: 0 4px 14px rgba(124,58,237,0.35);
}
.btn-submit:hover:not(:disabled) { background: #6d28d9; transform: translateY(-1px); box-shadow: 0 6px 20px rgba(124,58,237,0.4); }
.btn-submit:disabled { opacity: 0.55; cursor: not-allowed; transform: none; }
.spinner {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3); border-top-color: white;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from { opacity: 0; transform: translateY(-8px); }
.slide-leave-to   { opacity: 0; transform: translateY(-4px); }
.bg-deco { position: absolute; inset: 0; pointer-events: none; }
.deco-circle { position: absolute; border-radius: 50%; background: rgba(124,58,237,0.12); }
.deco-1 { width: 400px; height: 400px; top: -100px; right: -100px; }
.deco-2 { width: 300px; height: 300px; bottom: -80px; left: -80px; }
</style>
