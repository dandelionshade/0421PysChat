<!-- This is the main chat interface component view -->
<template>
  <!-- Main container for the chat interface with CSS class 'chat-container' -->
  <div class="chat-container">
    <!-- Element Plus card component to create a styled container for the chat -->
    <el-card class="chat-card">
      <!-- The card header section containing the title -->
      <template #header>
        <!-- Header container with CSS class 'chat-header' -->
        <div class="chat-header">
          <!-- The title of the chat application -->
          <h2>心理健康助手</h2>
          <!-- 新增: 会话控制按钮 -->
          <div class="session-controls">
            <el-tooltip content="开始新对话" placement="top">
              <el-button 
                type="primary" 
                plain 
                circle 
                icon="Plus" 
                @click="startNewSession" 
                :disabled="loading"
              ></el-button>
            </el-tooltip>
          </div>
        </div>
      </template>
      
      <!-- Container for chat messages with a reference to access it in JavaScript -->
      <div class="chat-messages" ref="messagesContainer">
        <!-- Loop through each message in the messages array -->
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          :class="['message', msg.role]"
        >
          <!-- Display the content of each message -->
          <div class="message-content">{{ msg.content }}</div>
          
          <!-- 新增: 用户反馈按钮 (仅显示在AI回复上) -->
          <div v-if="msg.role === 'assistant'" class="message-feedback">
            <el-tooltip content="这个回答有帮助" placement="top">
              <el-button 
                type="success" 
                size="small" 
                circle 
                icon="ThumbUp" 
                @click="provideFeedback(index, 'positive')"
              ></el-button>
            </el-tooltip>
            <el-tooltip content="这个回答没帮助" placement="top">
              <el-button 
                type="danger" 
                size="small" 
                circle 
                icon="ThumbDown" 
                @click="provideFeedback(index, 'negative')"
              ></el-button>
            </el-tooltip>
          </div>
        </div>
        
        <!-- Show loading indicator when waiting for AI response -->
        <div v-if="loading" class="message assistant">
          <!-- Loading message with animation -->
          <div class="message-content loading">
            <!-- Loading text -->
            <span>思考中</span>
            <!-- Element Plus loading icon with animation -->
            <el-icon class="loading-icon"><Loading /></el-icon>
          </div>
        </div>
      </div>
      
      <!-- Input area for user to type and send messages -->
      <div class="chat-input">
        <!-- Textarea for user to input messages -->
        <el-input
          v-model="userInput"
          type="textarea"
          :rows="2"
          placeholder="请输入您的问题或感受..."
          resize="none"
          @keydown.enter.prevent="sendMessage"
          :disabled="loading"
        />
        <!-- Button to send the message -->
        <el-button 
          type="primary"
          :disabled="!userInput.trim() || loading"
          @click="sendMessage"
          :loading="loading"
        >
          <!-- Button text -->
          发送
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
// Import necessary functions from Vue
import { ref, nextTick, onMounted } from 'vue';
// Import loading icon from Element Plus
import { Loading } from '@element-plus/icons-vue';
// Import API service for backend communication
import api from '../services/api';
// Import Element Plus message notification component
import { ElMessage } from 'element-plus';
// 新增: 导入会话存储服务
import { saveSession, loadSession, generateSessionId } from '../services/sessionStorage';

// Define and export the component
export default {
  // Register components used in the template
  components: {
    Loading,
  },
  // Setup function defines component logic and returns data to the template
  setup() {
    // 新增: 会话ID，用于关联后端会话和本地存储
    const sessionId = ref(generateSessionId());
    // Create a reactive array of message objects with initial welcome message
    const messages = ref([
      { role: 'assistant', content: '你好！我是心理助手。请告诉我你想聊些什么？我会尽我所能为你提供支持和信息。' }
    ]);
    // Reactive variable to store user input text
    const userInput = ref('');
    // Reactive boolean to track loading state
    const loading = ref(false);
    // Reference to the messages container DOM element
    const messagesContainer = ref(null);
    // 新增: 错误重试计数
    const retryCount = ref(0);
    // 新增: 最大重试次数
    const MAX_RETRIES = 3;

    // Function to scroll the chat to the bottom after new messages
    const scrollToBottom = async () => {
      await nextTick();
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      }
    };

    // 新增: 保存当前会话到本地存储
    const saveCurrentSession = () => {
      saveSession(sessionId.value, messages.value);
    };

    // 新增: 从本地存储加载会话
    const loadSavedSession = () => {
      const savedSession = loadSession(sessionId.value);
      if (savedSession && savedSession.messages && savedSession.messages.length > 0) {
        messages.value = savedSession.messages;
        nextTick(() => scrollToBottom());
        return true;
      }
      return false;
    };

    // 新增: 开始新会话
    const startNewSession = () => {
      if (loading.value) return;
      
      // 确认是否保存当前会话
      ElMessage({
        message: '正在开始新对话...',
        type: 'info',
        duration: 1500
      });
      
      // 生成新的会话ID
      sessionId.value = generateSessionId();
      
      // 重置消息列表，只保留欢迎消息
      messages.value = [
        { role: 'assistant', content: '你好！我是心理助手。请告诉我你想聊些什么？我会尽我所能为你提供支持和信息。' }
      ];
      
      // 保存新会话
      saveCurrentSession();
      
      // 滚动到底部
      scrollToBottom();
    };

    // Function to send user message and get AI response
    const sendMessage = async () => {
      // Exit early if input is empty or already loading
      if (!userInput.value.trim() || loading.value) return;
      
      // Get the trimmed message text
      const userMessage = userInput.value.trim();
      // Add user message to the messages array
      messages.value.push({ role: 'user', content: userMessage });
      // Clear the input field
      userInput.value = '';
      // Scroll to the bottom to show the new message
      scrollToBottom();
      // 保存当前会话状态
      saveCurrentSession();
      
      // Set loading state to true while waiting for response
      loading.value = true;
      retryCount.value = 0;
      
      try {
        // Send message to backend API and wait for response
        const response = await api.sendMessage(userMessage, sessionId.value);
        
        // Add AI assistant response to messages array
        messages.value.push({ 
          role: 'assistant', 
          content: response.data.response || '抱歉，我现在无法回答这个问题。'
        });
        
        // 保存更新后的会话
        saveCurrentSession();
      } catch (error) {
        console.error('Error sending message:', error);
        
        // 新增: 实现自动重试逻辑
        if (retryCount.value < MAX_RETRIES) {
          retryCount.value++;
          
          ElMessage({
            message: `连接问题，正在进行第${retryCount.value}次重试...`,
            type: 'warning',
            duration: 2000
          });
          
          // 延迟重试，避免立即发送请求
          setTimeout(() => {
            loading.value = false;
            sendMessage();
          }, 1000 * retryCount.value);
          return;
        }
        
        // Show error notification to user
        ElMessage.error('发送消息失败，请稍后再试');
        // Add error message in chat
        messages.value.push({ 
          role: 'assistant', 
          content: '抱歉，发生了一个错误。请稍后再试。'
        });
        
        // 保存会话，包括错误信息
        saveCurrentSession();
      } finally {
        // Set loading to false regardless of success or failure
        if (retryCount.value === 0 || retryCount.value >= MAX_RETRIES) {
          loading.value = false;
        }
        // Scroll chat to bottom to show the new message
        scrollToBottom();
      }
    };

    // 新增: 提供反馈功能
    const provideFeedback = (messageIndex, feedbackType) => {
      ElMessage({
        message: '感谢您的反馈！',
        type: feedbackType === 'positive' ? 'success' : 'info',
        duration: 1500
      });
      
      // 此处可以添加向后端发送反馈的逻辑
      // 例如: api.sendFeedback(messageIndex, feedbackType, sessionId.value);
    };

    // When component is mounted, scroll to bottom to show welcome message
    onMounted(() => {
      // 尝试加载保存的会话
      const sessionLoaded = loadSavedSession();
      
      if (!sessionLoaded) {
        // 如果没有找到保存的会话，保存当前会话（包含欢迎消息）
        saveCurrentSession();
      }
      
      scrollToBottom();
    });

    // Return data and functions to make them available in the template
    return {
      messages,
      userInput,
      loading,
      messagesContainer,
      sendMessage,
      startNewSession,
      provideFeedback
    };
  }
}
</script>

<style scoped>
/* 保留现有样式 */
/* Container for the entire chat interface */
.chat-container {
  max-width: 800px;    /* Limit the width for better readability */
  margin: 0 auto;      /* Center the container horizontally */
}

/* Styling for the card that contains the chat */
.chat-card {
  height: calc(100vh - 160px);  /* Make card take most of the viewport height */
  display: flex;                /* Use flexbox for layout */
  flex-direction: column;       /* Stack children vertically */
}

/* Styling for the chat header section */
.chat-header {
  display: flex;         /* 使用弹性布局 */
  justify-content: space-between; /* 在标题和控制按钮之间均匀分布空间 */
  align-items: center;   /* 垂直居中对齐 */
}

/* Styling for the title in the header */
.chat-header h2 {
  margin: 0;           /* Remove default margins */
  color: #303133;      /* Dark gray color for the title */
}

/* Container for all chat messages */
.chat-messages {
  flex-grow: 1;          /* Allow this element to expand and fill available space */
  overflow-y: auto;      /* Add vertical scrollbar when content overflows */
  padding: 10px;         /* Add space around the content */
  display: flex;         /* Use flexbox for layout */
  flex-direction: column;/* Stack messages vertically */
  gap: 10px;             /* Add spacing between messages */
}

/* Individual message container */
.message {
  display: flex;         /* Use flexbox for layout */
  margin-bottom: 10px;   /* Add space below each message */
  position: relative;    /* 为反馈按钮的定位做准备 */
}

/* User message alignment (right side) */
.message.user {
  justify-content: flex-end;  /* Align user messages to the right */
}

/* Styling for message bubble content */
.message-content {
  padding: 10px 15px;     /* Add space inside the bubble */
  border-radius: 12px;    /* Round the corners */
  max-width: 70%;         /* Limit width to 70% of container */
  word-break: break-word; /* Allow long words to break to prevent overflow */
}

/* Styling specifically for user message bubbles */
.user .message-content {
  background-color: #ecf5ff;  /* Light blue background */
  color: #303133;             /* Dark text color */
}

/* Styling specifically for assistant message bubbles */
.assistant .message-content {
  background-color: #f5f7fa;  /* Light gray background */
  color: #303133;             /* Dark text color */
}

/* Styling for the loading animation */
.loading .loading-icon {
  animation: rotating 2s linear infinite;  /* Apply rotating animation */
  margin-left: 6px;                       /* Add space to the left of the icon */
}

/* Container for the input area */
.chat-input {
  margin-top: 20px;   /* Add space above the input area */
  display: flex;      /* Use flexbox for layout */
  gap: 10px;          /* Add space between input and button */
}

/* 新增: 反馈按钮样式 */
.message-feedback {
  position: absolute;  /* 绝对定位 */
  right: -70px;        /* 位于消息气泡右侧 */
  top: 50%;            /* 垂直居中 */
  transform: translateY(-50%); /* 精确垂直居中 */
  display: flex;       /* 弹性布局 */
  flex-direction: column; /* 垂直排列按钮 */
  gap: 5px;            /* 按钮之间的间距 */
  opacity: 0;          /* 默认隐藏 */
  transition: opacity 0.3s ease; /* 平滑过渡效果 */
}

/* 鼠标悬停时显示反馈按钮 */
.message:hover .message-feedback {
  opacity: 1;
}

/* 会话控制按钮样式 */
.session-controls {
  display: flex;       /* 弹性布局 */
  gap: 10px;           /* 按钮之间的间距 */
}

/* Keyframe animation for the loading spinner */
@keyframes rotating {
  from {
    transform: rotate(0deg);    /* Start rotation from 0 degrees */
  }
  to {
    transform: rotate(360deg);  /* End rotation at 360 degrees (full circle) */
  }
}

/* 媒体查询：移动设备适配 */
@media (max-width: 768px) {
  .message-feedback {
    position: static;     /* 在移动设备上改为静态定位 */
    opacity: 1;           /* 始终显示 */
    flex-direction: row;  /* 水平排列按钮 */
    justify-content: flex-end; /* 靠右对齐 */
    margin-top: 5px;      /* 与消息之间的间距 */
  }
  
  .message-content {
    max-width: 85%;       /* 移动设备上消息气泡可以稍宽一些 */
  }
  
  .chat-input {
    flex-direction: column; /* 输入框和按钮垂直排列 */
  }
}
</style>