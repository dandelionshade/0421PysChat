-- PsyChat 数据库初始化脚本
-- 本脚本创建必要的数据库、表结构和初始数据

-- 创建数据库
CREATE DATABASE IF NOT EXISTS psychat CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE psychat;

-- 创建心理健康资源表
CREATE TABLE IF NOT EXISTS resources (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(50),
  location_tag VARCHAR(50),
  contact_info VARCHAR(255),
  url VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  -- 添加索引以提高筛选性能
  INDEX idx_category (category),
  INDEX idx_location (location_tag),
  INDEX idx_created (created_at)
);

-- 插入示例资源数据
INSERT INTO resources (title, description, category, location_tag, contact_info, url)
VALUES 
('全国心理援助热线', '提供24小时心理支持和危机干预', 'crisis', 'national', '400-161-9995', 'https://example.com/hotline'),
('心理健康咨询中心', '提供专业心理咨询服务', 'counseling', 'beijing', '010-12345678', 'https://example.com/center'),
('抑郁症自助小组', '抑郁症患者互助社区', 'support', 'online', 'depression@example.com', 'https://example.com/depression'),
('冥想与放松技巧课程', '学习减压和情绪管理技巧', 'self-help', 'shanghai', '021-87654321', 'https://example.com/meditation'),
('心理健康公益讲座', '免费心理健康教育', 'education', 'guangzhou', 'lectures@example.com', 'https://example.com/lectures'),
('青少年心理辅导热线', '专为青少年提供心理支持和辅导', 'crisis', 'national', '400-888-9999', 'https://example.com/youth-hotline'),
('线上心理健康自测工具', '提供常见心理问题初步自测和建议', 'self-help', 'online', 'tools@example.com', 'https://example.com/assessment');

-- 创建用户反馈表
CREATE TABLE IF NOT EXISTS feedback (
  id INT AUTO_INCREMENT PRIMARY KEY,
  message_id VARCHAR(36) NOT NULL,
  user_query TEXT NOT NULL,
  bot_response TEXT NOT NULL,
  rating TINYINT,
  comment TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  -- 添加索引
  INDEX idx_message_id (message_id),
  INDEX idx_rating (rating)
);

-- 创建聊天会话表 (支持聊天历史功能)
CREATE TABLE IF NOT EXISTS chat_sessions (
  id VARCHAR(36) PRIMARY KEY,
  name VARCHAR(255),           -- 会话名称，可以是基于第一条消息自动生成的
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_created (created_at)
);

-- 创建聊天消息表 (支持聊天历史功能)
CREATE TABLE IF NOT EXISTS chat_messages (
  id VARCHAR(36) PRIMARY KEY,
  session_id VARCHAR(36) NOT NULL,
  role ENUM('user', 'assistant') NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  INDEX idx_session (session_id),
  FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
);

-- 创建数据库用户并授权 (仅生产环境使用，开发环境可注释掉)
-- CREATE USER IF NOT EXISTS 'psychat_app'@'%' IDENTIFIED BY 'StrongPasswordHere';
-- GRANT SELECT, INSERT, UPDATE, DELETE ON psychat.* TO 'psychat_app'@'%';
-- FLUSH PRIVILEGES;