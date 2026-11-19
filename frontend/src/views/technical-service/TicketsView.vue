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
                <button class="btn-icon btn-print" @click="openReceipt(item)" title="Imprimir recepción" aria-label="Imprimir recepción">
                  <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 9V2h12v7M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2m-2 0v4H8v-4h8z"/></svg>
                </button>
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

      <!-- Comprobante de recepción -->
      <div v-if="showReceipt && receiptTicket" class="modal-overlay" @click.self="closeReceipt">
        <div class="modal receipt-modal">
          <div class="modal-header">
            <h3 class="modal-title">Comprobante de recepción</h3>
            <button class="modal-close" @click="closeReceipt">✕</button>
          </div>

          <div class="receipt-preview">
            <div class="receipt-heading">
              <div>
                <p class="receipt-kicker">SERVICIO TÉCNICO</p>
                <h2>Comprobante de recepción</h2>
              </div>
              <div class="receipt-number">Ticket #{{ receiptTicket.id }}</div>
            </div>

            <div class="receipt-grid">
              <div><span>Cliente</span><strong>{{ receiptTicket.client_name }}</strong></div>
              <div><span>Teléfono</span><strong>{{ receiptTicket.client_phone || '—' }}</strong></div>
              <div><span>Fecha de recepción</span><strong>{{ receiptTicket.received_at }}</strong></div>
              <div><span>Fecha prometida</span><strong>{{ receiptTicket.promised_at || 'Por confirmar' }}</strong></div>
            </div>

            <div class="receipt-section">
              <span>Equipo / dispositivo</span>
              <strong>{{ receiptTicket.device }}</strong>
              <p v-if="receiptTicket.serial_number">N.º de serie: {{ receiptTicket.serial_number }}</p>
            </div>
            <div class="receipt-section">
              <span>Accesorios entregados</span>
              <p>{{ receiptTicket.accessories || 'No se registraron accesorios.' }}</p>
            </div>
            <div class="receipt-section">
              <span>Problema reportado</span>
              <p>{{ receiptTicket.problem }}</p>
            </div>
            <div v-if="receiptTicket.estimated_cost !== null" class="receipt-estimate">
              Costo estimado: <strong>{{ fmt(receiptTicket.estimated_cost) }}</strong>
            </div>

            <p class="receipt-note">El equipo se recibe en las condiciones descritas. El diagnóstico y el costo final serán comunicados antes de realizar reparaciones no autorizadas.</p>

            <div class="receipt-signatures">
              <div><span>Firma del cliente</span></div>
              <div><span>Recibido por</span></div>
            </div>
          </div>

          <div class="modal-footer receipt-actions">
            <button type="button" class="btn-secondary" @click="closeReceipt">
              Cerrar
            </button>

            <button
              type="button"
              class="btn-primary"
              @click="printReceipt('a5')"
            >
              <icon-placeholder />
              Imprimir A5
            </button>

            <button
              type="button"
              class="btn-secondary"
              @click="printReceipt('thermal-80')"
            >
              Ticket 80 mm
            </button>

            <button
              type="button"
              class="btn-secondary"
              @click="printReceipt('thermal-58')"
            >
              Ticket 58 mm
            </button>
          </div>
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
const showModal = ref(false); const showConfirm = ref(false); const showClientModal = ref(false); const showReceipt = ref(false)
const editingItem = ref<Ticket | null>(null); const deletingItem = ref<Ticket | null>(null)
const receiptTicket = ref<Ticket | null>(null)
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
function openReceipt(ticket: Ticket) { receiptTicket.value = ticket; showReceipt.value = true }
function closeReceipt() { showReceipt.value = false; receiptTicket.value = null }

function escapeHtml(value: string) {
  return value.replace(/[&<>"']/g, (character) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;',
  }[character] ?? character))
}

type ReceiptFormat = 'a5' | 'thermal-80' | 'thermal-58'

function formatReceiptDate(value?: string | null): string {
  if (!value) return '—'

  const datePart = value.substring(0, 10)
  const parts = datePart.split('-')

  if (parts.length !== 3) return value

  const [year, month, day] = parts
  return `${day}/${month}/${year}`
}

function printReceipt(format: ReceiptFormat = 'a5') {
  const ticket = receiptTicket.value

  if (!ticket) return

  const receiptWindow = window.open('', '_blank', 'width=900,height=700')

  if (!receiptWindow) {
    toast.error('El navegador bloqueó la ventana de impresión. Permite las ventanas emergentes e inténtalo nuevamente.')
    return
  }

  const escape = (value?: string | null) =>
    escapeHtml(value?.trim() || '—')

  const receivedDate = formatReceiptDate(ticket.received_at)
  const promisedDate = formatReceiptDate(ticket.promised_at)

  const estimatedCost = ticket.estimated_cost !== null
    ? `<div class="cost-row">
         <span>Costo estimado:</span>
         <strong>${fmt(ticket.estimated_cost)}</strong>
       </div>`
    : ''

  const isA5 = format === 'a5'
  const is80 = format === 'thermal-80'

  const pageStyle = isA5
    ? `
      @page {
        size: A5 landscape;
        margin: 5mm;
      }

      body {
        width: 200mm;
        min-height: 138mm;
        font-size: 10px;
      }

      .receipt {
        width: 100%;
      }

      .company-name {
        font-size: 25px;
      }

      .section-title {
        font-size: 10px;
      }

      .signatures {
        margin-top: 18mm;
      }
    `
    : `
      @page {
        size: ${is80 ? '80mm' : '58mm'} auto;
        margin: 3mm;
      }

      body {
        width: ${is80 ? '74mm' : '52mm'};
        font-size: ${is80 ? '11px' : '10px'};
      }

      .company-header {
        text-align: center;
        display: block;
      }

      .company-name {
        font-size: ${is80 ? '19px' : '16px'};
      }

      .company-info {
        text-align: center;
        margin-top: 5px;
      }

      .order-number {
        margin-top: 10px;
        text-align: center;
      }

      .data-grid {
        grid-template-columns: 1fr;
      }

      .signatures {
        margin-top: 30px;
      }
    `

  const html = `
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Orden de trabajo #${ticket.id}</title>

      <style>
        * {
          box-sizing: border-box;
        }

        body {
          margin: 0 auto;
          padding: 0;
          color: #000;
          font-family: Arial, Helvetica, sans-serif;
        }

        .receipt {
          width: 100%;
        }

        .company-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          border-bottom: 1.5px solid #000;
          padding-bottom: 8px;
        }

        .company-name {
          color: #c62828;
          font-weight: 900;
          margin: 0;
          font-family: Georgia, serif;
        }

        .company-info {
          font-size: 9px;
          line-height: 1.5;
          font-weight: 600;
          text-align: right;
        }

        .order-number {
          text-align: center;
          font-size: 17px;
          font-weight: 800;
          margin: 9px 0;
        }

        .data-grid {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          gap: 8px 15px;
          margin-bottom: 10px;
        }

        .field {
          border-bottom: 1px solid #000;
          min-height: 22px;
          padding-bottom: 3px;
        }

        .field-label {
          font-weight: 700;
          font-size: 9px;
          display: block;
          margin-bottom: 3px;
        }

        .field-value {
          font-size: 11px;
          font-weight: 600;
          overflow-wrap: anywhere;
        }

        .section-title {
          font-weight: 800;
          margin: 10px 0 5px;
          text-transform: uppercase;
        }

        .equipment-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 8px;
        }

        .content-box {
          border-bottom: 1px solid #000;
          padding: 5px 0;
          min-height: 27px;
          white-space: pre-wrap;
          overflow-wrap: anywhere;
        }

        .content-label {
          display: block;
          font-size: 9px;
          font-weight: 700;
          margin-bottom: 4px;
        }

        .content-value {
          font-size: 11px;
        }

        .cost-row {
          display: flex;
          justify-content: space-between;
          margin-top: 8px;
          font-weight: 700;
        }

        .conditions {
          margin-top: 10px;
          font-size: 9px;
          line-height: 1.4;
        }

        .conditions strong {
          display: block;
          margin-bottom: 4px;
        }

        .signatures {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 25px;
        }

        .signature {
          border-top: 1px solid #000;
          padding-top: 5px;
          text-align: center;
          font-size: 9px;
          font-weight: 700;
        }

        .thermal-divider {
          border-top: 1px dashed #000;
          margin: 8px 0;
        }

        .thermal-section {
          margin-top: 8px;
          overflow-wrap: anywhere;
        }

        .thermal-label {
          font-weight: 700;
          display: block;
          margin-bottom: 3px;
        }

        @media print {
          body {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
          }
        }

        ${pageStyle}
      </style>
    </head>

    <body>
      <div class="receipt">

        <header class="company-header">
          <h1 class="company-name">Magic World Computers</h1>

          <div class="company-info">
            Dirección: Tomás de Berlanga E8-43 y Av. Shyris<br>
            Teléfono: 6008553<br>
            Email: vero_meneses@hotmail.com
          </div>
        </header>

        <div class="order-number">
          ORDEN DE TRABAJO No. ${ticket.id}
        </div>

        <div class="data-grid">
          <div class="field">
            <span class="field-label">Cliente:</span>
            <span class="field-value">${escape(ticket.client_name)}</span>
          </div>

          <div class="field">
            <span class="field-label">Teléfono:</span>
            <span class="field-value">${escape(ticket.client_phone)}</span>
          </div>

          <div class="field">
            <span class="field-label">Fecha recepción:</span>
            <span class="field-value">${receivedDate}</span>
          </div>

          <div class="field">
            <span class="field-label">Equipo:</span>
            <span class="field-value">${escape(ticket.device)}</span>
          </div>

          <div class="field">
            <span class="field-label">Número de serie:</span>
            <span class="field-value">${escape(ticket.serial_number)}</span>
          </div>

          <div class="field">
            <span class="field-label">Fecha prometida:</span>
            <span class="field-value">${promisedDate}</span>
          </div>
        </div>

        <div class="section-title">Accesorios entregados:</div>

        <div class="content-box">
          <span class="content-value">${escape(ticket.accessories)}</span>
        </div>

        <div class="section-title">Problema reportado:</div>

        <div class="content-box">
          <span class="content-value">${escape(ticket.problem)}</span>
        </div>

        ${estimatedCost}

        <div class="conditions">
          <strong>IMPORTANTE:</strong>
          El equipo se recibe para diagnóstico y/o servicio técnico.
          Cualquier reparación adicional será comunicada al cliente
          antes de realizarse.
        </div>

        <div class="signatures">
          <div class="signature">FIRMA DEL CLIENTE</div>
          <div class="signature">RECIBIDO POR</div>
        </div>

      </div>

      <script>
        window.onload = () => {
          window.focus();
          window.print();
        };

        window.onafterprint = () => {
          window.close();
        };
      <\/script>
    </body>
    </html>
  `

  receiptWindow.document.open()
  receiptWindow.document.write(html)
  receiptWindow.document.close()
}

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
      const response = await api.post('/technical-service/tickets/', form.value)
      openReceipt(response.data)
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
.btn-print { background: #ecfdf5; color: #059669; }
.btn-print:hover { background: #d1fae5; }
.receipt-modal { max-width: 680px; }
.receipt-preview { margin: 16px 24px; color: #0f172a; }
.receipt-heading { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; border-bottom: 2px solid #2563eb; padding-bottom: 14px; }
.receipt-heading h2 { margin: 0; font-size: 20px; }
.receipt-kicker { margin: 0 0 5px; color: #2563eb; font-size: 11px; font-weight: 700; letter-spacing: .08em; }
.receipt-number { color: #2563eb; font-size: 14px; font-weight: 700; white-space: nowrap; }
.receipt-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px 20px; margin: 18px 0; }
.receipt-grid span, .receipt-section > span { display: block; color: #64748b; font-size: 11px; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; }
.receipt-grid strong { display: block; margin-top: 4px; color: #374151; font-size: 14px; }
.receipt-section { margin-top: 10px; padding: 12px 14px; border: 1px solid #e2e8f0; border-radius: 8px; }
.receipt-section strong { display: block; margin-top: 5px; }
.receipt-section p { margin: 6px 0 0; color: #374151; line-height: 1.45; white-space: pre-wrap; }
.receipt-estimate { margin-top: 14px; color: #374151; font-size: 14px; text-align: right; }
.receipt-estimate strong { color: #2563eb; font-size: 16px; }
.receipt-note { margin: 22px 0 0; color: #64748b; font-size: 12px; line-height: 1.5; }
.receipt-signatures { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-top: 52px; }
.receipt-signatures div { border-top: 1px solid #64748b; padding-top: 7px; color: #64748b; font-size: 12px; text-align: center; }
.receipt-actions { padding: 0 24px 24px; }
.receipt-actions { display: flex; flex-wrap: wrap; justify-content: flex-end; gap: 8px; }
.receipt-modal { max-width: 850px; }
@media (max-width: 560px) { .receipt-grid { grid-template-columns: 1fr; } .receipt-signatures { gap: 18px; } }
</style>
