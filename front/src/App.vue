<template>
  <div class="app-container">
    <!-- 全局导航栏 -->
    <GlobalNav>
      <template #left>
        <!-- 左侧内容由各个页面自定义 -->
      </template>
      <template #right>
        <!-- 右侧内容由各个页面自定义 -->
      </template>
    </GlobalNav>
    <!-- 主内容区域，添加顶部 padding 以避免被导航栏遮挡 -->
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUser } from './composables/useUser'
import GlobalNav from './components/GlobalNav.vue'

const { loadUsers, restoreUser, setDefaultUser } = useUser()

onMounted(async () => {
  // 恢复保存的用户状态
  restoreUser()
  // 加载用户列表
  await loadUsers()
  // 如果没有用户，设置默认用户（小刚）
  await setDefaultUser()
})
</script>

<style>
.app-container {
  min-height: 100vh;
}

.main-content {
  padding-top: 48px; /* 为全局导航栏留出空间 */
}
</style>

