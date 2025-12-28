import { ref, reactive } from 'vue'

// 全局用户状态
const currentUser = ref(null)
const users = ref([])

// 加载用户列表
const loadUsers = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/users')
    if (response.ok) {
      users.value = await response.json()
    }
  } catch (error) {
    console.error('加载用户列表失败:', error)
  }
}

// 设置当前用户
const setCurrentUser = (user) => {
  currentUser.value = user
  // 保存到 localStorage 以便刷新后保持
  if (user) {
    localStorage.setItem('currentUser', JSON.stringify(user))
  } else {
    localStorage.removeItem('currentUser')
  }
}

// 从 localStorage 恢复用户
const restoreUser = () => {
  try {
    const saved = localStorage.getItem('currentUser')
    if (saved) {
      currentUser.value = JSON.parse(saved)
    }
  } catch (error) {
    console.error('恢复用户状态失败:', error)
  }
}

// 设置默认用户（小刚）
const setDefaultUser = async () => {
  try {
    // 如果已经有用户，不设置默认值
    if (currentUser.value) {
      return
    }
    
    // 如果用户列表为空，先加载
    if (users.value.length === 0) {
      await loadUsers()
    }
    
    // 查找"小刚"用户（通过 nickname 或 username）
    const defaultUser = users.value.find(
      u => u.nickname === '小刚' || u.username === 'student3' || u.username === 'xiaogang'
    )
    
    if (defaultUser) {
      setCurrentUser(defaultUser)
      console.log('已设置默认用户：小刚')
    }
  } catch (error) {
    console.error('设置默认用户失败:', error)
  }
}

// 导出 composable
export function useUser() {
  return {
    currentUser,
    users,
    loadUsers,
    setCurrentUser,
    restoreUser,
    setDefaultUser
  }
}

