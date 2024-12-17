/*
 Navicat Premium Dump SQL

 Source Server         : mac-pg
 Source Server Type    : PostgreSQL
 Source Server Version : 160004 (160004)
 Source Host           : localhost:5432
 Source Catalog        : butter
 Source Schema         : public

 Target Server Type    : PostgreSQL
 Target Server Version : 160004 (160004)
 File Encoding         : 65001

 Date: 16/12/2024 19:28:27
*/


-- ----------------------------
-- Table structure for prompt
-- ----------------------------
DROP TABLE IF EXISTS "public"."prompt";
CREATE TABLE "public"."prompt" (
  "code" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "content" text COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "is_active" bool,
  "id" uuid NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
)
;
ALTER TABLE "public"."prompt" OWNER TO "bukp";

-- ----------------------------
-- Uniques structure for table prompt
-- ----------------------------
ALTER TABLE "public"."prompt" ADD CONSTRAINT "prompt_code_key" UNIQUE ("code");

-- ----------------------------
-- Primary Key structure for table prompt
-- ----------------------------
ALTER TABLE "public"."prompt" ADD CONSTRAINT "prompt_pkey" PRIMARY KEY ("id");
