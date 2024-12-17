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

 Date: 16/12/2024 19:27:00
*/


-- ----------------------------
-- Table structure for admin_user
-- ----------------------------
DROP TABLE IF EXISTS "public"."admin_user";
CREATE TABLE "public"."admin_user" (
  "email" varchar COLLATE "pg_catalog"."default",
  "telephone" varchar COLLATE "pg_catalog"."default",
  "username" varchar COLLATE "pg_catalog"."default",
  "hashed_password" varchar COLLATE "pg_catalog"."default",
  "is_active" bool,
  "id" uuid NOT NULL,
  "created_at" timestamptz(6) NOT NULL DEFAULT now(),
  "updated_at" timestamptz(6)
)
;
ALTER TABLE "public"."admin_user" OWNER TO "bukp";

-- ----------------------------
-- Indexes structure for table admin_user
-- ----------------------------
CREATE UNIQUE INDEX "ix_admin_user_email" ON "public"."admin_user" USING btree (
  "email" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "ix_admin_user_telephone" ON "public"."admin_user" USING btree (
  "telephone" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);
CREATE UNIQUE INDEX "ix_admin_user_username" ON "public"."admin_user" USING btree (
  "username" COLLATE "pg_catalog"."default" "pg_catalog"."text_ops" ASC NULLS LAST
);

-- ----------------------------
-- Primary Key structure for table admin_user
-- ----------------------------
ALTER TABLE "public"."admin_user" ADD CONSTRAINT "admin_user_pkey" PRIMARY KEY ("id");
