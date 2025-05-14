/**
 * 会话存储服务
 * 负责管理聊天会话的本地存储，使用localStorage实现聊天历史的持久化
 */

// 存储会话数据到localStorage
export const saveSession = (sessionId, messages) => {
  try {
    localStorage.setItem(`chat_session_${sessionId}`, JSON.stringify({
      id: sessionId,
      messages,
      lastUpdated: new Date().toISOString()
    }));
    return true;
  } catch (error) {
    console.error('Error saving session to localStorage:', error);
    return false;
  }
};

// 从localStorage加载会话数据
export const loadSession = (sessionId) => {
  try {
    const sessionData = localStorage.getItem(`chat_session_${sessionId}`);
    return sessionData ? JSON.parse(sessionData) : null;
  } catch (error) {
    console.error('Error loading session from localStorage:', error);
    return null;
  }
};

// 获取所有会话ID列表
export const getSessionsList = () => {
  try {
    const sessions = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key.startsWith('chat_session_')) {
        const sessionId = key.replace('chat_session_', '');
        const sessionData = JSON.parse(localStorage.getItem(key));
        sessions.push({
          id: sessionId,
          lastUpdated: sessionData.lastUpdated,
          messageCount: sessionData.messages.length
        });
      }
    }
    // 按最后更新时间排序，最新的在前面
    return sessions.sort((a, b) => new Date(b.lastUpdated) - new Date(a.lastUpdated));
  } catch (error) {
    console.error('Error getting sessions list:', error);
    return [];
  }
};

// 删除会话
export const deleteSession = (sessionId) => {
  try {
    localStorage.removeItem(`chat_session_${sessionId}`);
    return true;
  } catch (error) {
    console.error('Error deleting session:', error);
    return false;
  }
};

// 生成新的会话ID
export const generateSessionId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substring(2);
};
