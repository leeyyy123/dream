<template>
  <component
    :is="iconComponent"
    :class="iconClasses"
  />
</template>

<script setup>
import { computed } from 'vue'
import * as ElementPlusIcons from '@element-plus/icons-vue'

const props = defineProps({
  name: {
    type: String,
    required: true
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value)
  }
})

const iconComponent = computed(() => {
  return ElementPlusIcons[props.name] || ElementPlusIcons.QuestionFilled
})

const iconClasses = computed(() => {
  return ['app-icon', `app-icon-${props.size}`]
})
</script>

<style scoped>
.app-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.app-icon-xs {
  width: 14px;
  height: 14px;
}

.app-icon-sm {
  width: 16px;
  height: 16px;
}

.app-icon-md {
  width: 20px;
  height: 20px;
}

.app-icon-lg {
  width: 24px;
  height: 24px;
}

.app-icon-xl {
  width: 32px;
  height: 32px;
}

.app-icon-2xl {
  width: 40px;
  height: 40px;
}

.app-icon-3xl {
  width: 48px;
  height: 48px;
}
</style>
