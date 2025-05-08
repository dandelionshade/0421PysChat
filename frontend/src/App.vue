<!--
 * @Author: zhen doniajohary2677@gmail.com
 * @Date: 2025-04-29 16:43:30
 * @LastEditors: zhen doniajohary2677@gmail.com
 * @LastEditTime: 2025-04-29 16:43:54
 * @FilePath: \0421PsyChat\frontend\src\App.vue
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
<!-- This is the root App component that serves as the application shell -->
<template>
  <!-- Element Plus config provider for global configuration -->
  <el-config-provider>
    <!-- Main application container with CSS class 'app-container' -->
    <div class="app-container">
      <!-- Application header containing logo and navigation -->
      <header class="app-header">
        <!-- Logo container -->
        <div class="logo">
          <!-- Application title -->
          <h1>PsyChat</h1>
        </div>
        <!-- Navigation menu with router links -->
        <nav>
          <!-- Link to chat page - becomes active when route matches -->
          <router-link to="/chat">聊天</router-link>
          <!-- Link to resources page - becomes active when route matches -->
          <router-link to="/resources">资源</router-link>
        </nav>
      </header>
      
      <!-- Main content area where page components are rendered -->
      <main class="app-main">
        <!-- Router view renders the component matching the current route -->
        <router-view />
      </main>
      
      <!-- Application footer with copyright information -->
      <footer class="app-footer">
        <!-- Copyright text and application description -->
        <p>© 2025 PsyChat - 基于RAG的心理健康助手</p>
      </footer>
    </div>
  </el-config-provider>
</template>

<style>
/* Reset margin and set global font family */
body {
  margin: 0;  /* Remove default margin */
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;  /* Font stack with Chinese support */
}

/* Container for the entire application */
.app-container {
  display: flex;          /* Use flexbox for layout */
  flex-direction: column; /* Stack children vertically */
  min-height: 100vh;      /* Take at least full viewport height */
}

/* Styling for the application header */
.app-header {
  display: flex;               /* Use flexbox for layout */
  justify-content: space-between; /* Space items at the ends */
  align-items: center;         /* Center items vertically */
  padding: 0 20px;             /* Add horizontal padding */
  height: 60px;                /* Fixed height for header */
  background-color: #fff;      /* White background */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow for depth */
}

/* Styling for the logo heading */
.logo h1 {
  margin: 0;           /* Remove default margin */
  font-size: 24px;     /* Larger text size */
  color: #409eff;      /* Blue color matching Element Plus theme */
}

/* Styling for the navigation menu */
nav {
  display: flex;    /* Use flexbox for layout */
  gap: 20px;        /* Add space between navigation links */
}

/* Styling for navigation links */
nav a {
  text-decoration: none;  /* Remove underline */
  color: #606266;         /* Medium gray color */
  font-weight: bold;      /* Bold text */
}

/* Styling for active navigation link */
nav a.router-link-active {
  color: #409eff;  /* Blue color for active link */
}

/* Styling for the main content area */
.app-main {
  flex-grow: 1;            /* Allow to expand and fill available space */
  padding: 20px;           /* Add space around content */
  background-color: #f5f7fa; /* Light gray background */
}

/* Styling for the application footer */
.app-footer {
  text-align: center;      /* Center the text */
  padding: 15px 0;         /* Add vertical padding */
  background-color: #fff;  /* White background */
  border-top: 1px solid #eaeaea; /* Light gray top border */
  color: #909399;          /* Light gray text color */
  font-size: 14px;         /* Smaller text size */
}
</style>