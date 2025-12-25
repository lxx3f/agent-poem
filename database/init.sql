-- ===============================
-- 数据库初始化：诗云（Shiyun）
-- ===============================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS shiyun_db
DEFAULT CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE shiyun_db;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ===============================
-- 作者表
-- ===============================
DROP TABLE IF EXISTS writer;
CREATE TABLE writer (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '作者ID',
    name VARCHAR(50) NOT NULL COMMENT '作者姓名',
    dynasty VARCHAR(20) DEFAULT '' COMMENT '朝代',
    intro TEXT COMMENT '作者简介',
    detail_intro TEXT COMMENT '作者详细介绍',
    create_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_writer_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='作者表';

-- 插入默认作者：佚名
INSERT INTO writer (id, name, dynasty, intro)
VALUES (1, '佚名', '', '作者信息不详')
ON DUPLICATE KEY UPDATE name = name;

-- ===============================
-- 诗词表
-- ===============================
DROP TABLE IF EXISTS poetry;
CREATE TABLE poetry (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '诗词ID',
    title VARCHAR(100) NOT NULL COMMENT '诗词标题',
    dynasty VARCHAR(20) DEFAULT '' COMMENT '朝代',
    writer_id INT(11) NOT NULL DEFAULT 1 COMMENT '作者ID',
    keywords VARCHAR(200) DEFAULT '' COMMENT '关键词',
    milvus_id VARCHAR(50) DEFAULT '' COMMENT 'Milvus向量ID',
    content TEXT NOT NULL COMMENT '诗词内容',
    connotation TEXT COMMENT '注释',
    translation TEXT COMMENT '译文',
    remark TEXT COMMENT '赏析',
    create_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_writer_id (writer_id),
    KEY idx_keywords (keywords),
    CONSTRAINT fk_poetry_writer
        FOREIGN KEY (writer_id)
        REFERENCES writer(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='诗词表';

-- 插入默认诗词：佚名
INSERT INTO poetry (id, title, content, dynasty, writer_id, keywords)
VALUES (
    1,
    '佚名',
    '此诗词暂无具体内容。',
    '',
    1,
    '佚名'
)
ON DUPLICATE KEY UPDATE title = title;

-- ===============================
-- 诗句表
-- ===============================
DROP TABLE IF EXISTS sentence;
CREATE TABLE sentence (
    id INT(11) NOT NULL AUTO_INCREMENT COMMENT '诗句ID',
    content VARCHAR(200) NOT NULL COMMENT '诗句内容',
    poetry_id INT(11) NOT NULL DEFAULT 1 COMMENT '关联诗词ID',
    create_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    KEY idx_poetry_id (poetry_id),
    KEY idx_content (content),
    CONSTRAINT fk_sentence_poetry
        FOREIGN KEY (poetry_id)
        REFERENCES poetry(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='诗句表';

SET FOREIGN_KEY_CHECKS = 1;
