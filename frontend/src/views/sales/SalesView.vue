<template>
  <div class="view">
    <!-- Header -->
    <div class="view-header">
      <div>
        <h2 class="view-title">Ventas</h2>
        <p class="view-sub">Registro y seguimiento de todas las ventas</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        Nueva venta
      </button>
    </div>

    <!-- Stats strip -->
    <div class="stats-strip">
      <div class="stat-pill">
        <span class="stat-label">Total período</span>
        <span class="stat-value">{{ fmt(summary.total) }}</span>
      </div>
      <div class="stat-pill">
        <span class="stat-label">Transacciones</span>
        <span class="stat-value">{{ summary.transacciones }}</span>
      </div>
      <div class="stat-pill">
        <span class="stat-label">Promedio</span>
        <span class="stat-value">{{ fmt(summary.promedio) }}</span>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <input v-model="filters.fecha_inicio" @change="() => loadData(1)" type="date" class="filter-input" />
      <input v-model="filters.fecha_fin" @change="() => loadData(1)" type="date" class="filter-input" />
      <select v-model="filters.metodo_pago" @change="() => loadData(1)" class="filter-select">
        <option value="">Todos los métodos</option>
        <option v-for="m in metodoPagoOpts" :key="m.value" :value="m.value">{{ m.label }}</option>
      </select>
      <button v-if="hasFilters" @click="clearFilters" class="btn-clear">Limpiar</button>
    </div>

    <!-- Table -->
    <div class="table-card">
      <div v-if="tableLoading" class="table-loading">
        <div class="spinner-lg"></div>
      </div>
      <table v-else-if="items.length" class="data-table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Cliente</th>
            <th class="text-center">Ítems</th>
            <th class="text-right">Total</th>
            <th>Método de pago</th>
            <th class="text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td class="font-mono">{{ item.fecha_venta }}</td>
            <td>{{ item.client_name || '—' }}</td>
            <td class="text-center">{{ item.items?.length ?? 0 }}</td>
            <td class="text-right font-semibold">{{ fmt(item.total) }}</td>
            <td><span class="badge badge-blue">{{ labelMetodo(item.metodo_pago) }}</span></td>
            <td class="text-center">
              <div class="row-actions">
                <button class="btn-icon btn-edit" @click="openEdit(item)" title="Editar">
                  <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                  </svg>
                </button>
                <button class="btn-icon btn-delete" @click="confirmDelete(item)" title="Eliminar">
                  <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-else class="empty-state">
        <div class="empty-icon">📊</div>
        <p>No hay ventas registradas para este período.</p>
        <button class="btn-primary" @click="openCreate">Registrar primera venta</button>
      </div>

      <!-- Pagination -->
      <div v-if="count > 0" class="pagination">
        <span class="page-info">{{ paginationText }}</span>
        <div class="page-btns">
          <button :disabled="!prevUrl" @click="goPage(currentPage - 1)" class="page-btn">‹ Anterior</button>
          <button :disabled="!nextUrl" @click="goPage(currentPage + 1)" class="page-btn">Siguiente ›</button>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal modal-wide">
          <div class="modal-header">
            <h3 class="modal-title">{{ editingItem ? 'Editar venta' : 'Nueva venta' }}</h3>
            <button class="modal-close" @click="closeModal">✕</button>
          </div>
          <form @submit.prevent="saveItem" class="modal-form">

            <!-- Cabecera de venta -->
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Fecha *</label>
                <input v-model="form.fecha_venta" type="date" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">Método de pago *</label>
                <select v-model="form.metodo_pago" class="form-input" required>
                  <option v-for="m in metodoPagoOpts" :key="m.value" :value="m.value">{{ m.label }}</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Cliente (opcional)</label>
                <select v-model="form.client" class="form-input">
                  <option :value="null">Sin cliente asignado</option>
                  <option v-for="c in clients" :key="c.id" :value="c.id">
                    {{ c.first_name }} {{ c.last_name }} — {{ c.phone || c.username }}
                  </option>
                </select>
              </div>
              <div class="form-group" style="justify-content:flex-end;padding-bottom:4px">
                <label class="check-label" style="margin-top:auto">
                  <input type="checkbox" v-model="form.es_feriado" />
                  Es feriado
                </label>
              </div>
            </div>

            <!-- Ítems de venta -->
            <div class="items-section">
              <div class="items-header">
                <span class="items-title">Productos / Servicios</span>
                <button type="button" class="btn-add-item" @click="addItem">+ Agregar ítem</button>
              </div>

              <div v-if="form.items.length === 0" class="items-empty">
                Agrega al menos un producto o servicio para registrar la venta.
              </div>

              <div v-else class="items-table-wrapper">
                <table class="items-table">
                  <thead>
                    <tr>
                      <th>Producto (opcional)</th>
                      <th>Descripción *</th>
                      <th style="width:70px">Cant.</th>
                      <th style="width:110px">Precio unit.</th>
                      <th style="width:110px">Subtotal</th>
                      <th style="width:36px"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(it, idx) in form.items" :key="idx">
                      <td>
                        <select v-model="it.product" class="form-input form-input--sm" @change="onProductSelect(idx)">
                          <option :value="null">— Libre —</option>
                          <option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</option>
                        </select>
                      </td>
                      <td>
                        <input v-model="it.description" class="form-input form-input--sm" placeholder="Descripción..." required />
                      </td>
                      <td>
                        <input v-model.number="it.quantity" type="number" min="1" class="form-input form-input--sm" @input="calcSubtotal(idx)" required />
                      </td>
                      <td>
                        <input v-model.number="it.unit_price" type="number" step="0.01" min="0" class="form-input form-input--sm" @input="calcSubtotal(idx)" required />
                      </td>
                      <td class="subtotal-cell">{{ fmt(it.subtotal) }}</td>
                      <td>
                        <button type="button" class="btn-remove-item" @click="removeItem(idx)" title="Quitar">✕</button>
                      </td>
                    </tr>
                  </tbody>
                  <tfoot>
                    <tr>
                      <td colspan="4" class="total-label">Total</td>
                      <td class="total-value">{{ fmt(computedTotal) }}</td>
                      <td></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>

            <div v-if="formError" class="form-error">{{ formError }}</div>
            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="saving || form.items.length === 0">
                <span v-if="saving" class="spinner-sm"></span>
                {{ editingItem ? 'Guardar cambios' : 'Registrar venta' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Confirm delete -->
      <div v-if="showConfirm" class="modal-overlay" @click.self="showConfirm = false">
        <div class="modal modal-sm">
          <div class="modal-header">
            <h3 class="modal-title">Confirmar eliminación</h3>
            <button class="modal-close" @click="showConfirm = false">✕</button>
          </div>
          <p class="confirm-text">¿Estás seguro de eliminar esta venta? Esta acción no se puede deshacer.</p>
          <div class="modal-footer">
            <button class="btn-secondary" @click="showConfirm = false">Cancelar</button>
            <button class="btn-danger" @click="deleteItem" :disabled="saving">
              <span v-if="saving" class="spinner-sm"></span>
              Eliminar
            </button>
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

interface VentaItem {
  id?: number
  product: number | null
  description: string
  quantity: number
  unit_price: number
  subtotal: number
}

interface Venta {
  id: number
  client: number | null
  client_name: string | null
  fecha_venta: string
  total: number
  metodo_pago: string
  es_feriado: boolean
  items: VentaItem[]
}

interface ClientUser {
  id: number
  username: string
  first_name: string
  last_name: string
  phone: string
}

interface Product {
  id: number
  name: string
  price: number
}

const items = ref<Venta[]>([])
const count = ref(0)
const nextUrl = ref<string | null>(null)
const prevUrl = ref<string | null>(null)
const currentPage = ref(1)
const tableLoading = ref(false)
const saving = ref(false)
const showModal = ref(false)
const showConfirm = ref(false)
const editingItem = ref<Venta | null>(null)
const deletingItem = ref<Venta | null>(null)
const formError = ref('')

const summary = ref({ total: 0, transacciones: 0, promedio: 0 })
const filters = ref({ fecha_inicio: '', fecha_fin: '', metodo_pago: '' })

const clients = ref<ClientUser[]>([])
const products = ref<Product[]>([])

const metodoPagoOpts = [
  { value: 'efectivo', label: 'Efectivo' },
  { value: 'transferencia', label: 'Transferencia' },
  { value: 'deuna', label: 'DeUna' },
  { value: 'tarjeta', label: 'Tarjeta' },
  { value: 'otro', label: 'Otro' },
]

const emptyForm = () => ({
  fecha_venta: new Date().toISOString().split('T')[0],
  metodo_pago: 'efectivo',
  client: null as number | null,
  es_feriado: false,
  items: [] as VentaItem[],
})
const form = ref(emptyForm())

const computedTotal = computed(() =>
  form.value.items.reduce((acc, it) => acc + it.subtotal, 0),
)

const hasFilters = computed(() =>
  !!filters.value.fecha_inicio || !!filters.value.fecha_fin || !!filters.value.metodo_pago,
)
const paginationText = computed(() => {
  const start = (currentPage.value - 1) * 20 + 1
  const end = Math.min(currentPage.value * 20, count.value)
  return `${start}–${end} de ${count.value}`
})

function addItem() {
  form.value.items.push({ product: null, description: '', quantity: 1, unit_price: 0, subtotal: 0 })
}

function removeItem(idx: number) {
  form.value.items.splice(idx, 1)
}

function calcSubtotal(idx: number) {
  const it = form.value.items[idx]
  it.subtotal = (it.quantity || 0) * (it.unit_price || 0)
}

function onProductSelect(idx: number) {
  const it = form.value.items[idx]
  const prod = products.value.find(p => p.id === it.product)
  if (prod) {
    it.description = prod.name
    it.unit_price = prod.price
    calcSubtotal(idx)
  }
}

async function loadData(page = 1) {
  tableLoading.value = true
  currentPage.value = page
  const params = new URLSearchParams()
  if (filters.value.fecha_inicio) params.set('fecha_inicio', filters.value.fecha_inicio)
  if (filters.value.fecha_fin) params.set('fecha_fin', filters.value.fecha_fin)
  if (filters.value.metodo_pago) params.set('metodo_pago', filters.value.metodo_pago)
  params.set('page', String(page))
  try {
    const [list, sum] = await Promise.all([
      api.get(`/sales/ventas/?${params}`),
      api.get(`/sales/ventas/resumen/?${params}`),
    ])
    items.value = list.data.results
    count.value = list.data.count
    nextUrl.value = list.data.next
    prevUrl.value = list.data.previous
    summary.value = sum.data
  } catch {
    toast.error('Error al cargar ventas')
  } finally {
    tableLoading.value = false
  }
}

async function loadAuxData() {
  const [cli, prods] = await Promise.all([
    api.get('/users/?role=client&page_size=200').catch(() => ({ data: { results: [] } })),
    api.get('/inventory/products/?is_active=true&page_size=200').catch(() => ({ data: { results: [] } })),
  ])
  clients.value = Array.isArray(cli.data) ? cli.data : (cli.data.results ?? [])
  products.value = Array.isArray(prods.data) ? prods.data : (prods.data.results ?? [])
}

function goPage(p: number) { loadData(p) }

function fmt(v: number) {
  return `$${Number(v || 0).toLocaleString('es-EC', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function labelMetodo(v: string) {
  return metodoPagoOpts.find((m) => m.value === v)?.label ?? v
}

function clearFilters() {
  filters.value = { fecha_inicio: '', fecha_fin: '', metodo_pago: '' }
  loadData()
}

function openCreate() {
  editingItem.value = null
  form.value = emptyForm()
  formError.value = ''
  showModal.value = true
}

function openEdit(item: Venta) {
  editingItem.value = item
  form.value = {
    fecha_venta: item.fecha_venta,
    metodo_pago: item.metodo_pago,
    client: item.client,
    es_feriado: item.es_feriado,
    items: (item.items ?? []).map(it => ({ ...it, subtotal: it.subtotal })),
  }
  formError.value = ''
  showModal.value = true
}

function closeModal() { showModal.value = false }

function confirmDelete(item: Venta) {
  deletingItem.value = item
  showConfirm.value = true
}

async function saveItem() {
  if (form.value.items.length === 0) {
    formError.value = 'Agrega al menos un ítem a la venta.'
    return
  }
  formError.value = ''
  saving.value = true
  try {
    const payload = {
      ...form.value,
      total: computedTotal.value,
    }
    if (editingItem.value) {
      await api.put(`/sales/ventas/${editingItem.value.id}/`, payload)
      toast.success('Venta actualizada correctamente')
    } else {
      await api.post('/sales/ventas/', payload)
      toast.success('Venta registrada correctamente')
    }
    closeModal()
    loadData(currentPage.value)
  } catch (e: any) {
    const err = e.response?.data
    if (typeof err === 'object') {
      formError.value = Object.values(err).flat().join(' ')
    } else {
      formError.value = 'Error al guardar. Verifica los datos.'
    }
  } finally {
    saving.value = false
  }
}

async function deleteItem() {
  if (!deletingItem.value) return
  saving.value = true
  try {
    await api.delete(`/sales/ventas/${deletingItem.value.id}/`)
    toast.success('Venta eliminada')
    showConfirm.value = false
    loadData(currentPage.value)
  } catch {
    toast.error('Error al eliminar la venta')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadData()
  loadAuxData()
})
</script>

<style scoped>
@import '@/assets/crud.css';

.modal-wide { max-width: 820px; }

.items-section { border: 1.5px solid #e2e8f0; border-radius: 12px; overflow: hidden; }
.items-header { display: flex; justify-content: space-between; align-items: center; padding: 12px 16px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.items-title { font-size: 13px; font-weight: 700; color: #374151; text-transform: uppercase; letter-spacing: 0.04em; }
.btn-add-item { padding: 6px 14px; background: #2563eb; color: white; border: none; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; }
.btn-add-item:hover { background: #1d4ed8; }

.items-empty { padding: 24px; text-align: center; font-size: 13px; color: #94a3b8; }

.items-table-wrapper { overflow-x: auto; }
.items-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.items-table th { padding: 8px 12px; text-align: left; font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.04em; background: #f8fafc; border-bottom: 1px solid #e2e8f0; }
.items-table td { padding: 8px 10px; border-bottom: 1px solid #f1f5f9; vertical-align: middle; }
.items-table tfoot td { border-top: 2px solid #e2e8f0; border-bottom: none; font-weight: 700; padding: 10px 10px; }

.form-input--sm { padding: 6px 10px; font-size: 13px; }
.subtotal-cell { font-weight: 600; color: #0f172a; font-size: 13px; }
.total-label { text-align: right; color: #374151; font-size: 13px; }
.total-value { color: #2563eb; font-size: 15px; }

.btn-remove-item { background: none; border: none; color: #94a3b8; cursor: pointer; font-size: 14px; padding: 4px 6px; border-radius: 6px; }
.btn-remove-item:hover { color: #ef4444; background: #fef2f2; }
</style>
