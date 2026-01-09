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


-- ===============================
-- 用户表
-- ===============================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
  email VARCHAR(128) NOT NULL UNIQUE COMMENT '登录邮箱',
  password_hash VARCHAR(255) NOT NULL COMMENT '密码哈希',
  username VARCHAR(64) COMMENT '用户名/昵称',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ===============================
-- agent表
-- ===============================
DROP TABLE IF EXISTS agents;
CREATE TABLE agents (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(64) NOT NULL COMMENT 'Agent 名称（展示用）',
    code VARCHAR(64) NOT NULL UNIQUE COMMENT 'Agent 唯一标识，如 feihualing_v1',
    description VARCHAR(255) COMMENT 'Agent 描述',

    workflow_key VARCHAR(64) NOT NULL COMMENT '绑定的 workflow key',

    system_prompt TEXT NOT NULL COMMENT 'Agent 规则 Prompt（system role）',

    parameters JSON NULL COMMENT 'workflow 参数配置（如关键词、轮次限制等）',

    llm_config JSON NULL COMMENT '模型配置，如 model / temperature / max_tokens',

    is_active TINYINT DEFAULT 1 COMMENT '是否启用',

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent 定义表';

-- 插入初始数据
INSERT INTO agents (code, name, description, system_prompt, workflow_key)
VALUES (
  'poetry_chat_v1',
  '诗词问答助手',
  '支持诗词解释、背景介绍、诗句赏析的通用助手',
  '你是一名精通中国古典诗词的助手。
用户的问题可能涉及诗词原文、作者背景、意象解析或赏析。
回答应准确、简洁、具有文学性。
如有需要，可引用诗句原文，但不要编造不存在的内容。',
  'rag_chat'
);
INSERT INTO agents (code, name, description, system_prompt, workflow_key)
VALUES (
  'poetry_semantic_search_v1',
  '诗词语义搜索',
  '根据用户描述匹配最相关的诗词内容',
  '你是一名诗词检索专家。
用户会使用自然语言描述想找的诗词主题、场景或情感。
你的任务是：
1. 理解用户意图
2. 从候选诗词中选择最匹配的内容
3. 简要说明匹配理由
只基于提供的诗词内容进行回答，不要凭空创作。',
  'rag_search'
);
INSERT INTO agents (code, name, description, system_prompt, workflow_key)
VALUES (
  'feihualing_v1',
  '飞花令',
  '诗词飞花令玩法',
  '你正在与用户进行诗词飞花令游戏。
规则如下：
1. 双方轮流说出包含指定关键字的诗句
2. 诗句必须真实存在，不可重复
3. 若一方无法接续，则判负
你作为助手，应：
- 给出完整诗句
- 标注作者与作品名
- 避免重复之前出现的诗句',
  'game_turn_based'
);
INSERT INTO agents (code, name, description, system_prompt, workflow_key)
VALUES (
  'poetry_chain_v1',
  '诗词接龙',
  '根据上一句诗的结尾进行诗词接龙',
  '你正在进行诗词接龙游戏。
规则如下：
1. 新诗句的首字必须与上一句的末字相同
2. 诗句需真实存在
3. 不可重复
请给出：
- 诗句原文
- 作者
- 作品名',
  'game_turn_based'
);



-- ===============================
-- 会话表
-- ===============================
DROP TABLE IF EXISTS conversations;
CREATE TABLE conversations (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '会话ID',
  user_id BIGINT NOT NULL COMMENT '所属用户ID',
  title VARCHAR(128) COMMENT '会话标题',
  agent_id BIGINT NOT NULL COMMENT '所属agentID',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_conversations_users
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE,

    CONSTRAINT fk_conversations_agents
    FOREIGN KEY (agent_id)
    REFERENCES agents(id)
    ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会话表';


-- ===============================
-- 消息表
-- ===============================
DROP TABLE IF EXISTS messages;
CREATE TABLE messages (
  id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '消息ID',
  conversation_id BIGINT NOT NULL COMMENT '所属会话ID',
  role ENUM('user', 'assistant', 'system') NOT NULL COMMENT '消息角色',
  content TEXT NOT NULL COMMENT '消息内容',
  status ENUM('pending', 'done', 'failed') NOT NULL COMMENT '消息状态',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_messages_conversations
    FOREIGN KEY (conversation_id)
    REFERENCES conversations(id)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='会话消息表';


