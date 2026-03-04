import { ref } from 'vue'
import { defineStore } from 'pinia'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: number
  message: string
  type: ToastType
}

export const useToastStore = defineStore('toast', () => {
  const toasts = ref<Toast[]>([])

  function add(message: string, type: ToastType = 'success', duration = 3500) {
    const id = Date.now()
    toasts.value.push({ id, message, type })
    setTimeout(() => remove(id), duration)
  }

  function remove(id: number) {
    const idx = toasts.value.findIndex((t) => t.id === id)
    if (idx > -1) toasts.value.splice(idx, 1)
  }

  const success = (msg: string) => add(msg, 'success')
  const error = (msg: string) => add(msg, 'error', 5000)
  const warning = (msg: string) => add(msg, 'warning')
  const info = (msg: string) => add(msg, 'info')

  return { toasts, add, remove, success, error, warning, info }
})
