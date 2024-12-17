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

 Date: 16/12/2024 19:27:36
*/


-- ----------------------------
-- Table structure for dict_group
-- ----------------------------
DROP TABLE IF EXISTS "public"."dict_group";
CREATE TABLE "public"."dict_group" (
  "code" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "name" varchar(255) COLLATE "pg_catalog"."default" NOT NULL,
  "description" text COLLATE "pg_catalog"."default",
  "is_system" bool,
  "parent_id" varchar(36) COLLATE "pg_catalog"."default",
  "id" uuid NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
)
;
ALTER TABLE "public"."dict_group" OWNER TO "bukp";

-- ----------------------------
-- Uniques structure for table dict_group
-- ----------------------------
ALTER TABLE "public"."dict_group" ADD CONSTRAINT "dict_group_code_key" UNIQUE ("code");

-- ----------------------------
-- Primary Key structure for table dict_group
-- ----------------------------
ALTER TABLE "public"."dict_group" ADD CONSTRAINT "dict_group_pkey" PRIMARY KEY ("id");
