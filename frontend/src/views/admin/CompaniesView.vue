<template>
  <div>
    <!-- Header -->
    <div class="page-header">
      <div>
        <h1 class="page-title">Empresas</h1>
        <p class="page-sub">Gestión de tenants y módulos habilitados</p>
      </div>
      <button class="btn-primary" @click="openCreateModal">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        Nueva empresa
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <span class="spinner-lg"></span>
      <p>Cargando empresas...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="companies.length === 0" class="empty-state">
      <svg width="48" height="48" fill="none" stroke="#94a3b8" stroke-width="1.5" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
      </svg>
      <p>No hay empresas registradas.</p>
      <button class="btn-primary" @click="openCreateModal">Crear primera empresa</button>
    </div>

    <!-- Companies grid -->
    <div v-else class="companies-grid">
      <div v-for="company in companies" :key="company.id" class="company-card">
        <div class="card-header">
          <div class="company-avatar">{{ company.name[0].toUpperCase() }}</div>
          <div class="company-info">
            <h3 class="company-name">{{ company.name }}</h3>
            <div class="company-meta">
              <span class="meta-badge schema">{{ company.schema_name }}</span>
              <span class="meta-badge domain">{{ company.domain }}</span>
            </div>
          </div>
          <button class="btn-delete" @click="confirmDelete(company)" title="Eliminar empresa">
            <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
            </svg>
          </button>
        </div>

        <!-- Modules -->
        <div class="modules-section">
          <p class="modules-label">Módulos habilitados</p>
          <div class="modules-grid">
            <label
              v-for="mod in allModules"
              :key="mod.code"
              class="module-toggle"
              :class="{ active: hasModule(company, mod.code) }"
            >
              <input
                type="checkbox"
                :checked="hasModule(company, mod.code)"
                @change="toggleModule(company, mod.code)"
              />
              <span class="toggle-dot"></span>
              <span class="toggle-label">{{ mod.name }}</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- ─── Create Company Modal ─── -->
    <Transition name="modal">
      <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
        <div class="modal">
          <div class="modal-header">
            <h2 class="modal-title">Nueva empresa</h2>
            <button class="btn-close" @click="closeCreateModal">
              <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <form class="modal-form" @submit.prevent="createCompany">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Nombre de la empresa *</label>
                <input v-model="form.name" class="form-input" placeholder="Ej: Magic Computer" required />
              </div>
              <div class="form-group">
                <label class="form-label">Schema (único) *</label>
                <input v-model="form.schema_name" class="form-input" placeholder="magic_computer" required
                  pattern="[a-z0-9_]+" title="Solo letras minúsculas, números y guiones bajos" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Dominio *</label>
                <input v-model="form.domain" class="form-input" placeholder="magiccomputer.localhost" required />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Usuario admin *</label>
                <input v-model="form.admin_username" class="form-input" placeholder="admin" required />
              </div>
              <div class="form-group">
                <label class="form-label">Contraseña admin *</label>
                <input v-model="form.admin_password" type="password" class="form-input" placeholder="Contraseña segura" required />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Módulos a habilitar</label>
              <div class="modules-checkboxes">
                <label v-for="mod in allModules" :key="mod.code" class="checkbox-item">
                  <input type="checkbox" v-model="form.modules" :value="mod.code" />
                  <span>{{ mod.name }}</span>
                </label>
              </div>
            </div>

            <Transition name="slide">
              <div v-if="createError" class="error-box">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10"/><path stroke-linecap="round" d="M12 8v4m0 4h.01"/>
                </svg>
                {{ createError }}
              </div>
            </Transition>

            <div class="modal-actions">
              <button type="button" class="btn-secondary" @click="closeCreateModal">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="creating">
                <span v-if="creating" class="spinner"></span>
                <span v-else>Crear empresa</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- ─── Delete Confirm Modal ─── -->
    <Transition name="modal">
      <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
        <div class="modal modal--sm">
          <div class="modal-header">
            <h2 class="modal-title">¿Eliminar empresa?</h2>
            <button class="btn-close" @click="deleteTarget = null">
              <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <p class="delete-warning">
            Se eliminará la empresa <strong>{{ deleteTarget?.name }}</strong> y su schema
            <code>{{ deleteTarget?.schema_name }}</code>. Esta acción no se puede deshacer.
          </p>
          <div class="modal-actions">
            <button class="btn-secondary" @click="deleteTarget = null">Cancelar</button>
            <button class="btn-danger" :disabled="deleting" @click="deleteCompany">
              <span v-if="deleting" class="spinner"></span>
              <span v-else>Eliminar</span>
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import adminApi from '@/services/adminApi'

interface Module { code: string; name: string }
interface Company {
  id: number
  name: string
  schema_name: string
  domain: string | null
  on_trial: boolean
  created_on: string
  modules: Module[]
}

const companies = ref<Company[]>([])
const allModules = ref<Module[]>([])
const loading = ref(true)

// ── Create modal ──
const showCreateModal = ref(false)
const creating = ref(false)
const createError = ref('')
const form = ref({
  name: '',
  schema_name: '',
  domain: '',
  admin_username: '',
  admin_password: '',
  modules: [] as string[],
})

// ── Delete modal ──
const deleteTarget = ref<Company | null>(null)
const deleting = ref(false)

// ── Load data ──
async function loadData() {
  loading.value = true
  try {
    const [companiesRes, modulesRes] = await Promise.all([
      adminApi.get('/companies/'),
      adminApi.get('/modules/'),
    ])
    companies.value = companiesRes.data
    allModules.value = modulesRes.data
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

// ── Helpers ──
function hasModule(company: Company, code: string) {
  return company.modules.some((m) => m.code === code)
}

// ── Module toggle ──
async function toggleModule(company: Company, code: string) {
  const current = company.modules.map((m) => m.code)
  const newCodes = current.includes(code)
    ? current.filter((c) => c !== code)
    : [...current, code]

  try {
    const { data } = await adminApi.put(`/companies/${company.id}/modules/`, { modules: newCodes })
    company.modules = data.modules
  } catch {
    // revert nothing — reload on next fetch
  }
}

// ── Create company ──
function openCreateModal() {
  form.value = { name: '', schema_name: '', domain: '', admin_username: '', admin_password: '', modules: [] }
  createError.value = ''
  showCreateModal.value = true
}

function closeCreateModal() {
  showCreateModal.value = false
}

async function createCompany() {
  createError.value = ''
  creating.value = true
  try {
    const { data } = await adminApi.post('/companies/', form.value)
    companies.value.push({ ...data, on_trial: false, created_on: '', modules: allModules.value.filter((m) => form.value.modules.includes(m.code)) })
    closeCreateModal()
  } catch (e: any) {
    createError.value = e.response?.data?.detail || 'Error al crear la empresa.'
  } finally {
    creating.value = false
  }
}

// ── Delete company ──
function confirmDelete(company: Company) {
  deleteTarget.value = company
}

async function deleteCompany() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await adminApi.delete(`/companies/${deleteTarget.value.id}/`)
    companies.value = companies.value.filter((c) => c.id !== deleteTarget.value!.id)
    deleteTarget.value = null
  } catch {
    // ignore
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
/* ── Page header ── */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 28px;
}
.page-title { font-size: 26px; font-weight: 800; color: #0f172a; margin: 0; }
.page-sub { font-size: 14px; color: #64748b; margin: 4px 0 0; }

/* ── States ── */
.loading-state, .empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 16px; padding: 80px 0; color: #64748b; font-size: 15px;
}
.spinner-lg {
  width: 40px; height: 40px;
  border: 3px solid #e2e8f0; border-top-color: #7c3aed;
  border-radius: 50%; animation: spin 0.8s linear infinite;
}

/* ── Grid ── */
.companies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

/* ── Company card ── */
.company-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  border: 1px solid #e2e8f0;
  transition: box-shadow 0.2s;
}
.company-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.1); }

.card-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 20px;
}
.company-avatar {
  width: 44px; height: 44px;
  background: linear-gradient(135deg, #7c3aed, #4f46e5);
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; font-weight: 800; color: white;
  flex-shrink: 0;
}
.company-info { flex: 1; min-width: 0; }
.company-name { font-size: 16px; font-weight: 700; color: #0f172a; margin: 0 0 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.company-meta { display: flex; gap: 6px; flex-wrap: wrap; }
.meta-badge {
  font-size: 11px; font-weight: 600; padding: 2px 8px;
  border-radius: 20px; letter-spacing: 0.3px;
}
.meta-badge.schema { background: #ede9fe; color: #5b21b6; }
.meta-badge.domain { background: #dbeafe; color: #1d4ed8; }

.btn-delete {
  flex-shrink: 0; padding: 7px;
  background: none; border: 1px solid #e2e8f0; border-radius: 8px;
  color: #94a3b8; cursor: pointer; transition: all 0.2s;
  display: flex; align-items: center;
}
.btn-delete:hover { background: #fef2f2; border-color: #fecaca; color: #ef4444; }

/* ── Modules toggle ── */
.modules-section { border-top: 1px solid #f1f5f9; padding-top: 16px; }
.modules-label { font-size: 12px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 12px; }
.modules-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.module-toggle {
  display: flex; align-items: center; gap: 7px;
  padding: 6px 12px;
  border-radius: 20px;
  border: 1.5px solid #e2e8f0;
  background: #f8fafc;
  cursor: pointer;
  transition: all 0.2s;
  user-select: none;
}
.module-toggle input { display: none; }
.module-toggle.active {
  background: #ede9fe;
  border-color: #7c3aed;
}
.toggle-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #cbd5e1; transition: background 0.2s;
  flex-shrink: 0;
}
.module-toggle.active .toggle-dot { background: #7c3aed; }
.toggle-label { font-size: 12px; font-weight: 500; color: #475569; }
.module-toggle.active .toggle-label { color: #5b21b6; font-weight: 600; }

/* ── Buttons ── */
.btn-primary {
  display: flex; align-items: center; gap: 7px;
  padding: 10px 20px;
  background: #7c3aed; color: white;
  border: none; border-radius: 10px;
  font-size: 14px; font-weight: 600; cursor: pointer;
  transition: background 0.2s, transform 0.15s;
  box-shadow: 0 4px 12px rgba(124,58,237,0.3);
}
.btn-primary:hover:not(:disabled) { background: #6d28d9; transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-secondary {
  padding: 10px 20px; background: white; color: #374151;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  font-size: 14px; font-weight: 500; cursor: pointer;
  transition: all 0.2s;
}
.btn-secondary:hover { background: #f8fafc; }
.btn-danger {
  display: flex; align-items: center; gap: 7px;
  padding: 10px 20px; background: #ef4444; color: white;
  border: none; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer;
  transition: background 0.2s;
}
.btn-danger:hover:not(:disabled) { background: #dc2626; }
.btn-danger:disabled { opacity: 0.55; cursor: not-allowed; }

/* ── Modal ── */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(15,23,42,0.6);
  backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000; padding: 20px;
}
.modal {
  background: white; border-radius: 20px;
  width: 100%; max-width: 560px;
  max-height: 90vh; overflow-y: auto;
  box-shadow: 0 25px 60px rgba(0,0,0,0.3);
}
.modal--sm { max-width: 420px; }
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 24px 28px 0;
}
.modal-title { font-size: 20px; font-weight: 700; color: #0f172a; margin: 0; }
.btn-close {
  padding: 6px; background: none; border: none; cursor: pointer;
  color: #94a3b8; border-radius: 8px;
  display: flex; align-items: center;
  transition: all 0.2s;
}
.btn-close:hover { background: #f1f5f9; color: #475569; }

.modal-form { padding: 20px 28px 28px; display: flex; flex-direction: column; gap: 16px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 13px; font-weight: 600; color: #374151; }
.form-input {
  width: 100%; padding: 10px 14px;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  font-size: 14px; color: #1e293b; outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box; background: #f8fafc;
}
.form-input:focus { border-color: #7c3aed; background: white; box-shadow: 0 0 0 3px rgba(124,58,237,0.1); }

.modules-checkboxes {
  display: flex; flex-wrap: wrap; gap: 8px;
  padding: 12px; background: #f8fafc; border-radius: 10px;
  border: 1.5px solid #e2e8f0;
}
.checkbox-item {
  display: flex; align-items: center; gap: 7px;
  padding: 5px 10px; cursor: pointer; border-radius: 6px;
  font-size: 13px; color: #475569;
  transition: background 0.15s;
}
.checkbox-item:hover { background: #ede9fe; }
.checkbox-item input[type="checkbox"] { accent-color: #7c3aed; width: 14px; height: 14px; }

.error-box {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px;
  background: #fef2f2; border: 1px solid #fecaca;
  border-radius: 8px; font-size: 13px; color: #b91c1c;
}
.modal-actions {
  display: flex; justify-content: flex-end; gap: 10px;
  padding-top: 8px;
}

.delete-warning {
  padding: 16px 28px; font-size: 14px; color: #374151; line-height: 1.6; margin: 0;
}
.delete-warning strong { color: #0f172a; }
.delete-warning code { background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-size: 13px; color: #5b21b6; }

/* ── Spinner ── */
.spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(255,255,255,0.3); border-top-color: white;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Transitions ── */
.modal-enter-active, .modal-leave-active { transition: all 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95); }
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from { opacity: 0; transform: translateY(-6px); }
.slide-leave-to   { opacity: 0; }
</style>
