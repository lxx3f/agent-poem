-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS shiyun_db DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE shiyun_db;

-- 作者表
DROP TABLE IF EXISTS writer;
CREATE TABLE writer (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '作者ID',
    name VARCHAR(50) NOT NULL COMMENT '作者姓名',
    dynasty VARCHAR(20) DEFAULT '' COMMENT '朝代',
    intro TEXT COMMENT '作者简介',
    create_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='作者表';

-- 诗词表
DROP TABLE IF EXISTS poetry;
CREATE TABLE poetry (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '诗词ID',
    title VARCHAR(100) NOT NULL COMMENT '诗词标题',
    content TEXT NOT NULL COMMENT '诗词内容',
    dynasty VARCHAR(20) DEFAULT '' COMMENT '朝代',
    writer_id INT(11) DEFAULT 0 COMMENT '作者ID',
    keywords VARCHAR(200) DEFAULT '' COMMENT '关键词',
    milvus_id VARCHAR(50) DEFAULT '' COMMENT 'Milvus向量ID',
    create_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    INDEX idx_writer_id (writer_id),
    INDEX idx_keywords (keywords)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='诗词表';

-- 诗句表
DROP TABLE IF EXISTS sentence;
CREATE TABLE sentence (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '诗句ID',
    content VARCHAR(200) NOT NULL COMMENT '诗句内容',
    poetry_id INT(11) DEFAULT 0 COMMENT '关联诗词ID',
    create_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    INDEX idx_poetry_id (poetry_id),
    INDEX idx_content (content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='诗句表';