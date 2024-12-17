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

 Date: 16/12/2024 19:26:31
*/


-- ----------------------------
-- Table structure for account
-- ----------------------------
DROP TABLE IF EXISTS "public"."account";
CREATE TABLE "public"."account" (
  "email" varchar COLLATE "pg_catalog"."default",
  "username" varchar COLLATE "pg_catalog"."default",
  "hashed_password" varchar COLLATE "pg_catalog"."default",
  "is_active" bool,
  "id" uuid NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
)
;
ALTER TABLE "public"."account" OWNER TO "bukp";

-- ----------------------------
-- Indexes structure for table account
-- ----------------------------
CREATE UNIQUE INDEX "ix_account_email" ON "public"."account" USING btree (
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "ix_account_username" ON "public"."account" USING btree (
  "username" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table account
-- ----------------------------
ALTER TABLE "public"."account" ADD CONSTRAINT "account_pkey" PRIMARY KEY ("id");
