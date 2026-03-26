<template>
  <div class="view">
    <div class="view-header">
      <div>
        <h2 class="view-title">Servicio Técnico</h2>
        <p class="view-sub">Gestión de tickets de servicio y reparación</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        Nuevo ticket
      </button>
    </div>

    <!-- Status counters -->
    <div class="status-counters">
      <div v-for="s in statusSummary" :key="s.status" class="status-counter" :class="`sc-${s.status}`">
        <div class="sc-count">{{ s.total }}</div>
        <div class="sc-label">{{ statusLabel(s.status) }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <input v-model="search" @input="debouncedLoad" type="search" placeholder="Buscar cliente, equipo..." class="filter-input filter-search" />
      <select v-model="filters.status" @change="() => loadData(1)" class="filter-select">
        <option value="">Todos los estados</option>
        <option v-for="s in statusOpts" :key="s.value" :value="s.value">{{ s.label }}</option>
      </select>
      <select v-model="filters.priority" @change="() => loadData(1)" class="filter-select">
        <option value="">Todas las prioridades</option>
        <option v-for="p in priorityOpts" :key="p.value" :value="p.value">{{ p.label }}</option>
      </select>
    </div>

    <div class="table-card">
      <div v-if="tableLoading" class="table-loading"><div class="spinner-lg"></div></div>
      <table v-else-if="items.length" class="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Cliente</th>
            <th>Equipo</th>
            <th>Problema</th>
            <th class="text-center">Prioridad</th>
            <th class="text-center">Estado</th>
            <th class="text-right">Costo</th>
            <th>Recibido</th>
            <th class="text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td class="font-mono" style="color:#94a3b8">#{{ item.id }}</td>
            <td>
              <div style="font-weight:600">{{ item.client_name }}</div>
              <div style="font-size:12px;color:#94a3b8">{{ item.client_phone }}</div>
            </td>
            <td>
              <div>{{ item.device }}</div>
              <div v-if="item.serial_number" style="font-size:12px;color:#94a3b8">S/N: {{ item.serial_number }}</div>
            </td>
            <td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ item.problem }}</td>
            <td class="text-center"><span :class="priorityBadge(item.priority)">{{ priorityLabel(item.priority) }}</span></td>
            <td class="text-center"><span :class="statusBadge(item.status)">{{ statusLabel(item.status) }}</span></td>
            <td class="text-right">{{ item.final_cost ? fmt(item.final_cost) : item.estimated_cost ? `~${fmt(item.estimated_cost)}` : '—' }}</td>
            <td class="font-mono">{{ item.received_at }}</td>
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
        <div class="empty-icon">🔧</div>
        <p>No hay tickets de servicio.</p>
        <button class="btn-primary" @click="openCreate">Crear primer ticket</button>
      </div>
      <div v-if="count > 0" class="pagination">
        <span class="page-info">{{ paginationText }}</span>
        <div class="page-btns">
          <button :disabled="!prevUrl" @click="goPage(currentPage - 1)" class="page-btn">‹ Anterior</button>
          <button :disabled="!nextUrl" @click="goPage(currentPage + 1)" class="page-btn">Siguiente ›</button>
        </div>
      </div>
    </div>

    <!-- Main modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal" style="max-width:720px">
          <div class="modal-header">
            <h3 class="modal-title">{{ editingItem ? `Ticket #${editingItem.id}` : 'Nuevo ticket de servicio' }}</h3>
            <button class="modal-close" @click="closeModal">✕</button>
          </div>
          <form @submit.prevent="saveItem" class="modal-form">

            <!-- Sección cliente -->
            <div class="form-section-title">Cliente *</div>
            <div class="form-group">
              <label class="form-label">Seleccionar cliente *</label>
              <div style="display:flex;gap:8px;align-items:center">
                <select v-model="form.client" class="form-input" required @change="onClientSelect" style="flex:1">
                  <option :value="null" disabled>-- Seleccione un cliente --</option>
                  <option v-for="c in clients" :key="c.id" :value="c.id">
                    {{ c.first_name }} {{ c.last_name }} — {{ c.phone || c.username }}
                  </option>
                </select>
                <button type="button" class="btn-secondary" style="white-space:nowrap" @click="openCreateClient">
                  + Nuevo cliente
                </button>
              </div>
            </div>
            <div v-if="selectedClientInfo" class="client-info-box">
              <span><strong>Nombre:</strong> {{ selectedClientInfo.first_name }} {{ selectedClientInfo.last_name }}</span>
              <span v-if="selectedClientInfo.phone"><strong>Tel:</strong> {{ selectedClientInfo.phone }}</span>
              <span v-if="selectedClientInfo.email"><strong>Email:</strong> {{ selectedClientInfo.email }}</span>
            </div>

            <!-- Sección equipo -->
            <div class="form-section-title">Equipo</div>
            <div class="form-row">
              <div class="form-group"><label class="form-label">Equipo / Dispositivo *</label><input v-model="form.device" type="text" class="form-input" required /></div>
              <div class="form-group"><label class="form-label">N° de serie</label><input v-model="form.serial_number" type="text" class="form-input" /></div>
            </div>
            <div class="form-group"><label class="form-label">Accesorios entregados</label><input v-model="form.accessories" type="text" class="form-input" /></div>

            <!-- Sección técnica -->
            <div class="form-section-title">Diagnóstico</div>
            <div class="form-group"><label class="form-label">Problema reportado *</label><textarea v-model="form.problem" class="form-input form-textarea" required></textarea></div>
            <div class="form-group"><label class="form-label">Diagnóstico técnico</label><textarea v-model="form.diagnosis" class="form-input form-textarea"></textarea></div>
            <div class="form-group"><label class="form-label">Solución aplicada</label><textarea v-model="form.solution" class="form-input form-textarea"></textarea></div>

            <!-- Estado y costos -->
            <div class="form-section-title">Estado y costos</div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Estado</label>
                <select v-model="form.status" class="form-input">
                  <option v-for="s in statusOpts" :key="s.value" :value="s.value">{{ s.label }}</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Prioridad</label>
                <select v-model="form.priority" class="form-input">
                  <option v-for="p in priorityOpts" :key="p.value" :value="p.value">{{ p.label }}</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group"><label class="form-label">Costo estimado</label><input v-model.number="form.estimated_cost" type="number" step="0.01" min="0" class="form-input" /></div>
              <div class="form-group"><label class="form-label">Costo final</label><input v-model.number="form.final_cost" type="number" step="0.01" min="0" class="form-input" /></div>
            </div>
            <div class="form-row">
              <div class="form-group"><label class="form-label">Fecha prometida</label><input v-model="form.promised_at" type="date" class="form-input" /></div>
              <div class="form-group"><label class="form-label">Fecha de entrega</label><input v-model="form.completed_at" type="date" class="form-input" /></div>
            </div>

            <div v-if="formError" class="form-error">{{ formError }}</div>
            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="saving"><span v-if="saving" class="spinner-sm"></span>{{ editingItem ? 'Guardar cambios' : 'Crear ticket' }}</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Quick create client modal -->
      <div v-if="showClientModal" class="modal-overlay" @click.self="showClientModal = false">
        <div class="modal" style="max-width:480px">
          <div class="modal-header">
            <h3 class="modal-title">Nuevo cliente</h3>
            <button class="modal-close" @click="showClientModal = false">✕</button>
          </div>
          <form @submit.prevent="saveNewClient" class="modal-form">
            <div class="form-row">
              <div class="form-group"><label class="form-label">Nombre *</label><input v-model="clientForm.first_name" type="text" class="form-input" required /></div>
              <div class="form-group"><label class="form-label">Apellido *</label><input v-model="clientForm.last_name" type="text" class="form-input" required /></div>
            </div>
            <div class="form-row">
              <div class="form-group"><label class="form-label">Cédula</label><input v-model="clientForm.cedula" type="text" class="form-input" /></div>
              <div class="form-group"><label class="form-label">Teléfono *</label><input v-model="clientForm.phone" type="text" class="form-input" required /></div>
            </div>
            <div class="form-group"><label class="form-label">Email</label><input v-model="clientForm.email" type="email" class="form-input" /></div>
            <div v-if="clientFormError" class="form-error">{{ clientFormError }}</div>
            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="showClientModal = false">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="savingClient"><span v-if="savingClient" class="spinner-sm"></span>Crear cliente</button>
            </div>
          </form>
        </div>
      </div>

      <!-- Delete confirm -->
      <div v-if="showConfirm" class="modal-overlay" @click.self="showConfirm = false">
        <div class="modal modal-sm">
          <div class="modal-header"><h3 class="modal-title">Confirmar eliminación</h3><button class="modal-close" @click="showConfirm = false">✕</button></div>
          <p class="confirm-text">¿Eliminar el ticket #{{ deletingItem?.id }}? Esta acción no se puede deshacer.</p>
          <div class="modal-footer">
            <button class="btn-secondary" @click="showConfirm = false">Cancelar</button>
            <button class="btn-danger" @click="deleteItem" :disabled="saving"><span v-if="saving" class="spinner-sm"></span>Eliminar</button>
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

interface Ticket {
  id: number; client: number | null
  client_name: string; client_phone: string; client_email: string
  device: string; serial_number: string; accessories: string
  problem: string; diagnosis: string; solution: string
  estimated_cost: number | null; final_cost: number | null
  status: string; priority: string; received_at: string; promised_at: string | null; completed_at: string | null
}

interface Client {
  id: number; username: string; first_name: string; last_name: string
  phone: string; email: string; cedula: string
}

const items = ref<Ticket[]>([])
const clients = ref<Client[]>([])
const statusSummary = ref<Array<{ status: string; total: number }>>([])
const count = ref(0); const nextUrl = ref<string | null>(null); const prevUrl = ref<string | null>(null)
const currentPage = ref(1)
const tableLoading = ref(false); const saving = ref(false); const savingClient = ref(false)
const search = ref(''); const filters = ref({ status: '', priority: '' })
const showModal = ref(false); const showConfirm = ref(false); const showClientModal = ref(false)
const editingItem = ref<Ticket | null>(null); const deletingItem = ref<Ticket | null>(null)
const formError = ref(''); const clientFormError = ref('')

const statusOpts = [
  { value: 'pending', label: 'Pendiente' }, { value: 'in_progress', label: 'En proceso' },
  { value: 'waiting_parts', label: 'Esperando repuestos' }, { value: 'completed', label: 'Completado' },
  { value: 'delivered', label: 'Entregado' }, { value: 'cancelled', label: 'Cancelado' },
]
const priorityOpts = [
  { value: 'low', label: 'Baja' }, { value: 'medium', label: 'Media' },
  { value: 'high', label: 'Alta' }, { value: 'urgent', label: 'Urgente' },
]

interface TicketForm {
  client: number | null; device: string; serial_number: string; accessories: string
  problem: string; diagnosis: string; solution: string
  estimated_cost: number | null; final_cost: number | null
  status: string; priority: string; promised_at: string | null; completed_at: string | null
}

const emptyForm = (): TicketForm => ({
  client: null, device: '', serial_number: '', accessories: '',
  problem: '', diagnosis: '', solution: '',
  estimated_cost: null, final_cost: null, status: 'pending', priority: 'medium',
  promised_at: null, completed_at: null,
})
const form = ref<TicketForm>(emptyForm())

const emptyClientForm = () => ({ first_name: '', last_name: '', cedula: '', phone: '', email: '' })
const clientForm = ref(emptyClientForm())

const selectedClientInfo = computed(() => {
  if (!form.value.client) return null
  return clients.value.find(c => c.id === form.value.client) ?? null
})

const paginationText = computed(() => {
  const s = (currentPage.value - 1) * 20 + 1; const e = Math.min(currentPage.value * 20, count.value)
  return `${s}–${e} de ${count.value}`
})

function statusLabel(s: string) { return statusOpts.find((o) => o.value === s)?.label ?? s }
function priorityLabel(s: string) { return priorityOpts.find((o) => o.value === s)?.label ?? s }
function statusBadge(s: string) {
  return { pending: 'badge badge-gray', in_progress: 'badge badge-blue', waiting_parts: 'badge badge-orange',
    completed: 'badge badge-green', delivered: 'badge badge-purple', cancelled: 'badge badge-red' }[s] ?? 'badge badge-gray'
}
function priorityBadge(s: string) {
  return { low: 'badge badge-gray', medium: 'badge badge-blue', high: 'badge badge-orange', urgent: 'badge badge-red' }[s] ?? 'badge badge-gray'
}
function fmt(v: number) { return `$${Number(v || 0).toLocaleString('es-EC', { minimumFractionDigits: 2 })}` }
function onClientSelect() { /* selectedClientInfo computed auto-updates */ }

let debounceTimer: ReturnType<typeof setTimeout>
function debouncedLoad() { clearTimeout(debounceTimer); debounceTimer = setTimeout(() => loadData(), 400) }

async function loadData(page = 1) {
  tableLoading.value = true; currentPage.value = page
  const p = new URLSearchParams()
  if (search.value) p.set('search', search.value)
  if (filters.value.status) p.set('status', filters.value.status)
  if (filters.value.priority) p.set('priority', filters.value.priority)
  p.set('page', String(page))
  try {
    const [list, summary] = await Promise.all([
      api.get(`/technical-service/tickets/?${p}`),
      api.get('/technical-service/tickets/resumen/'),
    ])
    items.value = list.data.results; count.value = list.data.count
    nextUrl.value = list.data.next; prevUrl.value = list.data.previous
    statusSummary.value = summary.data
  } catch { toast.error('Error al cargar tickets') } finally { tableLoading.value = false }
}

async function loadClients() {
  try {
    const res = await api.get('/users/?role=client&page_size=1000')
    clients.value = res.data.results ?? res.data
  } catch { /* silently fail */ }
}

function goPage(p: number) { loadData(p) }

function openCreate() {
  editingItem.value = null; form.value = emptyForm(); formError.value = ''; showModal.value = true
}
function openEdit(item: Ticket) {
  editingItem.value = item
  form.value = {
    client: item.client, device: item.device, serial_number: item.serial_number,
    accessories: item.accessories, problem: item.problem, diagnosis: item.diagnosis,
    solution: item.solution, estimated_cost: item.estimated_cost, final_cost: item.final_cost,
    status: item.status, priority: item.priority, promised_at: item.promised_at, completed_at: item.completed_at,
  }
  formError.value = ''; showModal.value = true
}
function closeModal() { showModal.value = false }
function confirmDelete(item: Ticket) { deletingItem.value = item; showConfirm.value = true }

function openCreateClient() {
  clientForm.value = emptyClientForm(); clientFormError.value = ''; showClientModal.value = true
}

async function saveNewClient() {
  clientFormError.value = ''; savingClient.value = true
  try {
    const payload = { ...clientForm.value, role: 'client', password: `Temp${clientForm.value.cedula || '1234'}!` }
    const res = await api.post('/users/', payload)
    const newClient: Client = res.data
    clients.value.push(newClient)
    form.value.client = newClient.id
    showClientModal.value = false
    toast.success('Cliente creado')
  } catch (e: any) {
    const d = e.response?.data
    clientFormError.value = typeof d === 'string' ? d : Object.values(d || {}).flat().join(' ') || 'Error al crear cliente'
  } finally { savingClient.value = false }
}

async function saveItem() {
  formError.value = ''; saving.value = true
  try {
    if (editingItem.value) {
      await api.put(`/technical-service/tickets/${editingItem.value.id}/`, form.value)
      toast.success('Ticket actualizado')
    } else {
      await api.post('/technical-service/tickets/', form.value)
      toast.success('Ticket creado')
    }
    closeModal(); loadData(currentPage.value)
  } catch (e: any) {
    const d = e.response?.data
    formError.value = typeof d === 'string' ? d : d?.detail || Object.values(d || {}).flat().join(' ') || 'Error al guardar'
  } finally { saving.value = false }
}

async function deleteItem() {
  if (!deletingItem.value) return
  saving.value = true
  try {
    await api.delete(`/technical-service/tickets/${deletingItem.value.id}/`)
    toast.success('Ticket eliminado'); showConfirm.value = false; loadData(currentPage.value)
  } catch { toast.error('Error al eliminar') } finally { saving.value = false }
}

onMounted(() => { loadData(); loadClients() })
</script>

<style scoped>
@import '@/assets/crud.css';
.status-counters { display: flex; gap: 10px; flex-wrap: wrap; }
.status-counter { padding: 12px 16px; border-radius: 10px; min-width: 100px; text-align: center; background: white; border: 1px solid #f1f5f9; }
.sc-count { font-size: 22px; font-weight: 800; color: #0f172a; }
.sc-label { font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; margin-top: 2px; }
.sc-pending       { border-left: 3px solid #94a3b8; }
.sc-in_progress   { border-left: 3px solid #2563eb; }
.sc-waiting_parts { border-left: 3px solid #d97706; }
.sc-completed     { border-left: 3px solid #059669; }
.sc-delivered     { border-left: 3px solid #7c3aed; }
.sc-cancelled     { border-left: 3px solid #dc2626; }
.form-section-title { font-size: 13px; font-weight: 700; color: #2563eb; text-transform: uppercase; letter-spacing: 0.05em; padding-bottom: 4px; border-bottom: 1px solid #e2e8f0; margin-top: 4px; }
.client-info-box { display: flex; gap: 16px; flex-wrap: wrap; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; font-size: 13px; color: #475569; margin-top: -4px; }
</style>
