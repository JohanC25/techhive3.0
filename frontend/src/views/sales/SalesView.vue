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
      <input v-model="search" @input="debouncedLoad" type="search" placeholder="Buscar por descripción..." class="filter-input filter-search" />
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
            <th>Descripción</th>
            <th class="text-center">Cantidad</th>
            <th class="text-right">Precio unit.</th>
            <th class="text-right">Total</th>
            <th>Método de pago</th>
            <th class="text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td class="font-mono">{{ item.fecha_venta }}</td>
            <td>{{ item.descripcion }}</td>
            <td class="text-center">{{ item.cantidad }}</td>
            <td class="text-right">{{ fmt(item.precio_unitario_pub) }}</td>
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
        <div class="modal">
          <div class="modal-header">
            <h3 class="modal-title">{{ editingItem ? 'Editar venta' : 'Nueva venta' }}</h3>
            <button class="modal-close" @click="closeModal">✕</button>
          </div>
          <form @submit.prevent="saveItem" class="modal-form">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Fecha *</label>
                <input v-model="form.fecha_venta" type="date" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">Cantidad *</label>
                <input v-model.number="form.cantidad" type="number" min="1" class="form-input" required />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Descripción *</label>
              <input v-model="form.descripcion" type="text" class="form-input" required placeholder="Producto o servicio..." />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Precio unitario (público) *</label>
                <input v-model.number="form.precio_unitario_pub" type="number" step="0.01" min="0" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">Precio unitario (empresa)</label>
                <input v-model.number="form.precio_unitario_emp" type="number" step="0.01" min="0" class="form-input" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Total *</label>
                <input v-model.number="form.total" type="number" step="0.01" min="0" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">Método de pago *</label>
                <select v-model="form.metodo_pago" class="form-input" required>
                  <option v-for="m in metodoPagoOpts" :key="m.value" :value="m.value">{{ m.label }}</option>
                </select>
              </div>
            </div>
            <div class="form-check">
              <label class="check-label">
                <input type="checkbox" v-model="form.es_feriado" />
                Es feriado
              </label>
            </div>
            <div v-if="formError" class="form-error">{{ formError }}</div>
            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="saving">
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

interface Venta {
  id: number
  fecha_venta: string
  descripcion: string
  cantidad: number
  precio_unitario_pub: number
  precio_unitario_emp: number | null
  total: number
  metodo_pago: string
  es_feriado: boolean
}

const items = ref<Venta[]>([])
const count = ref(0)
const nextUrl = ref<string | null>(null)
const prevUrl = ref<string | null>(null)
const currentPage = ref(1)
const tableLoading = ref(false)
const saving = ref(false)
const search = ref('')
const showModal = ref(false)
const showConfirm = ref(false)
const editingItem = ref<Venta | null>(null)
const deletingItem = ref<Venta | null>(null)
const formError = ref('')

const summary = ref({ total: 0, transacciones: 0, promedio: 0 })
const filters = ref({ fecha_inicio: '', fecha_fin: '', metodo_pago: '' })

const metodoPagoOpts = [
  { value: 'efectivo', label: 'Efectivo' },
  { value: 'transferencia', label: 'Transferencia' },
  { value: 'deuna', label: 'DeUna' },
  { value: 'tarjeta', label: 'Tarjeta' },
  { value: 'otro', label: 'Otro' },
]

const emptyForm = (): Partial<Venta> & { es_feriado: boolean } => ({
  fecha_venta: new Date().toISOString().split('T')[0],
  descripcion: '',
  cantidad: 1,
  precio_unitario_pub: 0,
  precio_unitario_emp: null,
  total: 0,
  metodo_pago: 'efectivo',
  es_feriado: false,
})
const form = ref(emptyForm())

const hasFilters = computed(() =>
  !!search.value || !!filters.value.fecha_inicio || !!filters.value.fecha_fin || !!filters.value.metodo_pago,
)
const paginationText = computed(() => {
  const start = (currentPage.value - 1) * 20 + 1
  const end = Math.min(currentPage.value * 20, count.value)
  return `${start}–${end} de ${count.value}`
})

let debounceTimer: ReturnType<typeof setTimeout>
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => loadData(), 400)
}

async function loadData(page = 1) {
  tableLoading.value = true
  currentPage.value = page
  const params = new URLSearchParams()
  if (search.value) params.set('search', search.value)
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

function goPage(p: number) { loadData(p) }

function fmt(v: number) {
  return `$${Number(v || 0).toLocaleString('es-EC', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function labelMetodo(v: string) {
  return metodoPagoOpts.find((m) => m.value === v)?.label ?? v
}

function clearFilters() {
  search.value = ''
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
  form.value = { ...item }
  formError.value = ''
  showModal.value = true
}

function closeModal() { showModal.value = false }

function confirmDelete(item: Venta) {
  deletingItem.value = item
  showConfirm.value = true
}

async function saveItem() {
  formError.value = ''
  saving.value = true
  try {
    if (editingItem.value) {
      await api.put(`/sales/ventas/${editingItem.value.id}/`, form.value)
      toast.success('Venta actualizada correctamente')
    } else {
      await api.post('/sales/ventas/', form.value)
      toast.success('Venta registrada correctamente')
    }
    closeModal()
    loadData(currentPage.value)
  } catch (e: any) {
    formError.value = e.response?.data?.detail || 'Error al guardar. Verifica los datos.'
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

onMounted(() => loadData())
</script>

<style scoped>
@import '@/assets/crud.css';
</style>
