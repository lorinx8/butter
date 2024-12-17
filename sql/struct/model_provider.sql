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

 Date: 16/12/2024 19:28:16
*/


-- ----------------------------
-- Table structure for model_provider
-- ----------------------------
DROP TABLE IF EXISTS "public"."model_provider";
CREATE TABLE "public"."model_provider" (
  "code" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "metadatas" jsonb,
  "description" text COLLATE "pg_catalog"."default",
  "is_active" bool,
  "id" uuid NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
)
;
ALTER TABLE "public"."model_provider" OWNER TO "bukp";

-- ----------------------------
-- Uniques structure for table model_provider
-- ----------------------------
ALTER TABLE "public"."model_provider" ADD CONSTRAINT "model_provider_code_key" UNIQUE ("code");

-- ----------------------------
-- Primary Key structure for table model_provider
-- ----------------------------
ALTER TABLE "public"."model_provider" ADD CONSTRAINT "model_provider_pkey" PRIMARY KEY ("id");
