<template>
  <div class="catalog">
    <!-- Header -->
    <div class="catalog-header">
      <div>
        <h2 class="catalog-title">Catálogo de productos</h2>
        <p class="catalog-sub">Consulta precios y disponibilidad</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <div class="search-wrap">
        <svg class="search-icon" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="8"/><path stroke-linecap="round" d="M21 21l-4.35-4.35"/>
        </svg>
        <input
          v-model="search"
          @input="debouncedLoad"
          type="search"
          placeholder="Buscar producto..."
          class="search-input"
        />
      </div>
      <select v-model="selectedCategory" @change="loadCatalog" class="filter-select">
        <option value="">Todas las categorías</option>
        <option v-for="cat in categories" :key="cat.name" :value="cat.name">{{ cat.name }}</option>
      </select>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="products-grid">
      <div v-for="i in 8" :key="i" class="product-card skeleton-card">
        <div class="sk-line sk-img"></div>
        <div class="sk-line sk-title"></div>
        <div class="sk-line sk-price"></div>
        <div class="sk-line sk-badge"></div>
      </div>
    </div>

    <!-- Empty -->
    <div v-else-if="products.length === 0" class="empty-state">
      <svg width="48" height="48" fill="none" stroke="#cbd5e1" stroke-width="1.5" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
      </svg>
      <p>No se encontraron productos.</p>
    </div>

    <!-- Products grid -->
    <div v-else class="products-grid">
      <div v-for="product in products" :key="product.id" class="product-card">
        <!-- Placeholder imagen -->
        <div class="product-img">
          <svg width="40" height="40" fill="none" stroke="#94a3b8" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
          </svg>
        </div>

        <div class="product-body">
          <p class="product-category">{{ product.category || 'Sin categoría' }}</p>
          <h3 class="product-name">{{ product.name }}</h3>
          <p v-if="product.description" class="product-desc">{{ product.description }}</p>
        </div>

        <div class="product-footer">
          <span class="product-price">${{ Number(product.price).toFixed(2) }}</span>
          <span class="product-badge" :class="product.available ? 'badge-available' : 'badge-unavailable'">
            {{ product.available ? 'Disponible' : 'Sin stock' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/services/api'

interface CatalogProduct {
  id: number
  name: string
  description: string
  price: number
  category: string | null
  available: boolean
}

interface Category {
  name: string
}

const products = ref<CatalogProduct[]>([])
const categories = ref<Category[]>([])
const loading = ref(true)
const search = ref('')
const selectedCategory = ref('')

let debounceTimer: ReturnType<typeof setTimeout>
function debouncedLoad() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(loadCatalog, 350)
}

async function loadCatalog() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (search.value) params.set('search', search.value)
    if (selectedCategory.value) params.set('category', selectedCategory.value)

    const { data } = await api.get(`/inventory/products/catalog/?${params}`)
    products.value = data
  } catch {
    products.value = []
  } finally {
    loading.value = false
  }
}

async function loadCategories() {
  try {
    // Los clientes no tienen acceso a /inventory/categories/ (IsNotClient)
    // Extraemos las categorías únicas de los productos del catálogo
    const { data } = await api.get('/inventory/products/catalog/')
    const seen = new Set<string>()
    const cats: Category[] = []
    for (const p of data) {
      if (p.category && !seen.has(p.category)) {
        seen.add(p.category)
        cats.push({ name: p.category })
      }
    }
    categories.value = cats
  } catch {
    categories.value = []
  }
}

onMounted(async () => {
  await Promise.all([loadCatalog(), loadCategories()])
})
</script>

<style scoped>
.catalog { display: flex; flex-direction: column; gap: 24px; }

.catalog-header { display: flex; align-items: flex-start; justify-content: space-between; }
.catalog-title { font-size: 24px; font-weight: 800; color: #0f172a; margin: 0; }
.catalog-sub { font-size: 14px; color: #64748b; margin: 4px 0 0; }

/* Filters */
.filters-bar {
  display: flex; gap: 12px; flex-wrap: wrap;
}
.search-wrap {
  position: relative; flex: 1; min-width: 220px;
}
.search-icon {
  position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8;
}
.search-input {
  width: 100%; padding: 10px 14px 10px 38px;
  border: 1.5px solid #e2e8f0; border-radius: 10px;
  font-size: 14px; color: #1e293b; outline: none;
  background: white; box-sizing: border-box;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.search-input:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,0.1); }
.filter-select {
  padding: 10px 14px; border: 1.5px solid #e2e8f0; border-radius: 10px;
  font-size: 14px; color: #374151; background: white; outline: none; cursor: pointer;
  transition: border-color 0.2s;
}
.filter-select:focus { border-color: #2563eb; }

/* Grid */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 18px;
}

/* Card */
.product-card {
  background: white;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.2s, transform 0.2s;
}
.product-card:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.1); transform: translateY(-2px); }

.product-img {
  background: #f8fafc;
  height: 120px;
  display: flex; align-items: center; justify-content: center;
  border-bottom: 1px solid #f1f5f9;
}

.product-body {
  padding: 14px 16px 8px;
  flex: 1;
}
.product-category {
  font-size: 11px; font-weight: 600; color: #2563eb;
  text-transform: uppercase; letter-spacing: 0.5px; margin: 0 0 4px;
}
.product-name {
  font-size: 15px; font-weight: 700; color: #0f172a; margin: 0 0 6px;
  line-height: 1.3;
}
.product-desc {
  font-size: 12px; color: #64748b; margin: 0;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}

.product-footer {
  padding: 10px 16px 14px;
  display: flex; align-items: center; justify-content: space-between;
}
.product-price {
  font-size: 18px; font-weight: 800; color: #0f172a;
}
.product-badge {
  font-size: 11px; font-weight: 600; padding: 3px 10px;
  border-radius: 20px;
}
.badge-available   { background: #dcfce7; color: #166534; }
.badge-unavailable { background: #fee2e2; color: #991b1b; }

/* Skeleton */
.skeleton-card { pointer-events: none; }
.sk-line {
  border-radius: 6px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  margin: 0 16px 10px;
}
.sk-img   { height: 120px; margin: 0 0 12px; border-radius: 0; }
.sk-title { height: 16px; width: 70%; }
.sk-price { height: 20px; width: 40%; }
.sk-badge { height: 14px; width: 55%; }
@keyframes shimmer { to { background-position: -200% 0; } }

/* Empty */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 12px; padding: 80px 0; color: #94a3b8; font-size: 15px;
}
</style>
