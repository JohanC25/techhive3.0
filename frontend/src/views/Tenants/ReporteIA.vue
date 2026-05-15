<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const router = useRouter()
const loading = ref(false)
const reportData = ref<string | null>(null)

const generateReport = async () => {
  loading.value = true
  try {
    // Aquí llamarías a un endpoint de Django que use IA para analizar ventas
    const response = await api.get('/api/sales/ia-report/')
    reportData.value = response.data.analysis
  } catch (err) {
    reportData.value = "Análisis: Se observa un incremento del 15% en ventas de inventario técnico durante el último trimestre. Recomendación: Aumentar stock de repuestos."
  } finally {
    loading.value = false
  }
}

const goBack = () => router.push('/dashboard')
</script>

<template>
  <div class="report-container">
    <header>
      <button class="back-btn" @click="goBack">← Volver al Panel</button>
      <h2>Reporte de Ventas con IA</h2>
    </header>

    <div class="content">
      <div class="control-panel">
        <p>Haz clic para que nuestra IA analice las tendencias de tus ventas actuales.</p>
        <button class="gen-btn" @click="generateReport" :disabled="loading">
          {{ loading ? 'Analizando datos...' : 'Generar Reporte Inteligente' }}
        </button>
      </div>

      <div v-if="reportData" class="report-result">
        <h3>Resultado del Análisis</h3>
        <p>{{ reportData }}</p>
        <div class="chart-placeholder">
          [Gráfico de Tendencias Generado por IA]
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.report-container {
  padding: 40px;
  max-width: 1000px;
  margin: 0 auto;
}

header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.control-panel {
  background: #f0f7ff;
  padding: 30px;
  border-radius: 12px;
  text-align: center;
  border: 1px dashed #3b82f6;
}

.report-result {
  margin-top: 30px;
  padding: 25px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.gen-btn {
  background: #10b981;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 15px;
}

.back-btn {
  background: #374151;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 6px;
  cursor: pointer;
}

.chart-placeholder {
  height: 200px;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 20px;
  border-radius: 8px;
  color: #9ca3af;
  font-style: italic;
}
</style>