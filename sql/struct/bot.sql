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

 Date: 16/12/2024 19:27:15
*/


-- ----------------------------
-- Table structure for bot
-- ----------------------------
DROP TABLE IF EXISTS "public"."bot";
CREATE TABLE "public"."bot" (
  "code" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "bot_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "properties" jsonb,
  "description" text COLLATE "pg_catalog"."default",
  "id" uuid NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
)
;
ALTER TABLE "public"."bot" OWNER TO "bukp";

-- ----------------------------
-- Uniques structure for table bot
-- ----------------------------
ALTER TABLE "public"."bot" ADD CONSTRAINT "bot_code_key" UNIQUE ("code");

-- ----------------------------
-- Primary Key structure for table bot
-- ----------------------------
ALTER TABLE "public"."bot" ADD CONSTRAINT "bot_pkey" PRIMARY KEY ("id");
