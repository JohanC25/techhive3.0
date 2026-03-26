<template>
  <div class="view">
    <div class="view-header">
      <div>
        <h2 class="view-title">Caja</h2>
        <p class="view-sub">Registro de ingresos y egresos</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        Nuevo movimiento
      </button>
    </div>

    <!-- Session banner -->
    <div v-if="session" class="session-banner">
      <span>Caja abierta el {{ session.date }}</span>
      <span>Monto inicial: <strong>${{ Number(session.opening_amount).toFixed(2) }}</strong></span>
      <span v-if="session.opened_by_name">Por: {{ session.opened_by_name }}</span>
    </div>

    <!-- Balance strip -->
    <div class="balance-strip">
      <div class="balance-card balance-blue">
        <div class="balance-label">Monto inicial</div>
        <div class="balance-value">{{ fmt(balance.monto_inicial) }}</div>
      </div>
      <div class="balance-card balance-green">
        <div class="balance-label">Ingresos</div>
        <div class="balance-value">{{ fmt(balance.ingresos) }}</div>
      </div>
      <div class="balance-card balance-red">
        <div class="balance-label">Egresos</div>
        <div class="balance-value">{{ fmt(balance.egresos) }}</div>
      </div>
      <div class="balance-card" :class="balance.caja_final >= 0 ? 'balance-blue' : 'balance-red'">
        <div class="balance-label">Caja final</div>
        <div class="balance-value">{{ fmt(balance.caja_final) }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <input v-model="search" @input="debouncedLoad" type="search" placeholder="Buscar descripción..." class="filter-input filter-search" />
      <select v-model="filters.type" @change="() => loadData(1)" class="filter-select">
        <option value="">Todos</option>
        <option value="income">Ingresos</option>
        <option value="expense">Egresos</option>
      </select>
      <select v-model="filters.category" @change="() => loadData(1)" class="filter-select">
        <option value="">Todas las categorías</option>
        <option v-for="c in categoryOpts" :key="c.value" :value="c.value">{{ c.label }}</option>
      </select>
      <input v-model="filters.fecha_inicio" @change="() => loadData(1)" type="date" class="filter-input" />
      <input v-model="filters.fecha_fin" @change="() => loadData(1)" type="date" class="filter-input" />
    </div>

    <div class="table-card">
      <div v-if="tableLoading" class="table-loading"><div class="spinner-lg"></div></div>
      <table v-else-if="items.length" class="data-table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th class="text-center">Tipo</th>
            <th>Categoría</th>
            <th>Descripción</th>
            <th class="text-right">Monto</th>
            <th class="text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td class="font-mono">{{ item.date }}</td>
            <td class="text-center">
              <span :class="item.type === 'income' ? 'badge badge-green' : 'badge badge-red'">
                {{ item.type === 'income' ? '↑ Ingreso' : '↓ Egreso' }}
              </span>
            </td>
            <td>{{ labelCategory(item.category) }}</td>
            <td>{{ item.description }}</td>
            <td class="text-right font-semibold" :style="{ color: item.type === 'income' ? '#059669' : '#dc2626' }">
              {{ item.type === 'income' ? '+' : '-' }}{{ fmt(item.amount) }}
            </td>
            <td class="text-center">
              <div class="row-actions">
                <button class="btn-icon btn-edit" @click="openEdit(item)">
                  <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                </button>
                <button class="btn-icon btn-delete" @click="confirmDelete(item)">
                  <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">
        <div class="empty-icon">💳</div>
        <p>No hay movimientos registrados.</p>
        <button class="btn-primary" @click="openCreate">Registrar primer movimiento</button>
      </div>
      <div v-if="count > 0" class="pagination">
        <span class="page-info">{{ paginationText }}</span>
        <div class="page-btns">
          <button :disabled="!prevUrl" @click="goPage(currentPage - 1)" class="page-btn">‹ Anterior</button>
          <button :disabled="!nextUrl" @click="goPage(currentPage + 1)" class="page-btn">Siguiente ›</button>
        </div>
      </div>
    </div>

    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h3 class="modal-title">{{ editingItem ? 'Editar movimiento' : 'Nuevo movimiento' }}</h3>
            <button class="modal-close" @click="closeModal">✕</button>
          </div>
          <form @submit.prevent="saveItem" class="modal-form">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Tipo *</label>
                <select v-model="form.type" class="form-input" required>
                  <option value="income">Ingreso</option>
                  <option value="expense">Egreso</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Fecha *</label>
                <input v-model="form.date" type="date" class="form-input" required />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Categoría *</label>
                <select v-model="form.category" class="form-input" required>
                  <option v-for="c in categoryOpts" :key="c.value" :value="c.value">{{ c.label }}</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Monto *</label>
                <input v-model.number="form.amount" type="number" step="0.01" min="0.01" class="form-input" required />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Descripción *</label>
              <input v-model="form.description" type="text" class="form-input" required placeholder="Detalle del movimiento..." />
            </div>
            <div class="form-group">
              <label class="form-label">Notas</label>
              <textarea v-model="form.notes" class="form-input form-textarea"></textarea>
            </div>
            <div v-if="formError" class="form-error">{{ formError }}</div>
            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="saving"><span v-if="saving" class="spinner-sm"></span>{{ editingItem ? 'Guardar' : 'Registrar' }}</button>
            </div>
          </form>
        </div>
      </div>

      <div v-if="showConfirm" class="modal-overlay" @click.self="showConfirm = false">
        <div class="modal modal-sm">
          <div class="modal-header"><h3 class="modal-title">Confirmar eliminación</h3><button class="modal-close" @click="showConfirm = false">✕</button></div>
          <p class="confirm-text">¿Eliminar este movimiento? Esta acción no se puede deshacer.</p>
          <div class="modal-footer">
            <button class="btn-secondary" @click="showConfirm = false">Cancelar</button>
            <button class="btn-danger" @click="deleteItem" :disabled="saving"><span v-if="saving" class="spinner-sm"></span>Eliminar</button>
          </div>
        </div>
      </div>

      <!-- Session modal — not closeable by clicking outside -->
      <div v-if="showSessionModal" class="modal-overlay">
        <div class="modal">
          <div class="modal-header">
            <h2 class="modal-title">Apertura de caja</h2>
          </div>
          <div class="modal-form">
            <p style="font-size:14px;color:#64748b;margin:0">Para comenzar el día, ingresa el monto inicial en caja.</p>
            <div class="form-group">
              <label class="form-label">Monto inicial *</label>
              <input v-model="sessionAmount" type="number" min="0" step="0.01" class="form-input" placeholder="0.00" required />
            </div>
            <div class="modal-actions">
              <button class="btn-primary" :disabled="savingSession || !sessionAmount" @click="openSession">
                <span v-if="savingSession" class="spinner"></span>
                <span v-else>Abrir caja</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()

interface Movement { id: number; type: string; category: string; description: string; amount: number; date: string; notes: string }
interface CashSession {
  id: number
  date: string
  opening_amount: number
  opened_by_name: string | null
  closed_at: string | null
  created_at: string
}

const items = ref<Movement[]>([])
const count = ref(0); const nextUrl = ref<string | null>(null); const prevUrl = ref<string | null>(null)
const currentPage = ref(1)
const tableLoading = ref(false); const saving = ref(false)
const search = ref(''); const filters = ref({ type: '', category: '', fecha_inicio: '', fecha_fin: '' })
const balance = ref({ monto_inicial: 0, ingresos: 0, egresos: 0, balance: 0, caja_final: 0 })
const session = ref<CashSession | null>(null)
const showSessionModal = ref(false)
const sessionAmount = ref('')
const savingSession = ref(false)
const showModal = ref(false); const showConfirm = ref(false)
const editingItem = ref<Movement | null>(null); const deletingItem = ref<Movement | null>(null)
const formError = ref('')

const categoryOpts = [
  { value: 'sale', label: 'Venta' }, { value: 'purchase', label: 'Compra' },
  { value: 'salary', label: 'Salario' }, { value: 'service', label: 'Servicio técnico' },
  { value: 'rent', label: 'Arriendo' }, { value: 'utility', label: 'Servicios básicos' },
  { value: 'other', label: 'Otro' },
]

const emptyForm = () => ({ type: 'income', category: 'other', description: '', amount: 0, date: new Date().toISOString().split('T')[0], notes: '' })
const form = ref(emptyForm())

const paginationText = computed(() => {
  const s = (currentPage.value - 1) * 20 + 1; const e = Math.min(currentPage.value * 20, count.value)
  return `${s}–${e} de ${count.value}`
})

function labelCategory(v: string) { return categoryOpts.find((c) => c.value === v)?.label ?? v }
function fmt(v: number) { return `$${Number(v || 0).toLocaleString('es-EC', { minimumFractionDigits: 2 })}` }

let debounceTimer: ReturnType<typeof setTimeout>
function debouncedLoad() { clearTimeout(debounceTimer); debounceTimer = setTimeout(() => loadData(), 400) }

async function loadData(page = 1) {
  tableLoading.value = true; currentPage.value = page
  const p = new URLSearchParams()
  if (search.value) p.set('search', search.value)
  if (filters.value.type) p.set('type', filters.value.type)
  if (filters.value.category) p.set('category', filters.value.category)
  if (filters.value.fecha_inicio) p.set('fecha_inicio', filters.value.fecha_inicio)
  if (filters.value.fecha_fin) p.set('fecha_fin', filters.value.fecha_fin)
  p.set('page', String(page))
  try {
    const [list, bal] = await Promise.all([
      api.get(`/cash/movements/?${p}`),
      api.get(`/cash/movements/balance/?${p}`),
    ])
    items.value = list.data.results; count.value = list.data.count
    nextUrl.value = list.data.next; prevUrl.value = list.data.previous
    balance.value = {
      monto_inicial: bal.data.monto_inicial ?? 0,
      ingresos: bal.data.ingresos ?? 0,
      egresos: bal.data.egresos ?? 0,
      balance: bal.data.balance ?? 0,
      caja_final: bal.data.caja_final ?? 0,
    }
  } catch { toast.error('Error al cargar movimientos') } finally { tableLoading.value = false }
}

function loadBalance() { loadData(currentPage.value) }

async function checkSession() {
  try {
    const { data } = await api.get('/cash/sessions/today/')
    session.value = data
  } catch {
    // No hay sesión hoy — mostrar modal de apertura
    showSessionModal.value = true
  }
}

async function openSession() {
  if (!sessionAmount.value || parseFloat(sessionAmount.value) < 0) return
  savingSession.value = true
  try {
    const { data } = await api.post('/cash/sessions/', {
      date: new Date().toISOString().split('T')[0],
      opening_amount: parseFloat(sessionAmount.value),
    })
    session.value = data
    showSessionModal.value = false
    loadBalance()
  } finally {
    savingSession.value = false
  }
}

function goPage(p: number) { loadData(p) }
function openCreate() { editingItem.value = null; form.value = emptyForm(); formError.value = ''; showModal.value = true }
function openEdit(item: Movement) { editingItem.value = item; form.value = { ...item }; formError.value = ''; showModal.value = true }
function closeModal() { showModal.value = false }
function confirmDelete(item: Movement) { deletingItem.value = item; showConfirm.value = true }

async function saveItem() {
  formError.value = ''; saving.value = true
  try {
    if (editingItem.value) { await api.put(`/cash/movements/${editingItem.value.id}/`, form.value); toast.success('Movimiento actualizado') }
    else { await api.post('/cash/movements/', form.value); toast.success('Movimiento registrado') }
    closeModal(); loadData(currentPage.value)
  } catch (e: any) { formError.value = e.response?.data?.detail || 'Error al guardar' }
  finally { saving.value = false }
}

async function deleteItem() {
  if (!deletingItem.value) return
  saving.value = true
  try { await api.delete(`/cash/movements/${deletingItem.value.id}/`); toast.success('Movimiento eliminado'); showConfirm.value = false; loadData(currentPage.value) }
  catch { toast.error('Error al eliminar') } finally { saving.value = false }
}

onMounted(() => { checkSession(); loadData() })
</script>

<style scoped>
@import '@/assets/crud.css';
.balance-strip { display: flex; gap: 14px; flex-wrap: wrap; }
.balance-card { flex: 1; min-width: 160px; padding: 18px 20px; border-radius: 12px; }
.balance-label { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.7; }
.balance-value { font-size: 24px; font-weight: 800; margin-top: 4px; }
.balance-green { background: #ecfdf5; color: #065f46; }
.balance-red   { background: #fef2f2; color: #991b1b; }
.balance-blue  { background: #eff6ff; color: #1e40af; }
.session-banner { display: flex; gap: 20px; padding: 10px 16px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 10px; font-size: 13px; color: #1d4ed8; flex-wrap: wrap; }
</style>
