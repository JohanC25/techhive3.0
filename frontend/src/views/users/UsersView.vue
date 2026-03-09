<template>
  <div class="view">
    <!-- Header -->
    <div class="view-header">
      <div>
        <h2 class="view-title">Usuarios</h2>
        <p class="view-sub">Gestión de empleados y clientes de la empresa</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        Nuevo usuario
      </button>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <input v-model="search" @input="debouncedLoad" type="search" placeholder="Buscar por nombre o usuario..." class="filter-input filter-search" />
      <select v-model="filterRole" @change="loadData" class="filter-select">
        <option value="">Todos los roles</option>
        <option value="admin">Administrador</option>
        <option value="manager">Gerente</option>
        <option value="employee">Empleado</option>
        <option value="client">Cliente</option>
      </select>
    </div>

    <!-- Table -->
    <div class="table-card">
      <div v-if="loading" class="table-loading"><div class="spinner-lg"></div></div>

      <table v-else-if="items.length" class="data-table">
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Nombre</th>
            <th>Email</th>
            <th>Rol</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in items" :key="u.id">
            <td><span class="username-chip">{{ u.username }}</span></td>
            <td>{{ [u.first_name, u.last_name].filter(Boolean).join(' ') || '—' }}</td>
            <td>{{ u.email || '—' }}</td>
            <td><span class="role-badge" :class="`role-${u.role}`">{{ roleLabel(u.role) }}</span></td>
            <td>
              <span class="status-dot" :class="u.is_active ? 'active' : 'inactive'">
                {{ u.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="actions-cell">
              <button class="btn-icon" title="Editar" @click="openEdit(u)">
                <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
              </button>
              <button class="btn-icon btn-icon--danger" title="Eliminar" @click="confirmDelete(u)" :disabled="u.id === currentUserId">
                <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else class="table-empty">
        <svg width="40" height="40" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
        <p>No hay usuarios registrados.</p>
      </div>
    </div>

    <!-- ─── Modal Crear / Editar ─── -->
    <Transition name="modal">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h2 class="modal-title">{{ editTarget ? 'Editar usuario' : 'Nuevo usuario' }}</h2>
            <button class="btn-close" @click="closeModal">
              <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>

          <form class="modal-form" @submit.prevent="saveUser">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Nombre *</label>
                <input v-model="form.first_name" class="form-input" placeholder="Juan" />
              </div>
              <div class="form-group">
                <label class="form-label">Apellido *</label>
                <input v-model="form.last_name" class="form-input" placeholder="Pérez" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Usuario *</label>
                <input v-model="form.username" class="form-input" placeholder="jperez" :disabled="!!editTarget" required />
              </div>
              <div class="form-group">
                <label class="form-label">Teléfono</label>
                <input v-model="form.phone" class="form-input" placeholder="0999999999" />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Email</label>
                <input v-model="form.email" type="email" class="form-input" placeholder="correo@ejemplo.com" />
              </div>
              <div class="form-group">
                <label class="form-label">Rol *</label>
                <select v-model="form.role" class="form-input" required>
                  <option value="admin">Administrador</option>
                  <option value="manager">Gerente</option>
                  <option value="employee">Empleado</option>
                  <option value="client">Cliente</option>
                </select>
              </div>
            </div>

            <!-- Contraseña solo en creación -->
            <div v-if="!editTarget" class="form-row">
              <div class="form-group">
                <label class="form-label">Contraseña *</label>
                <input v-model="form.password" type="password" class="form-input" placeholder="Mínimo 8 caracteres" required />
              </div>
              <div class="form-group">
                <label class="form-label">Confirmar contraseña *</label>
                <input v-model="form.password2" type="password" class="form-input" placeholder="Repetir contraseña" required />
              </div>
            </div>

            <!-- Estado solo en edición -->
            <div v-if="editTarget" class="form-group">
              <label class="form-label">Estado</label>
              <select v-model="form.is_active" class="form-input">
                <option :value="true">Activo</option>
                <option :value="false">Inactivo</option>
              </select>
            </div>

            <Transition name="slide">
              <div v-if="formError" class="error-box">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10"/><path stroke-linecap="round" d="M12 8v4m0 4h.01"/>
                </svg>
                {{ formError }}
              </div>
            </Transition>

            <div class="modal-actions">
              <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="saving">
                <span v-if="saving" class="spinner"></span>
                <span v-else>{{ editTarget ? 'Guardar cambios' : 'Crear usuario' }}</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </Transition>

    <!-- ─── Modal Eliminar ─── -->
    <Transition name="modal">
      <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
        <div class="modal modal--sm">
          <div class="modal-header">
            <h2 class="modal-title">¿Eliminar usuario?</h2>
            <button class="btn-close" @click="deleteTarget = null">
              <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <p class="delete-warning">
            Se eliminará el usuario <strong>{{ deleteTarget?.username }}</strong>. Esta acción no se puede deshacer.
          </p>
          <div class="modal-actions">
            <button class="btn-secondary" @click="deleteTarget = null">Cancelar</button>
            <button class="btn-danger" :disabled="deleting" @click="deleteUser">
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
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

interface UserItem {
  id: number
  username: string
  first_name: string
  last_name: string
  email: string
  role: string
  phone: string
  is_active: boolean
}

const auth = useAuthStore()
const currentUserId = computed(() => auth.user?.id)

const items = ref<UserItem[]>([])
const loading = ref(true)
const search = ref('')
const filterRole = ref('')

const showModal = ref(false)
const editTarget = ref<UserItem | null>(null)
const saving = ref(false)
const formError = ref('')
const form = ref({
  username: '', first_name: '', last_name: '',
  email: '', role: 'employee', phone: '',
  password: '', password2: '', is_active: true,
})

const deleteTarget = ref<UserItem | null>(null)
const deleting = ref(false)

const ROLE_LABELS: Record<string, string> = {
  admin: 'Administrador', manager: 'Gerente',
  employee: 'Empleado', client: 'Cliente',
}
const roleLabel = (r: string) => ROLE_LABELS[r] ?? r

let debounceTimer: ReturnType<typeof setTimeout>
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(loadData, 350)
}

async function loadData() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (search.value) params.set('search', search.value)
    const { data } = await api.get(`/users/?${params}`)
    const list: UserItem[] = Array.isArray(data) ? data : (data.results ?? [])
    items.value = filterRole.value ? list.filter((u) => u.role === filterRole.value) : list
  } finally {
    loading.value = false
  }
}

onMounted(loadData)

function openCreate() {
  editTarget.value = null
  form.value = { username: '', first_name: '', last_name: '', email: '', role: 'employee', phone: '', password: '', password2: '', is_active: true }
  formError.value = ''
  showModal.value = true
}

function openEdit(u: UserItem) {
  editTarget.value = u
  form.value = { username: u.username, first_name: u.first_name, last_name: u.last_name, email: u.email, role: u.role, phone: u.phone, password: '', password2: '', is_active: u.is_active }
  formError.value = ''
  showModal.value = true
}

function closeModal() { showModal.value = false }

async function saveUser() {
  formError.value = ''
  saving.value = true
  try {
    if (editTarget.value) {
      const { data } = await api.patch(`/users/${editTarget.value.id}/`, {
        first_name: form.value.first_name,
        last_name: form.value.last_name,
        email: form.value.email,
        role: form.value.role,
        phone: form.value.phone,
        is_active: form.value.is_active,
      })
      const idx = items.value.findIndex((u) => u.id === editTarget.value!.id)
      if (idx > -1) items.value[idx] = data
    } else {
      const { data } = await api.post('/users/', form.value)
      items.value.unshift(data)
    }
    closeModal()
  } catch (e: any) {
    const err = e.response?.data
    if (typeof err === 'object') {
      formError.value = Object.values(err).flat().join(' ')
    } else {
      formError.value = 'Error al guardar el usuario.'
    }
  } finally {
    saving.value = false
  }
}

function confirmDelete(u: UserItem) { deleteTarget.value = u }

async function deleteUser() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await api.delete(`/users/${deleteTarget.value.id}/`)
    items.value = items.value.filter((u) => u.id !== deleteTarget.value!.id)
    deleteTarget.value = null
  } finally {
    deleting.value = false
  }
}
</script>

<style scoped>
.view { display: flex; flex-direction: column; gap: 20px; }
.view-header { display: flex; align-items: flex-start; justify-content: space-between; }
.view-title { font-size: 22px; font-weight: 800; color: #0f172a; margin: 0; }
.view-sub { font-size: 13px; color: #64748b; margin: 3px 0 0; }

.filters-bar { display: flex; gap: 12px; flex-wrap: wrap; }
.filter-input { padding: 9px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #1e293b; outline: none; background: white; transition: border-color 0.2s; }
.filter-input:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
.filter-search { flex: 1; min-width: 200px; }
.filter-select { padding: 9px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #374151; background: white; outline: none; cursor: pointer; }

.table-card { background: white; border-radius: 14px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
.table-loading { display: flex; justify-content: center; padding: 60px; }
.spinner-lg { width: 36px; height: 36px; border: 3px solid #e2e8f0; border-top-color: #2563eb; border-radius: 50%; animation: spin 0.8s linear infinite; }
.data-table { width: 100%; border-collapse: collapse; font-size: 14px; }
.data-table th { padding: 13px 16px; text-align: left; font-size: 12px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.data-table td { padding: 13px 16px; border-bottom: 1px solid #f1f5f9; color: #374151; }
.data-table tr:last-child td { border-bottom: none; }
.data-table tr:hover td { background: #fafafa; }

.username-chip { font-family: monospace; font-size: 13px; font-weight: 600; color: #2563eb; background: #eff6ff; padding: 2px 8px; border-radius: 6px; }

.role-badge { font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px; }
.role-admin    { background: #ede9fe; color: #5b21b6; }
.role-manager  { background: #dbeafe; color: #1d4ed8; }
.role-employee { background: #dcfce7; color: #166534; }
.role-client   { background: #fef3c7; color: #92400e; }

.status-dot { font-size: 12px; font-weight: 600; display: flex; align-items: center; gap: 5px; }
.status-dot::before { content: ''; width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.status-dot.active::before   { background: #22c55e; }
.status-dot.inactive::before { background: #94a3b8; }
.status-dot.active   { color: #166534; }
.status-dot.inactive { color: #64748b; }

.actions-cell { display: flex; gap: 6px; }
.btn-icon { padding: 6px; background: white; border: 1px solid #e2e8f0; border-radius: 7px; cursor: pointer; color: #64748b; display: flex; align-items: center; transition: all 0.2s; }
.btn-icon:hover { background: #f8fafc; color: #2563eb; border-color: #bfdbfe; }
.btn-icon--danger:hover { background: #fef2f2; color: #ef4444; border-color: #fecaca; }
.btn-icon:disabled { opacity: 0.3; cursor: not-allowed; }

.table-empty { display: flex; flex-direction: column; align-items: center; gap: 10px; padding: 60px; color: #94a3b8; font-size: 14px; }

/* Buttons */
.btn-primary { display: flex; align-items: center; gap: 7px; padding: 10px 20px; background: #2563eb; color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; transition: background 0.2s; box-shadow: 0 4px 12px rgba(37,99,235,0.3); }
.btn-primary:hover:not(:disabled) { background: #1d4ed8; }
.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }
.btn-secondary { padding: 10px 20px; background: white; color: #374151; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s; }
.btn-secondary:hover { background: #f8fafc; }
.btn-danger { display: flex; align-items: center; gap: 7px; padding: 10px 20px; background: #ef4444; color: white; border: none; border-radius: 10px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-danger:hover:not(:disabled) { background: #dc2626; }
.btn-danger:disabled { opacity: 0.55; cursor: not-allowed; }

/* Modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.6); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; }
.modal { background: white; border-radius: 20px; width: 100%; max-width: 540px; max-height: 90vh; overflow-y: auto; box-shadow: 0 25px 60px rgba(0,0,0,0.3); }
.modal--sm { max-width: 420px; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 24px 28px 0; }
.modal-title { font-size: 20px; font-weight: 700; color: #0f172a; margin: 0; }
.btn-close { padding: 6px; background: none; border: none; cursor: pointer; color: #94a3b8; border-radius: 8px; display: flex; transition: all 0.2s; }
.btn-close:hover { background: #f1f5f9; color: #475569; }
.modal-form { padding: 20px 28px 28px; display: flex; flex-direction: column; gap: 16px; }
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { display: flex; flex-direction: column; gap: 6px; }
.form-label { font-size: 13px; font-weight: 600; color: #374151; }
.form-input { width: 100%; padding: 10px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px; font-size: 14px; color: #1e293b; outline: none; transition: border-color 0.2s; box-sizing: border-box; background: #f8fafc; }
.form-input:focus { border-color: #2563eb; background: white; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
.form-input:disabled { opacity: 0.6; cursor: not-allowed; }
.error-box { display: flex; align-items: center; gap: 8px; padding: 10px 14px; background: #fef2f2; border: 1px solid #fecaca; border-radius: 8px; font-size: 13px; color: #b91c1c; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; padding-top: 4px; }
.delete-warning { padding: 16px 28px; font-size: 14px; color: #374151; line-height: 1.6; margin: 0; }
.delete-warning strong { color: #0f172a; }

.spinner { width: 16px; height: 16px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.modal-enter-active, .modal-leave-active { transition: all 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95); }
.slide-enter-active, .slide-leave-active { transition: all 0.2s ease; }
.slide-enter-from { opacity: 0; transform: translateY(-6px); }
.slide-leave-to   { opacity: 0; }
</style>
