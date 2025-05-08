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
        <!-- Binds the input value to userInput variable -->
        <!-- Makes this a multi-line text input -->
        <!-- Sets the height to 2 rows -->
        <!-- Placeholder text shown when empty -->
        <!-- Prevents manual resizing -->
        <!-- Sends message when Enter is pressed -->
        <el-input
          v-model="userInput"
          type="textarea"
          :rows="2"
          placeholder="请输入您的问题或感受..."
          resize="none"
          @keydown.enter.prevent="sendMessage"
        />
        <!-- Button to send the message -->
        <!-- Sets button style to primary (blue) -->
        <!-- Disables button when input is empty or loading -->
        <!-- Calls sendMessage function when clicked -->
        <el-button 
          type="primary"
          :disabled="!userInput.trim() || loading"
          @click="sendMessage"
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

// Define and export the component
export default {
  // Register components used in the template
  components: {
    Loading,   // Register the Loading icon component
  },
  // Setup function defines component logic and returns data to the template
  setup() {
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

    // Function to scroll the chat to the bottom after new messages
    const scrollToBottom = async () => {
      // Wait for DOM to update
      await nextTick();
      // If the container exists, scroll to the bottom
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
      }
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
      
      // Set loading state to true while waiting for response
      loading.value = true;
      
      try {
        // Send message to backend API and wait for response
        const response = await api.sendMessage(userMessage);
        
        // Add AI assistant response to messages array
        messages.value.push({ 
          role: 'assistant', 
          content: response.data.response || '抱歉，我现在无法回答这个问题。'
        });
      } catch (error) {
        // Log error to console
        console.error('Error sending message:', error);
        // Show error notification to user
        ElMessage.error('发送消息失败，请稍后再试');
        // Add error message in chat
        messages.value.push({ 
          role: 'assistant', 
          content: '抱歉，发生了一个错误。请稍后再试。'
        });
      } finally {
        // Set loading to false regardless of success or failure
        loading.value = false;
        // Scroll chat to bottom to show the new message
        scrollToBottom();
      }
    };

    // When component is mounted, scroll to bottom to show welcome message
    onMounted(() => {
      scrollToBottom();
    });

    // Return data and functions to make them available in the template
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
  text-align: center;    /* Center the title text */
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

/* Keyframe animation for the loading spinner */
@keyframes rotating {
  from {
    transform: rotate(0deg);    /* Start rotation from 0 degrees */
  }
  to {
    transform: rotate(360deg);  /* End rotation at 360 degrees (full circle) */
  }
}
</style>