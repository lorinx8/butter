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

 Date: 16/12/2024 19:27:24
*/


-- ----------------------------
-- Table structure for dict
-- ----------------------------
DROP TABLE IF EXISTS "public"."dict";
CREATE TABLE "public"."dict" (
  "key" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "value" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "value_type" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "group_id" varchar(36) COLLATE "pg_catalog"."default" NOT NULL,
  "id" uuid NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
)
;
ALTER TABLE "public"."dict" OWNER TO "bukp";

-- ----------------------------
-- Uniques structure for table dict
-- ----------------------------
ALTER TABLE "public"."dict" ADD CONSTRAINT "dict_key_key" UNIQUE ("key");

-- ----------------------------
-- Primary Key structure for table dict
-- ----------------------------
ALTER TABLE "public"."dict" ADD CONSTRAINT "dict_pkey" PRIMARY KEY ("id");
