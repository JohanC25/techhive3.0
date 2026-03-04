<template>
  <div class="view">
    <div class="view-header">
      <div>
        <h2 class="view-title">Reportes</h2>
        <p class="view-sub">Análisis y estadísticas del negocio</p>
      </div>
      <div class="header-right">
        <input v-model="filters.fecha_inicio" @change="loadAll" type="date" class="filter-input" />
        <span class="date-sep">–</span>
        <input v-model="filters.fecha_fin" @change="loadAll" type="date" class="filter-input" />
        <button class="btn-secondary" @click="setPreset('month')">Este mes</button>
        <button class="btn-secondary" @click="setPreset('quarter')">Trimestre</button>
        <button class="btn-secondary" @click="setPreset('year')">Este año</button>
      </div>
    </div>

    <!-- Summary KPIs -->
    <div v-if="loading" class="kpi-grid">
      <div v-for="i in 4" :key="i" class="kpi-card skeleton-kpi">
        <div class="sk-line sk-short"></div>
        <div class="sk-line sk-long"></div>
        <div class="sk-line sk-med"></div>
      </div>
    </div>

    <div v-else class="kpi-grid">
      <div class="kpi-card kpi-blue">
        <div class="kpi-icon">
          <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-label">Ventas totales</div>
          <div class="kpi-value">{{ fmt(dash.ventas?.total ?? 0) }}</div>
          <div class="kpi-sub">{{ dash.ventas?.transacciones ?? 0 }} transacciones</div>
        </div>
      </div>

      <div class="kpi-card kpi-green">
        <div class="kpi-icon">
          <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-label">Balance de caja</div>
          <div class="kpi-value" :style="{ color: (dash.caja?.balance ?? 0) >= 0 ? '#059669' : '#dc2626' }">
            {{ fmt(dash.caja?.balance ?? 0) }}
          </div>
          <div class="kpi-sub">Ing: {{ fmt(dash.caja?.ingresos ?? 0) }} · Eg: {{ fmt(dash.caja?.egresos ?? 0) }}</div>
        </div>
      </div>

      <div class="kpi-card kpi-orange">
        <div class="kpi-icon">
          <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"/>
          </svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-label">Compras</div>
          <div class="kpi-value">{{ fmt(purchasesSummary.total_amount ?? 0) }}</div>
          <div class="kpi-sub">{{ purchasesSummary.total_purchases ?? 0 }} órdenes</div>
        </div>
      </div>

      <div class="kpi-card kpi-purple">
        <div class="kpi-icon">
          <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><circle cx="12" cy="12" r="3"/>
          </svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-label">Servicio técnico</div>
          <div class="kpi-value">{{ dash.servicio_tecnico?.tickets_abiertos ?? 0 }}</div>
          <div class="kpi-sub">{{ dash.servicio_tecnico?.tickets_completados_periodo ?? 0 }} completados en período</div>
        </div>
      </div>
    </div>

    <!-- Charts row -->
    <div class="charts-row">
      <!-- Ventas por día -->
      <div class="chart-card">
        <div class="chart-card-header">
          <h3 class="chart-title">Ventas por día</h3>
          <span class="chart-subtitle">Últimos 30 días</span>
        </div>
        <div v-if="salesByDay.length" class="bar-chart-wrap">
          <div class="bar-chart">
            <div
              v-for="(d, i) in salesByDay"
              :key="i"
              class="bar-col"
              :title="`${d.fecha_venta}: ${fmt(d.total)}`"
            >
              <div class="bar-fill" :style="{ height: barHeight(d.total) + '%' }"></div>
            </div>
          </div>
          <div class="bar-axis">
            <span>{{ salesByDay[0]?.fecha_venta }}</span>
            <span>{{ salesByDay[salesByDay.length - 1]?.fecha_venta }}</span>
          </div>
        </div>
        <div v-else class="chart-empty">Sin datos para el período</div>
      </div>

      <!-- Ventas por método de pago -->
      <div class="chart-card">
        <div class="chart-card-header">
          <h3 class="chart-title">Por método de pago</h3>
        </div>
        <div v-if="paymentMethods.length" class="donut-wrap">
          <div class="donut-legend">
            <div v-for="(pm, i) in paymentMethods" :key="i" class="legend-row">
              <span class="legend-dot" :style="{ background: COLORS[i % COLORS.length] }"></span>
              <span class="legend-label">{{ labelPayment(pm.metodo_pago) }}</span>
              <span class="legend-pct">{{ pct(pm.total, totalSales) }}%</span>
              <span class="legend-val">{{ fmt(pm.total) }}</span>
            </div>
          </div>
          <svg class="donut-svg" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="50" fill="none" stroke="#f1f5f9" stroke-width="20"/>
            <circle
              v-for="(seg, i) in donutSegments"
              :key="i"
              cx="60" cy="60" r="50"
              fill="none"
              :stroke="COLORS[i % COLORS.length]"
              stroke-width="20"
              :stroke-dasharray="`${seg.dash} ${314 - seg.dash}`"
              :stroke-dashoffset="seg.offset"
              transform="rotate(-90 60 60)"
            />
            <text x="60" y="64" text-anchor="middle" font-size="11" font-weight="700" fill="#0f172a">
              {{ paymentMethods.length }}
            </text>
            <text x="60" y="74" text-anchor="middle" font-size="7" fill="#94a3b8">métodos</text>
          </svg>
        </div>
        <div v-else class="chart-empty">Sin datos de ventas</div>
      </div>
    </div>

    <!-- Tables row -->
    <div class="tables-row">
      <!-- Top productos -->
      <div class="table-card">
        <div class="table-card-header">
          <h3 class="table-card-title">Top productos vendidos</h3>
        </div>
        <div v-if="topProducts.length">
          <table class="mini-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Producto</th>
                <th class="text-right">Cant.</th>
                <th class="text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(p, i) in topProducts" :key="i">
                <td class="rank">{{ i + 1 }}</td>
                <td>{{ p.descripcion }}</td>
                <td class="text-right font-mono">{{ p.cantidad }}</td>
                <td class="text-right font-semibold text-green">{{ fmt(p.total) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="mini-empty">Sin datos</div>
      </div>

      <!-- Compras por estado -->
      <div class="table-card">
        <div class="table-card-header">
          <h3 class="table-card-title">Compras por estado</h3>
        </div>
        <div v-if="purchasesByStatus.length">
          <table class="mini-table">
            <thead>
              <tr>
                <th>Estado</th>
                <th class="text-right">Órdenes</th>
                <th class="text-right">Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in purchasesByStatus" :key="p.status">
                <td>
                  <span :class="`badge badge-${statusColor(p.status)}`">{{ labelStatus(p.status) }}</span>
                </td>
                <td class="text-right font-mono">{{ p.count }}</td>
                <td class="text-right font-semibold">{{ fmt(p.total) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="mini-empty">Sin datos</div>
      </div>

      <!-- Cash flow por categoría -->
      <div class="table-card">
        <div class="table-card-header">
          <h3 class="table-card-title">Caja por categoría</h3>
        </div>
        <div v-if="cashByCategory.length">
          <table class="mini-table">
            <thead>
              <tr>
                <th>Categoría</th>
                <th class="text-right">Ingreso</th>
                <th class="text-right">Egreso</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in cashByCategory" :key="c.category">
                <td>{{ labelCategory(c.category) }}</td>
                <td class="text-right text-green">{{ c.income > 0 ? fmt(c.income) : '—' }}</td>
                <td class="text-right text-red">{{ c.expense > 0 ? fmt(c.expense) : '—' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="mini-empty">Sin datos</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useToastStore } from '@/stores/toast'

const toast = useToastStore()

const loading = ref(false)
const filters = ref({ fecha_inicio: '', fecha_fin: '' })

// Data
const dash = ref<any>({})
const salesByDay = ref<Array<{ fecha_venta: string; total: number }>>([])
const paymentMethods = ref<Array<{ metodo_pago: string; total: number; count: number }>>([])
const topProducts = ref<Array<{ descripcion: string; cantidad: number; total: number }>>([])
const purchasesSummary = ref<any>({})
const purchasesByStatus = ref<Array<{ status: string; count: number; total: number }>>([])
const cashByCategory = ref<Array<{ category: string; income: number; expense: number }>>([])

const COLORS = ['#2563eb', '#059669', '#d97706', '#7c3aed', '#dc2626', '#0891b2', '#db2777']

const totalSales = computed(() => paymentMethods.value.reduce((s, p) => s + p.total, 0))

const donutSegments = computed(() => {
  const total = totalSales.value || 1
  const circumference = 314
  let offset = 0
  return paymentMethods.value.map((pm) => {
    const dash = (pm.total / total) * circumference
    const seg = { dash, offset: -offset }
    offset += dash
    return seg
  })
})

function setPreset(preset: 'month' | 'quarter' | 'year') {
  const now = new Date()
  const fmt = (d: Date) => d.toISOString().split('T')[0]
  if (preset === 'month') {
    filters.value.fecha_inicio = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-01`
    filters.value.fecha_fin = fmt(now)
  } else if (preset === 'quarter') {
    const q = Math.floor(now.getMonth() / 3)
    filters.value.fecha_inicio = `${now.getFullYear()}-${String(q * 3 + 1).padStart(2, '0')}-01`
    filters.value.fecha_fin = fmt(now)
  } else {
    filters.value.fecha_inicio = `${now.getFullYear()}-01-01`
    filters.value.fecha_fin = fmt(now)
  }
  loadAll()
}

async function loadAll() {
  loading.value = true
  const { fecha_inicio, fecha_fin } = filters.value
  const p = new URLSearchParams()
  if (fecha_inicio) p.set('fecha_inicio', fecha_inicio)
  if (fecha_fin) p.set('fecha_fin', fecha_fin)
  const qs = p.toString()
  try {
    const [dashRes, salesDayRes, pmRes, topProdRes, purchRes, cashRes] = await Promise.all([
      api.get(`/reports/dashboard/?${qs}`),
      api.get(`/reports/ventas-por-dia/?${qs}`),
      api.get(`/sales/ventas/por-metodo-pago/?${qs}`),
      api.get(`/sales/ventas/por-producto/?${qs}`),
      api.get(`/reports/compras/?${qs}`),
      api.get(`/cash/movements/?${qs}&page_size=200`),
    ])
    dash.value = dashRes.data
    salesByDay.value = salesDayRes.data
    paymentMethods.value = pmRes.data
    topProducts.value = (topProdRes.data || []).slice(0, 8)
    purchasesSummary.value = purchRes.data
    purchasesByStatus.value = purchRes.data.by_status || []
    // aggregate cash by category client-side
    const movements: any[] = cashRes.data.results || []
    const map: Record<string, { income: number; expense: number }> = {}
    for (const m of movements) {
      if (!map[m.category]) map[m.category] = { income: 0, expense: 0 }
      if (m.type === 'income') map[m.category].income += Number(m.amount)
      else map[m.category].expense += Number(m.amount)
    }
    cashByCategory.value = Object.entries(map).map(([category, v]) => ({ category, ...v }))
  } catch {
    toast.error('Error al cargar reportes')
  } finally {
    loading.value = false
  }
}

function barHeight(val: number) {
  const max = Math.max(...salesByDay.value.map((d) => d.total), 1)
  return Math.max((val / max) * 100, 2)
}

function pct(val: number, total: number) {
  if (!total) return 0
  return Math.round((val / total) * 100)
}

function fmt(v: number) {
  return `$${Number(v || 0).toLocaleString('es-EC', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

const paymentLabels: Record<string, string> = {
  efectivo: 'Efectivo', transferencia: 'Transferencia', deuna: 'DeUna', tarjeta: 'Tarjeta', otro: 'Otro',
}
function labelPayment(v: string) { return paymentLabels[v] ?? v }

const statusLabels: Record<string, string> = {
  pending: 'Pendiente', received: 'Recibida', cancelled: 'Cancelada',
}
function labelStatus(v: string) { return statusLabels[v] ?? v }
function statusColor(v: string) {
  return { pending: 'yellow', received: 'green', cancelled: 'red' }[v] ?? 'gray'
}

const categoryLabels: Record<string, string> = {
  sale: 'Venta', purchase: 'Compra', salary: 'Salario', service: 'Servicio técnico',
  rent: 'Arriendo', utility: 'Servicios básicos', other: 'Otro',
}
function labelCategory(v: string) { return categoryLabels[v] ?? v }

onMounted(() => {
  setPreset('month')
})
</script>

<style scoped>
@import '@/assets/crud.css';

/* Header */
.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.date-sep { color: #94a3b8; font-weight: 600; }

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
@media (max-width: 1100px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px)  { .kpi-grid { grid-template-columns: 1fr; } }

.kpi-card {
  background: white;
  border-radius: 14px;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  gap: 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  border: 1px solid #f1f5f9;
}
.kpi-icon {
  width: 44px; height: 44px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.kpi-blue   .kpi-icon { background: #eff6ff; color: #2563eb; }
.kpi-green  .kpi-icon { background: #ecfdf5; color: #059669; }
.kpi-orange .kpi-icon { background: #fffbeb; color: #d97706; }
.kpi-purple .kpi-icon { background: #f5f3ff; color: #7c3aed; }
.kpi-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #94a3b8; }
.kpi-value { font-size: 22px; font-weight: 800; color: #0f172a; margin: 3px 0; line-height: 1.2; }
.kpi-sub   { font-size: 12px; color: #64748b; }

/* Skeleton */
.skeleton-kpi { flex-direction: column; gap: 10px; }
.sk-line {
  height: 12px; border-radius: 6px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.sk-short { width: 35%; }
.sk-long  { width: 55%; height: 22px; }
.sk-med   { width: 65%; }
@keyframes shimmer { to { background-position: -200% 0; } }

/* Charts row */
.charts-row {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 16px;
}
@media (max-width: 900px) { .charts-row { grid-template-columns: 1fr; } }

.chart-card {
  background: white;
  border-radius: 14px;
  padding: 22px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  border: 1px solid #f1f5f9;
}
.chart-card-header {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-bottom: 18px;
}
.chart-title    { font-size: 15px; font-weight: 700; color: #0f172a; margin: 0; }
.chart-subtitle { font-size: 12px; color: #94a3b8; }
.chart-empty { text-align: center; color: #94a3b8; font-size: 13px; padding: 40px 0; }

/* Bar chart */
.bar-chart-wrap { display: flex; flex-direction: column; gap: 8px; }
.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 130px;
}
.bar-col { flex: 1; display: flex; align-items: flex-end; cursor: pointer; }
.bar-fill {
  width: 100%;
  background: #2563eb;
  border-radius: 3px 3px 0 0;
  min-height: 2px;
  transition: height 0.4s ease;
  opacity: 0.75;
}
.bar-col:hover .bar-fill { opacity: 1; }
.bar-axis { display: flex; justify-content: space-between; font-size: 10px; color: #94a3b8; }

/* Donut */
.donut-wrap {
  display: flex;
  align-items: center;
  gap: 16px;
}
.donut-svg { width: 110px; height: 110px; flex-shrink: 0; }
.donut-legend { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.legend-row { display: flex; align-items: center; gap: 6px; font-size: 12px; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.legend-label { flex: 1; color: #374151; }
.legend-pct { color: #94a3b8; font-size: 11px; }
.legend-val { font-weight: 600; color: #0f172a; min-width: 70px; text-align: right; }

/* Tables row */
.tables-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
@media (max-width: 1000px) { .tables-row { grid-template-columns: 1fr 1fr; } }
@media (max-width: 640px)  { .tables-row { grid-template-columns: 1fr; } }

.table-card {
  background: white;
  border-radius: 14px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  border: 1px solid #f1f5f9;
  overflow: hidden;
}
.table-card-header {
  padding: 16px 18px 12px;
  border-bottom: 1px solid #f1f5f9;
}
.table-card-title { font-size: 14px; font-weight: 700; color: #0f172a; margin: 0; }

.mini-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.mini-table th {
  padding: 8px 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #94a3b8;
  background: #f8fafc;
  border-bottom: 1px solid #f1f5f9;
}
.mini-table td {
  padding: 9px 12px;
  border-bottom: 1px solid #f8fafc;
  color: #374151;
}
.mini-table tr:last-child td { border-bottom: none; }
.mini-table tr:hover td { background: #f8fafc; }

.rank {
  font-size: 12px;
  font-weight: 700;
  color: #94a3b8;
  width: 24px;
}
.text-right { text-align: right; }
.font-mono   { font-family: monospace; }
.font-semibold { font-weight: 600; }
.text-green { color: #059669; }
.text-red   { color: #dc2626; }
.mini-empty { padding: 28px; text-align: center; color: #94a3b8; font-size: 13px; }
</style>
