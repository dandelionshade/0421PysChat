<!--
 * @Author: zhen doniajohary2677@gmail.com
 * @Date: 2025-04-29 16:43:30
 * @LastEditors: zhen doniajohary2677@gmail.com
 * @LastEditTime: 2025-04-29 16:43:54
 * @FilePath: \0421PsyChat\frontend\src\App.vue
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->
<!-- filepath: e:\1_work\PersonalProgram\PsyChat\0421PsyChat\frontend\src\App.vue -->
<template>
  <el-config-provider>
    <div class="app-container">
      <header class="app-header">
        <div class="logo">
          <h1>PsyChat</h1>
        </div>
        <nav>
          <router-link to="/chat">聊天</router-link>
          <router-link to="/resources">资源</router-link>
        </nav>
      </header>
      
      <main class="app-main">
        <router-view />
      </main>
      
      <footer class="app-footer">
        <p>© 2025 PsyChat - 基于RAG的心理健康助手</p>
      </footer>
    </div>
  </el-config-provider>
</template>

<style>
body {
  margin: 0;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.logo h1 {
  margin: 0;
  font-size: 24px;
  color: #409eff;
}

nav {
  display: flex;
  gap: 20px;
}

nav a {
  text-decoration: none;
  color: #606266;
  font-weight: bold;
}

nav a.router-link-active {
  color: #409eff;
}

.app-main {
  flex-grow: 1;
  padding: 20px;
  background-color: #f5f7fa;
}

.app-footer {
  text-align: center;
  padding: 15px 0;
  background-color: #fff;
  border-top: 1px solid #eaeaea;
  color: #909399;
  font-size: 14px;
}
</style>