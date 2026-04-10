-- Document Verifier Project Database Schema (PostgreSQL)

DROP TABLE IF EXISTS "activity" CASCADE;
DROP TABLE IF EXISTS "document" CASCADE;
DROP TABLE IF EXISTS "user_oauth_credential" CASCADE;
DROP TABLE IF EXISTS "affiliation" CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;

CREATE TABLE "user" (
    "id" UUID NOT NULL PRIMARY KEY,
    "first_name" VARCHAR(150) NOT NULL,
    "last_name" VARCHAR(150) NULL,
    "email" VARCHAR(254) NOT NULL UNIQUE,
    "password" VARCHAR(128) NULL,
    "settings" JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE "affiliation" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "updated_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "type" VARCHAR(50) NOT NULL,
    "website" VARCHAR(200) NOT NULL,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "created_by_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "updated_by_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE "user_oauth_credential" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "provider" VARCHAR(50) NOT NULL,
    "provider_user_id" VARCHAR(255) NOT NULL,
    "access_token" TEXT NOT NULL,
    "refresh_token" TEXT NOT NULL,
    "token_expires_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "user_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "created_by_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT "unique_user_provider" UNIQUE ("user_id", "provider")
);

CREATE TABLE "document" (
    "id" UUID NOT NULL PRIMARY KEY,
    "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "updated_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "title" VARCHAR(150) NOT NULL,
    "type" VARCHAR(50) NOT NULL,
    "description" VARCHAR(300) NULL,
    "source_url" VARCHAR(200) NOT NULL DEFAULT '',
    "ocr_content" JSONB NOT NULL,
    "recipient_name" VARCHAR(150) NOT NULL,
    "recipient_email" VARCHAR(254) NOT NULL,
    "issuing_affiliation" VARCHAR(200) NOT NULL,
    "settings" JSONB NOT NULL DEFAULT '{}'::jsonb,
    "issue_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "expiry_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "created_by_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "updated_by_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "blockchain_tx_hash" VARCHAR(255) NULL,
    "document_hash" VARCHAR(255) NULL
);

CREATE TABLE "activity" (
    "id" UUID NOT NULL PRIMARY KEY,
    "activity_type" VARCHAR(50) NOT NULL,
    "created_at" TIMESTAMP WITH TIME ZONE NOT NULL,
    "doc_id" UUID NOT NULL REFERENCES "document" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "doc_owner_id" UUID NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED,
    "user_id" UUID NULL REFERENCES "user" ("id") ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED
);
