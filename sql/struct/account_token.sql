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

 Date: 16/12/2024 19:26:47
*/


-- ----------------------------
-- Table structure for account_token
-- ----------------------------
DROP TABLE IF EXISTS "public"."account_token";
CREATE TABLE "public"."account_token" (
  "account_id" varchar(36) COLLATE "pg_catalog"."default",
  "token" varchar COLLATE "pg_catalog"."default",
  "description" varchar COLLATE "pg_catalog"."default",
  "id" uuid NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
)
;
ALTER TABLE "public"."account_token" OWNER TO "bukp";

-- ----------------------------
-- Primary Key structure for table account_token
-- ----------------------------
ALTER TABLE "public"."account_token" ADD CONSTRAINT "account_token_pkey" PRIMARY KEY ("id");
