// API 配置
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8765'
const WS_RECONNECT_INTERVAL = 3000
const WS_MAX_RECONNECT_ATTEMPTS = 5

/**
 * WebSocket 服务类
 * 用于管理与后端的 WebSocket 连接
 */
export class WebSocketService {
  constructor() {
    this.ws = null
    this.url = WS_URL
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = WS_MAX_RECONNECT_ATTEMPTS
    this.reconnectInterval = WS_RECONNECT_INTERVAL
    this.listeners = new Map()
    this.isConnecting = false
    this.shouldReconnect = true
  }

  /**
   * 连接 WebSocket
   */
  connect() {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return Promise.resolve()
    }

    this.isConnecting = true
    this.shouldReconnect = true

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url)

        this.ws.onopen = () => {
          console.log('WebSocket 连接成功')
          this.isConnecting = false
          this.reconnectAttempts = 0
          this.emit('open')
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            this.handleMessage(data)
          } catch (error) {
            console.error('解析 WebSocket 消息失败:', error)
            this.emit('error', { type: 'parse_error', error })
          }
        }

        this.ws.onerror = (error) => {
          console.error('WebSocket 错误:', error)
          this.isConnecting = false
          this.emit('error', { type: 'connection_error', error })
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('WebSocket 连接关闭')
          this.isConnecting = false
          this.emit('close')

          // 自动重连
          if (this.shouldReconnect && this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++
            console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
            setTimeout(() => {
              this.connect()
            }, this.reconnectInterval)
          } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('达到最大重连次数，停止重连')
            this.emit('max_reconnect_reached')
          }
        }
      } catch (error) {
        this.isConnecting = false
        reject(error)
      }
    })
  }

  /**
   * 处理接收到的消息
   */
  handleMessage(data) {
    const { type } = data

    switch (type) {
      case 'system':
        this.emit('system', data)
        break
      case 'status':
        this.emit('status', data)
        break
      case 'ai_response_start':
        this.emit('ai_response_start', data)
        break
      case 'ai_response_chunk':
        this.emit('ai_response_chunk', data)
        break
      case 'ai_response_end':
        this.emit('ai_response_end', data)
        break
      case 'error':
        this.emit('error', data)
        break
      case 'history':
        this.emit('history', data)
        break
      default:
        console.warn('未知的消息类型:', type)
        this.emit('message', data)
    }
  }

  /**
   * 发送消息
   */
  send(type, message) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket 未连接，无法发送消息')
      return false
    }

    try {
      const data = {
        type,
        message: typeof message === 'string' ? message : JSON.stringify(message),
        ...(typeof message === 'object' ? message : {})
      }
      this.ws.send(JSON.stringify(data))
      return true
    } catch (error) {
      console.error('发送消息失败:', error)
      return false
    }
  }

  /**
   * 发送聊天消息（请求 AI 提示）
   */
  sendChatMessage(userInput, question) {
    const prompt = this.buildHintPrompt(question, userInput)
    return this.send('chat', prompt)
  }

  /**
   * 构建提示词
   */
  buildHintPrompt(question, userInput) {
    return `你是一个数学解题助手。请根据学生的解题步骤，给出适当的提示，帮助他们解决这道数学题。

题目：${question}

学生当前的解题步骤：
${userInput || '（学生还没有开始解题）'}

请给出简洁、鼓励的提示，不要直接给出答案，而是引导学生思考。如果学生还没有开始解题，请给出如何开始的建议。`
  }

  /**
   * 重置会话
   */
  resetSession() {
    return this.send('reset')
  }

  /**
   * 获取历史记录
   */
  getHistory() {
    return this.send('history')
  }

  /**
   * 断开连接
   */
  disconnect() {
    this.shouldReconnect = false
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  /**
   * 事件监听
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  /**
   * 移除事件监听
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  /**
   * 触发事件
   */
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error(`事件回调执行失败 (${event}):`, error)
        }
      })
    }
  }

  /**
   * 获取连接状态
   */
  getState() {
    if (!this.ws) return 'CLOSED'
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING'
      case WebSocket.OPEN:
        return 'OPEN'
      case WebSocket.CLOSING:
        return 'CLOSING'
      case WebSocket.CLOSED:
        return 'CLOSED'
      default:
        return 'UNKNOWN'
    }
  }

  /**
   * 检查是否已连接
   */
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

// 导出单例
export default new WebSocketService()

