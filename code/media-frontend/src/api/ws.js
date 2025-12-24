export function openStoryWS({ storyId, onMessage, onOpen, onClose, onError }) {
  // 开发阶段直接连后端，避免 WebSocket proxy 问题
  const ws = new WebSocket(`ws://127.0.0.1:8000/ws/story/${storyId}`)

  ws.onopen = () => {
    if (onOpen) onOpen()
  }

  ws.onclose = () => {
    if (onClose) onClose()
  }

  ws.onerror = (e) => {
    if (onError) onError(e)
  }

  ws.onmessage = (evt) => {
    try {
      const data = JSON.parse(evt.data)
      if (onMessage) onMessage(data)
    } catch (err) {
      // 避免 ESLint no-empty 报错，同时保留调试信息
      console.warn('[WS] Received non-JSON message:', evt.data)
    }
  }

  return ws
}
