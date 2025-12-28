<template>
  <nav class="global-nav">
    <div class="nav-container">
      <div class="nav-left">
        <slot name="left"></slot>
      </div>
      <div class="nav-right">
        <slot name="right"></slot>
        <!-- 全局用户选择器 - 紧凑样式 -->
        <div class="user-selector-compact">
          <select 
            v-model="selectedUserId" 
            @change="onUserChange"
            class="user-select-compact"
            :title="currentUser ? `当前用户：${currentUser.nickname || currentUser.username}` : '请选择用户'"
          >
            <option value="">选择用户</option>
            <option v-for="user in users" :key="user.id" :value="user.id">
              {{ user.nickname || user.username }}
            </option>
          </select>
          <div v-if="currentUser" class="current-user-compact" :title="`当前用户：${currentUser.nickname || currentUser.username}`">
            <i class="fas fa-check-circle"></i>
            <span>{{ currentUser.nickname || currentUser.username }}</span>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useUser } from '../composables/useUser'

const { currentUser, users, loadUsers, setCurrentUser } = useUser()
const selectedUserId = ref('')

// 用户选择变化
const onUserChange = () => {
  if (selectedUserId.value) {
    const userId = parseInt(selectedUserId.value)
    const user = users.value.find(u => u.id === userId)
    if (user) {
      setCurrentUser(user)
    }
  } else {
    setCurrentUser(null)
  }
}

// 监听全局用户变化，同步到本地选择
watch(currentUser, (newUser) => {
  if (newUser) {
    selectedUserId.value = newUser.id
  } else {
    selectedUserId.value = ''
  }
}, { immediate: true })

onMounted(async () => {
  await loadUsers()
  if (currentUser.value) {
    selectedUserId.value = currentUser.value.id
  } else {
    // 如果没有用户，尝试设置默认用户（小刚）
    const { setDefaultUser } = useUser()
    await setDefaultUser()
    if (currentUser.value) {
      selectedUserId.value = currentUser.value.id
    }
  }
})
</script>

<style scoped>
.global-nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.nav-container {
  max-width: 100%;
  margin: 0 auto;
  padding: 0.5rem 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 48px;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-selector-compact {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-select-compact {
  padding: 0.375rem 0.625rem;
  padding-right: 2rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background: white;
  font-size: 0.8125rem;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 100px;
  max-width: 150px;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23374151' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 0.75rem;
}

.user-select-compact:hover {
  border-color: #667eea;
  background-color: #f9fafb;
}

.user-select-compact:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.current-user-compact {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  color: #059669;
  font-weight: 500;
  white-space: nowrap;
  padding: 0.25rem 0.5rem;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 4px;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.current-user-compact i {
  color: #10b981;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.current-user-compact span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

