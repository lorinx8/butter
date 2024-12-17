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

 Date: 16/12/2024 19:28:07
*/


-- ----------------------------
-- Table structure for model
-- ----------------------------
DROP TABLE IF EXISTS "public"."model";
CREATE TABLE "public"."model" (
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "provider" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "deploy_name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "properties" jsonb,
  "is_active" bool,
  "id" uuid NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
)
;
ALTER TABLE "public"."model" OWNER TO "bukp";

-- ----------------------------
-- Uniques structure for table model
-- ----------------------------
ALTER TABLE "public"."model" ADD CONSTRAINT "model_deploy_name_key" UNIQUE ("deploy_name");

-- ----------------------------
-- Primary Key structure for table model
-- ----------------------------
ALTER TABLE "public"."model" ADD CONSTRAINT "model_pkey" PRIMARY KEY ("id");
