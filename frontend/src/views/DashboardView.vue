<template>
  <div class="dashboard">
    <!-- Welcome -->
    <div class="welcome-bar">
      <div>
        <h2 class="welcome-title">Bienvenido, {{ auth.fullName || auth.user?.username }} 👋</h2>
        <p class="welcome-sub">Aquí tienes el resumen del negocio de hoy</p>
      </div>
      <div class="period-selector">
        <select v-model="period" @change="loadDashboard" class="period-select">
          <option value="today">Hoy</option>
          <option value="week">Esta semana</option>
          <option value="month">Este mes</option>
          <option value="year">Este año</option>
        </select>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid" v-if="!loading">
      <div class="kpi-card kpi-blue">
        <div class="kpi-icon">
          <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-label">Ventas del período</div>
          <div class="kpi-value">{{ fmt(data.ventas.total) }}</div>
          <div class="kpi-sub">{{ data.ventas.transacciones }} transacciones</div>
        </div>
      </div>

      <div class="kpi-card" :class="data.caja.balance >= 0 ? 'kpi-green' : 'kpi-red'">
        <div class="kpi-icon">
          <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <rect x="2" y="5" width="20" height="14" rx="2"/><path stroke-linecap="round" d="M2 10h20"/>
          </svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-label">Balance de caja</div>
          <div class="kpi-value">{{ fmt(data.caja.balance) }}</div>
          <div class="kpi-sub">Ing: {{ fmt(data.caja.ingresos) }} · Eg: {{ fmt(data.caja.egresos) }}</div>
        </div>
      </div>

      <div class="kpi-card" :class="data.inventario.productos_stock_bajo > 0 ? 'kpi-orange' : 'kpi-green'">
        <div class="kpi-icon">
          <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/>
          </svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-label">Inventario</div>
          <div class="kpi-value">{{ data.inventario.total_productos }}</div>
          <div class="kpi-sub">
            <span v-if="data.inventario.productos_stock_bajo > 0" style="color:#f59e0b">
              ⚠ {{ data.inventario.productos_stock_bajo }} con stock bajo
            </span>
            <span v-else>✓ Todo en stock</span>
          </div>
        </div>
      </div>

      <div class="kpi-card kpi-purple">
        <div class="kpi-icon">
          <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><circle cx="12" cy="12" r="3"/>
          </svg>
        </div>
        <div class="kpi-body">
          <div class="kpi-label">Servicio Técnico</div>
          <div class="kpi-value">{{ data.servicio_tecnico.tickets_abiertos }}</div>
          <div class="kpi-sub">tickets abiertos</div>
        </div>
      </div>
    </div>

    <!-- Skeleton loading -->
    <div class="kpi-grid" v-else>
      <div v-for="i in 4" :key="i" class="kpi-card skeleton-card">
        <div class="skeleton-line short"></div>
        <div class="skeleton-line long"></div>
        <div class="skeleton-line medium"></div>
      </div>
    </div>

    <!-- Charts row -->
    <div class="charts-row">
      <!-- Ventas últimos 30 días -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Ventas — últimos 30 días</h3>
        </div>
        <div class="chart-wrap" v-if="chartData.length">
          <div class="bar-chart">
            <div
              v-for="(d, i) in chartData"
              :key="i"
              class="bar-col"
              :title="`${d.fecha_venta}: ${fmt(d.total)}`"
            >
              <div class="bar" :style="{ height: barHeight(d.total) + '%' }"></div>
            </div>
          </div>
          <div class="chart-legend">
            <span>{{ chartData[0]?.fecha_venta }}</span>
            <span>{{ chartData[chartData.length - 1]?.fecha_venta }}</span>
          </div>
        </div>
        <div v-else class="empty-chart">Sin datos para el período seleccionado</div>
      </div>

      <!-- Accesos rápidos -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title">Accesos rápidos</h3>
        </div>
        <div class="quick-links">
          <router-link to="/sales" class="quick-link">
            <span class="ql-icon">💰</span>
            <span>Nueva venta</span>
          </router-link>
          <router-link to="/inventory" class="quick-link">
            <span class="ql-icon">📦</span>
            <span>Ver inventario</span>
          </router-link>
          <router-link to="/purchases" class="quick-link">
            <span class="ql-icon">🛒</span>
            <span>Registrar compra</span>
          </router-link>
          <router-link to="/cash" class="quick-link">
            <span class="ql-icon">💳</span>
            <span>Movimiento de caja</span>
          </router-link>
          <router-link to="/technical-service" class="quick-link">
            <span class="ql-icon">🔧</span>
            <span>Nuevo ticket</span>
          </router-link>
          <router-link to="/reports" class="quick-link">
            <span class="ql-icon">📊</span>
            <span>Ver reportes</span>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'

const auth = useAuthStore()
const loading = ref(true)
const period = ref('month')

const data = ref({
  ventas: { total: 0, transacciones: 0, promedio: 0 },
  caja: { ingresos: 0, egresos: 0, balance: 0 },
  inventario: { total_productos: 0, productos_stock_bajo: 0 },
  servicio_tecnico: { tickets_abiertos: 0, tickets_completados_periodo: 0 },
})

const chartData = ref<Array<{ fecha_venta: string; total: number }>>([])

function getPeriodDates() {
  const hoy = new Date()
  const fmt = (d: Date) => d.toISOString().split('T')[0]
  if (period.value === 'today') {
    return { inicio: fmt(hoy), fin: fmt(hoy) }
  }
  if (period.value === 'week') {
    const lunes = new Date(hoy)
    lunes.setDate(hoy.getDate() - hoy.getDay() + 1)
    return { inicio: fmt(lunes), fin: fmt(hoy) }
  }
  if (period.value === 'year') {
    return { inicio: `${hoy.getFullYear()}-01-01`, fin: fmt(hoy) }
  }
  // month (default)
  return { inicio: `${hoy.getFullYear()}-${String(hoy.getMonth() + 1).padStart(2, '0')}-01`, fin: fmt(hoy) }
}

async function loadDashboard() {
  loading.value = true
  const { inicio, fin } = getPeriodDates()
  try {
    const [dash, chart] = await Promise.all([
      api.get(`/reports/dashboard/?fecha_inicio=${inicio}&fecha_fin=${fin}`),
      api.get(`/reports/ventas-por-dia/`),
    ])
    data.value = dash.data
    chartData.value = chart.data
  } catch {
    // silencioso
  } finally {
    loading.value = false
  }
}

function fmt(val: number) {
  return `$${Number(val || 0).toLocaleString('es-EC', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

function barHeight(val: number) {
  const max = Math.max(...chartData.value.map((d) => d.total), 1)
  return Math.max((val / max) * 100, 2)
}

onMounted(loadDashboard)
</script>

<style scoped>
.dashboard { display: flex; flex-direction: column; gap: 24px; }

/* Welcome */
.welcome-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.welcome-title { font-size: 22px; font-weight: 700; color: #0f172a; margin: 0; }
.welcome-sub   { font-size: 14px; color: #64748b; margin: 4px 0 0; }
.period-select {
  padding: 8px 14px;
  border: 1.5px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  color: #374151;
  background: white;
  cursor: pointer;
  outline: none;
}
.period-select:focus { border-color: #2563eb; }

/* KPI Grid */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
@media (max-width: 1100px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 600px)  { .kpi-grid { grid-template-columns: 1fr; } }

.kpi-card {
  background: white;
  border-radius: 14px;
  padding: 22px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  border: 1px solid #f1f5f9;
  transition: transform 0.2s, box-shadow 0.2s;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.1); }

.kpi-icon {
  width: 48px; height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.kpi-blue   .kpi-icon { background: #eff6ff; color: #2563eb; }
.kpi-green  .kpi-icon { background: #ecfdf5; color: #059669; }
.kpi-red    .kpi-icon { background: #fef2f2; color: #dc2626; }
.kpi-orange .kpi-icon { background: #fffbeb; color: #d97706; }
.kpi-purple .kpi-icon { background: #f5f3ff; color: #7c3aed; }

.kpi-label { font-size: 12px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
.kpi-value { font-size: 26px; font-weight: 800; color: #0f172a; line-height: 1.2; margin: 4px 0; }
.kpi-sub   { font-size: 12px; color: #64748b; }

/* Skeleton */
.skeleton-card { flex-direction: column; gap: 12px; }
.skeleton-line {
  height: 14px;
  border-radius: 6px;
  background: linear-gradient(90deg, #f1f5f9 25%, #e2e8f0 50%, #f1f5f9 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.skeleton-line.short  { width: 40%; }
.skeleton-line.long   { width: 60%; height: 24px; }
.skeleton-line.medium { width: 70%; }
@keyframes shimmer { to { background-position: -200% 0; } }

/* Charts Row */
.charts-row { display: grid; grid-template-columns: 1fr 300px; gap: 16px; }
@media (max-width: 900px) { .charts-row { grid-template-columns: 1fr; } }

.card {
  background: white;
  border-radius: 14px;
  padding: 22px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  border: 1px solid #f1f5f9;
}
.card-header { margin-bottom: 18px; }
.card-title  { font-size: 15px; font-weight: 700; color: #0f172a; margin: 0; }

/* Bar chart */
.chart-wrap { display: flex; flex-direction: column; gap: 8px; }
.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 120px;
  overflow: hidden;
}
.bar-col { flex: 1; display: flex; align-items: flex-end; }
.bar {
  width: 100%;
  background: #2563eb;
  border-radius: 3px 3px 0 0;
  min-height: 2px;
  transition: height 0.5s ease;
  opacity: 0.8;
}
.bar:hover { opacity: 1; }
.chart-legend { display: flex; justify-content: space-between; font-size: 11px; color: #94a3b8; }
.empty-chart { text-align: center; color: #94a3b8; font-size: 13px; padding: 40px 0; }

/* Quick links */
.quick-links { display: flex; flex-direction: column; gap: 4px; }
.quick-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  transition: background 0.15s, color 0.15s;
}
.quick-link:hover { background: #eff6ff; color: #2563eb; }
.ql-icon { font-size: 18px; }
</style>
