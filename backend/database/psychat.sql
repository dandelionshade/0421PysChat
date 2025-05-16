-- PsyChat 数据库初始化脚本 (MVP Version)
-- 本脚本创建必要的数据库、表结构和初始数据

-- 如果存在同名数据库，则删除重建
DROP DATABASE IF EXISTS psychat;

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

-- 用户反馈表 (REMOVED FOR MVP)
-- CREATE TABLE IF NOT EXISTS feedback (
--   ...
-- );

-- 聊天会话表 (REMOVED FOR MVP - Session management will be client-side for MVP)
-- CREATE TABLE IF NOT EXISTS chat_sessions (
--   ...
-- );

-- 聊天消息表 (REMOVED FOR MVP - Message history beyond current local session not stored in DB for MVP)
-- CREATE TABLE IF NOT EXISTS chat_messages (
--   ...
-- );

-- =============================================
-- 生产环境配置 (Simplified for MVP)
-- =============================================

-- 创建数据库用户并设置权限 (生产环境使用)
-- 注意: 在实际部署时替换为强密码并使用环境变量或密钥管理系统存储
CREATE USER IF NOT EXISTS 'psychat_app'@'%' IDENTIFIED BY 'StrongPasswordHere_MVP';

-- 应用服务账户 - 只有必要权限
GRANT SELECT, INSERT, UPDATE, DELETE ON psychat.resources TO 'psychat_app'@'%';
-- Removed grants for feedback, chat_sessions, chat_messages

-- 只读账户 (Optional for MVP, can be removed if not immediately needed)
-- CREATE USER IF NOT EXISTS 'psychat_readonly'@'%' IDENTIFIED BY 'ReadOnlyPasswordHere_MVP';
-- GRANT SELECT ON psychat.resources TO 'psychat_readonly'@'%';

FLUSH PRIVILEGES;

-- =============================================
-- 表优化 (生产环境)
-- =============================================
ALTER TABLE resources ROW_FORMAT=COMPRESSED KEY_BLOCK_SIZE=8;

-- 系统指标和数据库版本跟踪表 (REMOVED FOR MVP)
-- CREATE TABLE IF NOT EXISTS system_metrics (
--   ...
-- );
-- CREATE TABLE IF NOT EXISTS db_version (
--   ...
-- );
-- INSERT INTO db_version (version, description) VALUES ('1.0.0-mvp', 'Initial MVP database schema');

-- =============================================
-- 维护脚本说明 (生产环境)
-- =============================================

/*
生产环境维护建议 (MVP Focus):

1. 备份策略:
   - 每日全量备份: mysqldump -u root -p psychat > /backup/psychat_mvp_$(date +\%Y\%m\%d).sql
   - (Binary logging for point-in-time recovery can be considered post-MVP)

2. 监控:
   - Basic monitoring of DB server health, query performance on `resources` table.

3. 安全措施:
   - Use strong, unique passwords managed via environment variables or secrets management.
   - Limit database access to the application server's IP address.
*/