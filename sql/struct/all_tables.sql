/*
 Combined SQL Tables
 Generated on: 2024-12-16 19:32
 This file contains all table definitions from the sql/struct directory
*/

-- Start of account.sql
/*
 Table: account
*/
DROP TABLE IF EXISTS "public"."account" CASCADE;
CREATE TABLE "public"."account" (
  "email" varchar COLLATE "pg_catalog"."default",
  "username" varchar COLLATE "pg_catalog"."default",
  "hashed_password" varchar COLLATE "pg_catalog"."default",
  "is_active" bool,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
);

CREATE UNIQUE INDEX "ix_account_email" ON "public"."account" USING btree (
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "ix_account_username" ON "public"."account" USING btree (
  "username" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

ALTER TABLE "public"."account" ADD CONSTRAINT "account_pkey" PRIMARY KEY ("id");

-- Start of account_token.sql
/*
 Table: account_token
*/
DROP TABLE IF EXISTS "public"."account_token" CASCADE;
CREATE TABLE "public"."account_token" (
  "account_id" varchar(36) COLLATE "pg_catalog"."default",
  "token" varchar COLLATE "pg_catalog"."default",
  "description" varchar COLLATE "pg_catalog"."default",
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
);

ALTER TABLE "public"."account_token" ADD CONSTRAINT "account_token_pkey" PRIMARY KEY ("id");

-- Start of admin_user.sql
/*
 Table: admin_user
*/
DROP TABLE IF EXISTS "public"."admin_user" CASCADE;
CREATE TABLE "public"."admin_user" (
  "email" varchar COLLATE "pg_catalog"."default",
  "telephone" varchar COLLATE "pg_catalog"."default",
  "username" varchar COLLATE "pg_catalog"."default",
  "hashed_password" varchar COLLATE "pg_catalog"."default",
  "is_active" bool,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
);

CREATE UNIQUE INDEX "ix_admin_user_email" ON "public"."admin_user" USING btree (
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "ix_admin_user_telephone" ON "public"."admin_user" USING btree (
  "telephone" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "ix_admin_user_username" ON "public"."admin_user" USING btree (
  "username" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

ALTER TABLE "public"."admin_user" ADD CONSTRAINT "admin_user_pkey" PRIMARY KEY ("id");

-- Start of bot.sql
/*
 Table: bot
*/
DROP TABLE IF EXISTS "public"."bot" CASCADE;
CREATE TABLE "public"."bot" (
  "code" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "bot_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "properties" jsonb,
  "description" text COLLATE "pg_catalog"."default",
  "version" varchar(255) COLLATE "pg_catalog"."default" NOT NULL DEFAULT 'version1',
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
);

ALTER TABLE "public"."bot" ADD CONSTRAINT "bot_code_key" UNIQUE ("code");
ALTER TABLE "public"."bot" ADD CONSTRAINT "bot_pkey" PRIMARY KEY ("id");

-- Start of dict.sql
/*
 Table: dict
*/
DROP TABLE IF EXISTS "public"."dict" CASCADE;
CREATE TABLE "public"."dict" (
  "key" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "value" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "value_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "group_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
);

ALTER TABLE "public"."dict" ADD CONSTRAINT "dict_key_key" UNIQUE ("key");
ALTER TABLE "public"."dict" ADD CONSTRAINT "dict_pkey" PRIMARY KEY ("id");

-- Start of dict_group.sql
/*
 Table: dict_group
*/
DROP TABLE IF EXISTS "public"."dict_group" CASCADE;
CREATE TABLE "public"."dict_group" (
  "code" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "is_system" bool,
  "parent_id" varchar(36) COLLATE "pg_catalog"."default",
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
);

ALTER TABLE "public"."dict_group" ADD CONSTRAINT "dict_group_code_key" UNIQUE ("code");
ALTER TABLE "public"."dict_group" ADD CONSTRAINT "dict_group_pkey" PRIMARY KEY ("id");

-- Start of model.sql
/*
 Table: model
*/
DROP TABLE IF EXISTS "public"."model" CASCADE;
CREATE TABLE "public"."model" (
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "provider" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "deploy_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "properties" jsonb,
  "is_active" bool,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
);

ALTER TABLE "public"."model" ADD CONSTRAINT "model_deploy_name_key" UNIQUE ("deploy_name");
ALTER TABLE "public"."model" ADD CONSTRAINT "model_pkey" PRIMARY KEY ("id");

-- Start of model_provider.sql
/*
 Table: model_provider
*/
DROP TABLE IF EXISTS "public"."model_provider" CASCADE;
CREATE TABLE "public"."model_provider" (
  "code" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "metadatas" jsonb,
  "description" text COLLATE "pg_catalog"."default",
  "is_active" bool,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
);

ALTER TABLE "public"."model_provider" ADD CONSTRAINT "model_provider_code_key" UNIQUE ("code");
ALTER TABLE "public"."model_provider" ADD CONSTRAINT "model_provider_pkey" PRIMARY KEY ("id");

-- Start of prompt.sql
/*
 Table: prompt
*/
DROP TABLE IF EXISTS "public"."prompt" CASCADE;
CREATE TABLE "public"."prompt" (
  "code" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "content" text COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "is_active" bool,
  "id" uuid NOT NULL DEFAULT gen_random_uuid(),
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
);

ALTER TABLE "public"."prompt" ADD CONSTRAINT "prompt_code_key" UNIQUE ("code");
ALTER TABLE "public"."prompt" ADD CONSTRAINT "prompt_pkey" PRIMARY KEY ("id");

-- ########################################################################################################################################################
-- start of chat history
/*
 Table: chat_histories
*/
-- 创建 sender_type 枚举类型
CREATE TYPE sender_type AS ENUM ('USER', 'AI');

DROP TABLE IF EXISTS chat_histories;
-- 创建分区表
CREATE TABLE chat_histories (
    id uuid DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP NOT NULL,
    sender sender_type NOT NULL,
    session_id VARCHAR NOT NULL,
    content TEXT,
    bot_code VARCHAR NOT NULL,
    image_url VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

-- 创建分区表维护函数
CREATE OR REPLACE FUNCTION create_chat_history_partition()
RETURNS void AS $$
DECLARE
    partition_date date;
    partition_name text;
    start_date text;
    end_date text;
BEGIN
    -- 获取下个月的日期
    partition_date := date_trunc('month', current_date + interval '1 month');
    
    -- 构造分区名称，例如：chat_histories_y2024m03
    partition_name := 'chat_histories_y' || 
                     to_char(partition_date, 'YYYY') || 
                     'm' || 
                     to_char(partition_date, 'MM');
    
    -- 构造日期范围
    start_date := to_char(partition_date, 'YYYY-MM-DD');
    end_date := to_char(partition_date + interval '1 month', 'YYYY-MM-DD');
    
    -- 创建分区
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF chat_histories FOR VALUES FROM (%L) TO (%L)',
        partition_name,
        start_date,
        end_date
    );
    
    RAISE NOTICE 'Created partition % for date range % to %', 
                 partition_name, start_date, end_date;
END;
$$ LANGUAGE plpgsql;

-- 创建初始分区函数
CREATE OR REPLACE FUNCTION create_initial_partitions()
RETURNS void AS $$
DECLARE
    current_date_var date;
    partition_name text;
    start_date text;
    end_date text;
BEGIN
    -- 从当前月开始，创建未来3个月的分区
    FOR i IN 0..2 LOOP
        current_date_var := date_trunc('month', current_date + (i || ' month')::interval);
        
        partition_name := 'chat_histories_y' || 
                         to_char(current_date_var, 'YYYY') || 
                         'm' || 
                         to_char(current_date_var, 'MM');
        
        start_date := to_char(current_date_var, 'YYYY-MM-DD');
        end_date := to_char(current_date_var + interval '1 month', 'YYYY-MM-DD');
        
        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS %I PARTITION OF chat_histories FOR VALUES FROM (%L) TO (%L)',
            partition_name,
            start_date,
            end_date
        );
        
        RAISE NOTICE 'Created initial partition % for date range % to %', 
                     partition_name, start_date, end_date;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器，每月自动创建新分区
CREATE OR REPLACE FUNCTION create_partition_trigger()
RETURNS trigger AS $$
BEGIN
    PERFORM create_chat_history_partition();
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER create_new_partition_trigger
    AFTER INSERT ON chat_histories
    EXECUTE PROCEDURE create_partition_trigger();

-- 创建索引
-- 复合索引：用于时间范围查询和按会话查询
CREATE INDEX ix_chat_histories_timestamp_session ON chat_histories (timestamp, session_id);
-- 会话ID索引：用于按会话查询
CREATE INDEX ix_chat_histories_session_id ON chat_histories (session_id);
-- 时间戳索引：用于时间范围查询
CREATE INDEX ix_chat_histories_timestamp ON chat_histories (timestamp DESC);

-- 初始创建分区（当前月份和未来两个月）
SELECT create_initial_partitions();

-- ########################################################################################################################################################
