<!-- filepath: e:\1_work\PersonalProgram\PsyChat\0421PsyChat\frontend\src\views\ChatView.vue -->
<template>
  <div class="chat-container">
    <el-card class="chat-card">
      <template #header>
        <div class="chat-header">
          <h2>心理健康助手</h2>
        </div>
      </template>
      
      <div class="chat-messages" ref="messagesContainer">
        <div 
          v-for="(msg, index) in messages" 
          :key="index" 
          :class="['message', msg.role]"
        >
          <div class="message-content">{{ msg.content }}</div>
        </div>
        <div v-if="loading" class="message assistant">
          <div class="message-content loading">
            <span>思考中</span>
            <el-icon class="loading-icon"><Loading /></el-icon>
          </div>
        </div>
      </div>
      
      <div class="chat-input">
        <el-input
          v-model="userInput"
          type="textarea"
          :rows="2"
          placeholder="请输入您的问题或感受..."
          resize="none"
          @keydown.enter.prevent="sendMessage"
        />
        <el-button 
          type="primary" 
          :disabled="!userInput.trim() || loading" 
          @click="sendMessage"
        >
          发送
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, nextTick, onMounted } from 'vue';
import { Loading } from '@element-plus/icons-vue';
import api from '../services/api';
import { ElMessage } from 'element-plus';

export default {
  components: {
    Loading,
  },
  setup() {
    const messages = ref([
      { role: 'assistant', content: '你好！我是心理助手。请告诉我你想聊些什么？我会尽我所能为你提供支持和信息。' }
    ]);
    const userInput = ref('');
    const loading = ref(false);
    const messagesContainer = ref(null);

    const scrollToBottom = async () => {
      await nextTick();
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      }
    };

    const sendMessage = async () => {
      if (!userInput.value.trim() || loading.value) return;
      
      // Add user message
      const userMessage = userInput.value.trim();
      messages.value.push({ role: 'user', content: userMessage });
      userInput.value = '';
      scrollToBottom();
      
      // Set loading state
      loading.value = true;
      
      try {
        // Send to API
        const response = await api.sendMessage(userMessage);
        
        // Add assistant response
        messages.value.push({ 
          role: 'assistant', 
          content: response.data.response || '抱歉，我现在无法回答这个问题。'
        });
      } catch (error) {
        console.error('Error sending message:', error);
        ElMessage.error('发送消息失败，请稍后再试');
        messages.value.push({ 
          role: 'assistant', 
          content: '抱歉，发生了一个错误。请稍后再试。'
        });
      } finally {
        loading.value = false;
        scrollToBottom();
      }
    };

    onMounted(() => {
      scrollToBottom();
    });

    return {
      messages,
      userInput,
      loading,
      messagesContainer,
      sendMessage
    };
  }
}
</script>

<style scoped>
.chat-container {
  max-width: 800px;
  margin: 0 auto;
}

.chat-card {
  height: calc(100vh - 160px);
  display: flex;
  flex-direction: column;
}

.chat-header {
  text-align: center;
}

.chat-header h2 {
  margin: 0;
  color: #303133;
}

.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message {
  display: flex;
  margin-bottom: 10px;
}

.message.user {
  justify-content: flex-end;
}

.message-content {
  padding: 10px 15px;
  border-radius: 12px;
  max-width: 70%;
  word-break: break-word;
}

.user .message-content {
  background-color: #ecf5ff;
  color: #303133;
}

.assistant .message-content {
  background-color: #f5f7fa;
  color: #303133;
}

.loading .loading-icon {
  animation: rotating 2s linear infinite;
  margin-left: 6px;
}

.chat-input {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

@keyframes rotating {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>