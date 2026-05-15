<template>
  <div v-if="modelValue" class="scan-modal">
    <div class="scan-box">
      <p>📡 Esperando código de barras...</p>

      <button @click="$emit('cancel')" class="btn-cancel">
        Cancelar
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    modelValue: Boolean // controla si se muestra
  },
  emits: ["cancel"]
};
</script>