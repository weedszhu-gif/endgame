/**
 * 前端WebSocket客户端示例 - 与Python后端通信
 * 
 * 这个示例展示了如何修改前端代码以连接Python后端的WebSocket服务
 * 原代码使用Cloudflare Workers，现在改为连接FastAPI后端
 */

class WebSocketService {
  constructor(url) {
    this.url = url;
    this.socket = null;
    this.callbacks = {};
  }
  
  connect() {
    // 连接到Python后端的WebSocket服务
    // 原代码: this.socket = new WebSocket('wss://your-worker.example.com');
    this.socket = new WebSocket(this.url);
    
    this.socket.onopen = () => {
      console.log('WebSocket连接已建立');
      if (this.callbacks.onOpen) {
        this.callbacks.onOpen();
      }
    };
    
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('收到消息:', data);
      if (this.callbacks.onMessage) {
        this.callbacks.onMessage(data);
      }
    };
    
    this.socket.onerror = (error) => {
      console.error('WebSocket错误:', error);
      if (this.callbacks.onError) {
        this.callbacks.onError(error);
      }
    };
    
    this.socket.onclose = () => {
      console.log('WebSocket连接已关闭');
      if (this.callbacks.onClose) {
        this.callbacks.onClose();
      }
    };
  }
  
  on(event, callback) {
    this.callbacks[event] = callback;
  }
  
  send(data) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(data));
      console.log('发送消息:', data);
    } else {
      console.error('WebSocket未连接');
    }
  }
  
  close() {
    if (this.socket) {
      this.socket.close();
    }
  }
}

// 使用示例
const wsService = new WebSocketService('ws://localhost:8000/ws');

// 连接到服务器
wsService.connect();

// 监听连接事件
wsService.on('onOpen', () => {
  console.log('连接成功，可以开始发送解题步骤');
  
  // 发送第一个解题步骤示例
  setTimeout(() => {
    wsService.send({
      type: 'step',
      content: '设x为书的价格'
    });
  }, 1000);
});

// 监听消息事件
wsService.on('onMessage', (data) => {
  if (data.type === 'hint') {
    console.log('收到提示:', data.content);
    
    // 这里可以将提示显示在界面上
    // showHint(data.content);
    
    // 示例：模拟用户继续发送下一个步骤
    setTimeout(() => {
      wsService.send({
        type: 'step',
        content: '根据题意，得到方程：2x + 5 = 15'
      });
    }, 2000);
  }
  
  if (data.type === 'error') {
    console.error('收到错误:', data.content);
  }
});

// 监听错误事件
wsService.on('onError', (error) => {
  console.error('WebSocket错误:', error);
});

// 监听关闭事件
wsService.on('onClose', () => {
  console.log('连接已关闭，尝试重新连接...');
  // 可以在这里实现重连逻辑
  setTimeout(() => {
    wsService.connect();
  }, 3000);
});

// 页面卸载时关闭连接
window.addEventListener('beforeunload', () => {
  wsService.close();
});

/**
 * 示例函数：显示提示
 * @param {string} hint - 提示内容
 */
function showHint(hint) {
  const hintElement = document.getElementById('hint-container');
  if (hintElement) {
    hintElement.textContent = hint;
    hintElement.style.display = 'block';
  }
}

/**
 * 示例函数：发送解题步骤
 * @param {string} step - 解题步骤内容
 */
function sendStep(step) {
  wsService.send({
    type: 'step',
    content: step
  });
}
