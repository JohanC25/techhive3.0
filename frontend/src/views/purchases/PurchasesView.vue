<template>
  <div class="view">
    <div class="view-header">
      <div>
        <h2 class="view-title">Compras</h2>
        <p class="view-sub">Gestión de proveedores y órdenes de compra</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        {{ activeTab === 'purchases' ? 'Nueva compra' : 'Nuevo proveedor' }}
      </button>
    </div>

    <div class="tabs">
      <button class="tab-btn" :class="{ active: activeTab === 'purchases' }" @click="activeTab = 'purchases'; loadData()">
        Compras
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'suppliers' }" @click="activeTab = 'suppliers'; loadSuppliers()">
        Proveedores
      </button>
    </div>

    <!-- Purchases -->
    <template v-if="activeTab === 'purchases'">
      <div class="filters-bar">
        <input v-model="search" @input="debouncedLoad" type="search" placeholder="Buscar proveedor, notas..." class="filter-input filter-search" />
        <input v-model="filters.fecha_inicio" @change="() => loadData(1)" type="date" class="filter-input" />
        <input v-model="filters.fecha_fin" @change="() => loadData(1)" type="date" class="filter-input" />
        <select v-model="filters.status" @change="() => loadData(1)" class="filter-select">
          <option value="">Todos los estados</option>
          <option value="pending">Pendiente</option>
          <option value="received">Recibida</option>
          <option value="cancelled">Cancelada</option>
        </select>
      </div>

      <div class="table-card">
        <div v-if="tableLoading" class="table-loading"><div class="spinner-lg"></div></div>
        <table v-else-if="items.length" class="data-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Fecha</th>
              <th>Proveedor</th>
              <th class="text-center">Ítems</th>
              <th class="text-right">Total</th>
              <th class="text-center">Estado</th>
              <th class="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td class="font-mono" style="color:#94a3b8">#{{ item.id }}</td>
              <td class="font-mono">{{ item.date }}</td>
              <td style="font-weight:600">{{ item.supplier_name }}</td>
              <td class="text-center">{{ item.items?.length ?? 0 }}</td>
              <td class="text-right font-semibold">{{ fmt(item.total) }}</td>
              <td class="text-center"><span :class="statusBadge(item.status)">{{ statusLabel(item.status) }}</span></td>
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
          <div class="empty-icon">🛒</div>
          <p>No hay compras registradas.</p>
          <button class="btn-primary" @click="openCreate">Registrar primera compra</button>
        </div>
        <div v-if="count > 0" class="pagination">
          <span class="page-info">{{ paginationText }}</span>
          <div class="page-btns">
            <button :disabled="!prevUrl" @click="goPage(currentPage - 1)" class="page-btn">‹ Anterior</button>
            <button :disabled="!nextUrl" @click="goPage(currentPage + 1)" class="page-btn">Siguiente ›</button>
          </div>
        </div>
      </div>
    </template>

    <!-- Suppliers -->
    <template v-if="activeTab === 'suppliers'">
      <div class="table-card">
        <div v-if="supLoading" class="table-loading"><div class="spinner-lg"></div></div>
        <table v-else-if="suppliers.length" class="data-table">
          <thead>
            <tr><th>Proveedor</th><th>RUC</th><th>Email</th><th>Teléfono</th><th class="text-center">Estado</th><th class="text-center">Acciones</th></tr>
          </thead>
          <tbody>
            <tr v-for="sup in suppliers" :key="sup.id">
              <td style="font-weight:600">{{ sup.name }}</td>
              <td class="font-mono">{{ sup.ruc || '—' }}</td>
              <td>{{ sup.email || '—' }}</td>
              <td>{{ sup.phone || '—' }}</td>
              <td class="text-center"><span :class="sup.is_active ? 'badge badge-green' : 'badge badge-gray'">{{ sup.is_active ? 'Activo' : 'Inactivo' }}</span></td>
              <td class="text-center">
                <div class="row-actions">
                  <button class="btn-icon btn-edit" @click="openEditSup(sup)"><svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg></button>
                  <button class="btn-icon btn-delete" @click="confirmDeleteSup(sup)"><svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-else class="empty-state"><div class="empty-icon">🏭</div><p>No hay proveedores registrados.</p><button class="btn-primary" @click="openCreate">Agregar proveedor</button></div>
      </div>
    </template>

    <!-- Modals -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h3 class="modal-title">{{ editingItem ? 'Editar' : 'Nuevo' }} {{ activeTab === 'suppliers' ? 'proveedor' : 'compra' }}</h3>
            <button class="modal-close" @click="closeModal">✕</button>
          </div>

          <!-- Supplier form -->
          <form v-if="activeTab === 'suppliers'" @submit.prevent="saveSup" class="modal-form">
            <div class="form-group"><label class="form-label">Nombre *</label><input v-model="supForm.name" type="text" class="form-input" required /></div>
            <div class="form-row">
              <div class="form-group"><label class="form-label">RUC / Cédula</label><input v-model="supForm.ruc" type="text" class="form-input" /></div>
              <div class="form-group"><label class="form-label">Teléfono</label><input v-model="supForm.phone" type="text" class="form-input" /></div>
            </div>
            <div class="form-group"><label class="form-label">Email</label><input v-model="supForm.email" type="email" class="form-input" /></div>
            <div class="form-group"><label class="form-label">Dirección</label><textarea v-model="supForm.address" class="form-input form-textarea"></textarea></div>
            <div class="form-check"><label class="check-label"><input type="checkbox" v-model="supForm.is_active" /> Activo</label></div>
            <div v-if="formError" class="form-error">{{ formError }}</div>
            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="saving"><span v-if="saving" class="spinner-sm"></span>Guardar</button>
            </div>
          </form>

          <!-- Purchase form -->
          <form v-else @submit.prevent="saveItem" class="modal-form">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Proveedor *</label>
                <select v-model.number="purForm.supplier" class="form-input" required>
                  <option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</option>
                </select>
              </div>
              <div class="form-group"><label class="form-label">Fecha *</label><input v-model="purForm.date" type="date" class="form-input" required /></div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Estado</label>
                <select v-model="purForm.status" class="form-input">
                  <option value="pending">Pendiente</option>
                  <option value="received">Recibida</option>
                  <option value="cancelled">Cancelada</option>
                </select>
              </div>
            </div>
            <div class="form-group"><label class="form-label">Notas</label><textarea v-model="purForm.notes" class="form-input form-textarea"></textarea></div>

            <!-- Items -->
            <div class="items-section">
              <div class="items-header">
                <span style="font-weight:600;font-size:14px">Ítems de la compra</span>
                <button type="button" class="btn-add-item" @click="addItem">+ Agregar ítem</button>
              </div>
              <div v-for="(item, idx) in purForm.items" :key="idx" class="item-row">
                <input v-model="item.description" type="text" placeholder="Descripción" class="form-input" style="flex:2" />
                <input v-model.number="item.quantity" type="number" min="1" placeholder="Cant." class="form-input" style="width:70px" />
                <input v-model.number="item.unit_price" type="number" step="0.01" placeholder="P. unit." class="form-input" style="width:100px" />
                <span style="font-size:13px;font-weight:600;color:#0f172a;min-width:70px;text-align:right">{{ fmt(item.quantity * item.unit_price) }}</span>
                <button type="button" class="btn-icon btn-delete" @click="purForm.items.splice(idx, 1)">✕</button>
              </div>
              <div v-if="purForm.items.length === 0" style="font-size:13px;color:#94a3b8;padding:8px 0">Sin ítems. Agrega al menos uno.</div>
            </div>

            <div v-if="formError" class="form-error">{{ formError }}</div>
            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="saving"><span v-if="saving" class="spinner-sm"></span>{{ editingItem ? 'Guardar cambios' : 'Registrar compra' }}</button>
            </div>
          </form>
        </div>
      </div>

      <div v-if="showConfirm" class="modal-overlay" @click.self="showConfirm = false">
        <div class="modal modal-sm">
          <div class="modal-header"><h3 class="modal-title">Confirmar eliminación</h3><button class="modal-close" @click="showConfirm = false">✕</button></div>
          <p class="confirm-text">¿Estás seguro? Esta acción no se puede deshacer.</p>
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
const activeTab = ref<'purchases' | 'suppliers'>('purchases')

interface PurchaseItem { description: string; quantity: number; unit_price: number }
interface Purchase { id: number; date: string; supplier: number; supplier_name: string; status: string; total: number; notes: string; items: PurchaseItem[] }
interface Supplier { id: number; name: string; ruc: string; email: string; phone: string; address: string; is_active: boolean }

const items = ref<Purchase[]>([])
const suppliers = ref<Supplier[]>([])
const count = ref(0); const nextUrl = ref<string | null>(null); const prevUrl = ref<string | null>(null)
const currentPage = ref(1)
const tableLoading = ref(false); const supLoading = ref(false); const saving = ref(false)
const search = ref(''); const filters = ref({ fecha_inicio: '', fecha_fin: '', status: '' })
const showModal = ref(false); const showConfirm = ref(false)
const editingItem = ref<any>(null); const deletingItem = ref<any>(null)
const formError = ref('')

const emptyPur = () => ({ supplier: null as number | null, date: new Date().toISOString().split('T')[0], status: 'pending', notes: '', items: [] as PurchaseItem[] })
const emptySup = () => ({ name: '', ruc: '', email: '', phone: '', address: '', is_active: true })
const purForm = ref(emptyPur())
const supForm = ref(emptySup())

const paginationText = computed(() => {
  const s = (currentPage.value - 1) * 20 + 1; const e = Math.min(currentPage.value * 20, count.value)
  return `${s}–${e} de ${count.value}`
})

function statusBadge(s: string) {
  return { pending: 'badge badge-orange', received: 'badge badge-green', cancelled: 'badge badge-gray' }[s] ?? 'badge badge-gray'
}
function statusLabel(s: string) {
  return { pending: 'Pendiente', received: 'Recibida', cancelled: 'Cancelada' }[s] ?? s
}
function fmt(v: number) { return `$${Number(v || 0).toLocaleString('es-EC', { minimumFractionDigits: 2 })}` }

let debounceTimer: ReturnType<typeof setTimeout>
function debouncedLoad() { clearTimeout(debounceTimer); debounceTimer = setTimeout(() => loadData(), 400) }

async function loadData(page = 1) {
  tableLoading.value = true; currentPage.value = page
  const p = new URLSearchParams()
  if (search.value) p.set('search', search.value)
  if (filters.value.fecha_inicio) p.set('fecha_inicio', filters.value.fecha_inicio)
  if (filters.value.fecha_fin) p.set('fecha_fin', filters.value.fecha_fin)
  if (filters.value.status) p.set('status', filters.value.status)
  p.set('page', String(page))
  try {
    const res = await api.get(`/purchases/purchases/?${p}`)
    items.value = res.data.results; count.value = res.data.count
    nextUrl.value = res.data.next; prevUrl.value = res.data.previous
  } catch { toast.error('Error al cargar compras') } finally { tableLoading.value = false }
}

async function loadSuppliers() {
  supLoading.value = true
  try { const res = await api.get('/purchases/suppliers/?is_active=true'); suppliers.value = res.data.results ?? res.data }
  catch { toast.error('Error al cargar proveedores') } finally { supLoading.value = false }
}

function goPage(p: number) { loadData(p) }
function addItem() { purForm.value.items.push({ description: '', quantity: 1, unit_price: 0 }) }

function openCreate() {
  editingItem.value = null; formError.value = ''
  if (activeTab.value === 'suppliers') supForm.value = emptySup()
  else { purForm.value = emptyPur(); addItem() }
  showModal.value = true
}
function openEdit(item: Purchase) { editingItem.value = item; purForm.value = { ...item, items: item.items ? [...item.items] : [] }; formError.value = ''; showModal.value = true }
function openEditSup(sup: Supplier) { editingItem.value = sup; supForm.value = { ...sup }; formError.value = ''; showModal.value = true }
function closeModal() { showModal.value = false }
function confirmDelete(item: any) { deletingItem.value = item; showConfirm.value = true }
function confirmDeleteSup(sup: any) { deletingItem.value = sup; showConfirm.value = true }

async function saveItem() {
  if (!purForm.value.supplier) { formError.value = 'Selecciona un proveedor'; return }
  formError.value = ''; saving.value = true
  try {
    if (editingItem.value) { await api.put(`/purchases/purchases/${editingItem.value.id}/`, purForm.value); toast.success('Compra actualizada') }
    else { await api.post('/purchases/purchases/', purForm.value); toast.success('Compra registrada') }
    closeModal(); loadData(currentPage.value)
  } catch (e: any) { formError.value = e.response?.data?.detail || 'Error al guardar' }
  finally { saving.value = false }
}

async function saveSup() {
  formError.value = ''; saving.value = true
  try {
    if (editingItem.value) { await api.put(`/purchases/suppliers/${editingItem.value.id}/`, supForm.value); toast.success('Proveedor actualizado') }
    else { await api.post('/purchases/suppliers/', supForm.value); toast.success('Proveedor creado') }
    closeModal(); loadSuppliers()
  } catch (e: any) { formError.value = e.response?.data?.detail || 'Error al guardar' }
  finally { saving.value = false }
}

async function deleteItem() {
  saving.value = true
  const url = activeTab.value === 'suppliers'
    ? `/purchases/suppliers/${deletingItem.value.id}/`
    : `/purchases/purchases/${deletingItem.value.id}/`
  try { await api.delete(url); toast.success('Eliminado'); showConfirm.value = false; activeTab.value === 'suppliers' ? loadSuppliers() : loadData(currentPage.value) }
  catch { toast.error('Error al eliminar') } finally { saving.value = false }
}

onMounted(async () => { await loadSuppliers(); loadData() })
</script>

<style scoped>
@import '@/assets/crud.css';
.items-section { display: flex; flex-direction: column; gap: 8px; padding: 14px; background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; }
.items-header { display: flex; justify-content: space-between; align-items: center; }
.btn-add-item { padding: 5px 12px; background: #eff6ff; color: #2563eb; border: 1px solid #bfdbfe; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; }
.btn-add-item:hover { background: #dbeafe; }
.item-row { display: flex; gap: 8px; align-items: center; }
</style>
