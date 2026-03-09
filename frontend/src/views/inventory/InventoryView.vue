<template>
  <div class="view">
    <!-- Header -->
    <div class="view-header">
      <div>
        <h2 class="view-title">Inventario</h2>
        <p class="view-sub">Gestión de productos y categorías</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4"/>
        </svg>
        {{ activeTab === 'products' ? 'Nuevo producto' : 'Nueva categoría' }}
      </button>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button class="tab-btn" :class="{ active: activeTab === 'products' }" @click="activeTab = 'products'; loadData()">
        Productos ({{ totalProducts }})
      </button>
      <button class="tab-btn" :class="{ active: activeTab === 'categories' }" @click="activeTab = 'categories'; loadCategories()">
        Categorías
      </button>
    </div>

    <!-- Products tab -->
    <template v-if="activeTab === 'products'">
      <div class="filters-bar">
        <input v-model="search" @input="debouncedLoad" type="search" placeholder="Buscar producto, SKU..." class="filter-input filter-search" />
        <select v-model="filters.category" @change="() => loadData(1)" class="filter-select">
          <option value="">Todas las categorías</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
        <select v-model="filters.is_active" @change="() => loadData(1)" class="filter-select">
          <option value="">Todos</option>
          <option value="true">Activos</option>
          <option value="false">Inactivos</option>
        </select>
        <button v-if="search || filters.category || filters.is_active" @click="clearFilters" class="btn-clear">Limpiar</button>
      </div>

      <div class="table-card">
        <div v-if="tableLoading" class="table-loading"><div class="spinner-lg"></div></div>
        <table v-else-if="items.length" class="data-table">
          <thead>
            <tr>
              <th>Producto</th>
              <th>SKU</th>
              <th>Categoría</th>
              <th class="text-right">Precio</th>
              <th class="text-right">Costo</th>
              <th class="text-center">Stock</th>
              <th class="text-center">Estado</th>
              <th class="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in items" :key="item.id">
              <td>
                <div style="font-weight:600;color:#0f172a">{{ item.name }}</div>
                <div v-if="item.description" style="font-size:12px;color:#94a3b8">{{ item.description.slice(0,60) }}</div>
              </td>
              <td class="font-mono">{{ item.sku || '—' }}</td>
              <td>{{ item.category_name || '—' }}</td>
              <td class="text-right">{{ fmt(item.price) }}</td>
              <td class="text-right">{{ item.cost ? fmt(item.cost) : '—' }}</td>
              <td class="text-center">
                <span :class="item.low_stock ? 'badge badge-orange' : 'badge badge-green'">
                  {{ item.stock }}
                  <span v-if="item.low_stock"> ⚠</span>
                </span>
              </td>
              <td class="text-center">
                <span :class="item.is_active ? 'badge badge-green' : 'badge badge-gray'">
                  {{ item.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="text-center">
                <div class="row-actions">
                  <button class="btn-icon btn-edit" @click="openEdit(item)">
                    <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                  </button>
                  <button class="btn-icon btn-delete" @click="confirmDelete(item)">
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
          <div class="empty-icon">📦</div>
          <p>No hay productos registrados.</p>
          <button class="btn-primary" @click="openCreate">Agregar primer producto</button>
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

    <!-- Categories tab -->
    <template v-if="activeTab === 'categories'">
      <div class="table-card">
        <div v-if="catLoading" class="table-loading"><div class="spinner-lg"></div></div>
        <table v-else-if="categories.length" class="data-table">
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Descripción</th>
              <th class="text-center">Productos</th>
              <th class="text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="cat in categories" :key="cat.id">
              <td style="font-weight:600">{{ cat.name }}</td>
              <td>{{ cat.description || '—' }}</td>
              <td class="text-center">{{ cat.products?.length ?? '—' }}</td>
              <td class="text-center">
                <div class="row-actions">
                  <button class="btn-icon btn-edit" @click="openEditCat(cat)">
                    <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                  </button>
                  <button class="btn-icon btn-delete" @click="confirmDeleteCat(cat)">
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
          <div class="empty-icon">🗂️</div>
          <p>No hay categorías registradas.</p>
          <button class="btn-primary" @click="openCreate">Agregar categoría</button>
        </div>
      </div>
    </template>

    <!-- Modal Producto -->
    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
        <div class="modal">
          <div class="modal-header">
            <h3 class="modal-title">{{ editingItem ? 'Editar producto' : activeTab === 'categories' ? 'Nueva categoría' : 'Nuevo producto' }}</h3>
            <button class="modal-close" @click="closeModal">✕</button>
          </div>
          <!-- Category form -->
          <form v-if="activeTab === 'categories'" @submit.prevent="saveCat" class="modal-form">
            <div class="form-group">
              <label class="form-label">Nombre *</label>
              <input v-model="catForm.name" type="text" class="form-input" required />
            </div>
            <div class="form-group">
              <label class="form-label">Descripción</label>
              <textarea v-model="catForm.description" class="form-input form-textarea"></textarea>
            </div>
            <div v-if="formError" class="form-error">{{ formError }}</div>
            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="saving"><span v-if="saving" class="spinner-sm"></span>Guardar</button>
            </div>
          </form>
          <!-- Product form -->
          <form v-else @submit.prevent="saveItem" class="modal-form">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Nombre *</label>
                <input v-model="prodForm.name" type="text" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">SKU</label>
                <input v-model="prodForm.sku" type="text" class="form-input" />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Categoría</label>
              <select v-model="prodForm.category" class="form-input">
                <option :value="null">Sin categoría</option>
                <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Descripción</label>
              <textarea v-model="prodForm.description" class="form-input form-textarea"></textarea>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Precio de venta *</label>
                <input v-model.number="prodForm.price" type="number" step="0.01" min="0" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">Costo</label>
                <input v-model.number="prodForm.cost" type="number" step="0.01" min="0" class="form-input" />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">Stock *</label>
                <input v-model.number="prodForm.stock" type="number" min="0" class="form-input" required />
              </div>
              <div class="form-group">
                <label class="form-label">Stock mínimo</label>
                <input v-model.number="prodForm.stock_min" type="number" min="0" class="form-input" />
              </div>
            </div>
            <div class="form-check">
              <label class="check-label"><input type="checkbox" v-model="prodForm.is_active" /> Producto activo</label>
            </div>
            <div v-if="formError" class="form-error">{{ formError }}</div>
            <div class="modal-footer">
              <button type="button" class="btn-secondary" @click="closeModal">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="saving"><span v-if="saving" class="spinner-sm"></span>{{ editingItem ? 'Guardar cambios' : 'Crear producto' }}</button>
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
          <p class="confirm-text">¿Estás seguro de eliminar este registro? Esta acción no se puede deshacer.</p>
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
const activeTab = ref<'products' | 'categories'>('products')

interface Product {
  id: number; name: string; sku: string; category: number | null; category_name: string
  description: string; price: number; cost: number | null; stock: number; stock_min: number
  is_active: boolean; low_stock: boolean
}
interface Category { id: number; name: string; description: string }

const items = ref<Product[]>([])
const categories = ref<Category[]>([])
const count = ref(0); const nextUrl = ref<string | null>(null); const prevUrl = ref<string | null>(null)
const currentPage = ref(1); const totalProducts = ref(0)
const tableLoading = ref(false); const catLoading = ref(false); const saving = ref(false)
const search = ref(''); const filters = ref({ category: '', is_active: '' })
const showModal = ref(false); const showConfirm = ref(false)
const editingItem = ref<Product | Category | null>(null)
const deletingItem = ref<any>(null); const formError = ref('')

const emptyProd = () => ({ name: '', sku: '', category: null as number | null, description: '', price: 0, cost: null as number | null, stock: 0, stock_min: 0, is_active: true })
const emptyCat = () => ({ name: '', description: '' })
const prodForm = ref(emptyProd())
const catForm = ref(emptyCat())

const paginationText = computed(() => {
  const s = (currentPage.value - 1) * 20 + 1; const e = Math.min(currentPage.value * 20, count.value)
  return `${s}–${e} de ${count.value}`
})

let debounceTimer: ReturnType<typeof setTimeout>
function debouncedLoad() { clearTimeout(debounceTimer); debounceTimer = setTimeout(() => loadData(), 400) }

async function loadData(page = 1) {
  tableLoading.value = true; currentPage.value = page
  const p = new URLSearchParams()
  if (search.value) p.set('search', search.value)
  if (filters.value.category) p.set('category', filters.value.category)
  if (filters.value.is_active) p.set('is_active', filters.value.is_active)
  p.set('page', String(page))
  try {
    const res = await api.get(`/inventory/products/?${p}`)
    items.value = res.data.results; count.value = res.data.count; totalProducts.value = res.data.count
    nextUrl.value = res.data.next; prevUrl.value = res.data.previous
  } catch { toast.error('Error al cargar productos') } finally { tableLoading.value = false }
}

async function loadCategories() {
  catLoading.value = true
  try { const res = await api.get('/inventory/categories/'); categories.value = res.data.results ?? res.data }
  catch { toast.error('Error al cargar categorías') } finally { catLoading.value = false }
}

function goPage(p: number) { loadData(p) }
function fmt(v: number) { return `$${Number(v || 0).toLocaleString('es-EC', { minimumFractionDigits: 2 })}` }
function clearFilters() { search.value = ''; filters.value = { category: '', is_active: '' }; loadData() }

function openCreate() {
  editingItem.value = null; formError.value = ''
  if (activeTab.value === 'categories') catForm.value = emptyCat()
  else prodForm.value = emptyProd()
  showModal.value = true
}
function openEdit(item: Product) { editingItem.value = item; prodForm.value = { ...item }; formError.value = ''; showModal.value = true }
function openEditCat(cat: Category) { editingItem.value = cat; catForm.value = { ...cat }; formError.value = ''; showModal.value = true }
function closeModal() { showModal.value = false }
function confirmDelete(item: Product) { deletingItem.value = item; showConfirm.value = true }
function confirmDeleteCat(cat: Category) { deletingItem.value = cat; showConfirm.value = true }

async function saveItem() {
  formError.value = ''; saving.value = true
  try {
    if (editingItem.value) { await api.put(`/inventory/products/${(editingItem.value as Product).id}/`, prodForm.value); toast.success('Producto actualizado') }
    else { await api.post('/inventory/products/', prodForm.value); toast.success('Producto creado') }
    closeModal(); loadData(currentPage.value)
  } catch (e: any) { formError.value = e.response?.data?.detail || 'Error al guardar' }
  finally { saving.value = false }
}

async function saveCat() {
  formError.value = ''; saving.value = true
  try {
    if (editingItem.value) { await api.put(`/inventory/categories/${(editingItem.value as Category).id}/`, catForm.value); toast.success('Categoría actualizada') }
    else { await api.post('/inventory/categories/', catForm.value); toast.success('Categoría creada') }
    closeModal(); loadCategories()
  } catch (e: any) { formError.value = e.response?.data?.detail || 'Error al guardar' }
  finally { saving.value = false }
}

async function deleteItem() {
  saving.value = true
  const isProduct = activeTab.value === 'products'
  const url = isProduct ? `/inventory/products/${deletingItem.value.id}/` : `/inventory/categories/${deletingItem.value.id}/`
  try {
    await api.delete(url); toast.success('Eliminado correctamente')
    showConfirm.value = false
    if (isProduct) loadData(currentPage.value); else loadCategories()
  } catch { toast.error('Error al eliminar') } finally { saving.value = false }
}

onMounted(async () => { await loadCategories(); loadData() })
</script>

<style scoped>
@import '@/assets/crud.css';
</style>
