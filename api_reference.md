# Complete API Route Examples - DocumentVerifierBK

This document provides **working examples** for **ALL** API endpoints in the project, organized by category.

---

## Table of Contents

1. [Common](#common)
2. [Authentication](#authentication)
3. [User Management](#user-management)
4. [Documents](#documents)
5. [Verification (Public)](#verification-public)

---

## Common

### Health Check

**Description**: Check if the API server is running and healthy.

```bash
GET http://localhost:8000/common/health/
```

**Response:**
```json
{
  "hasError": false,
  "statusCode": 200,
  "message": {
    "general": ["✅ Server is healthy and running 🚀"]
  },
  "response": {}
}
```

---

## Authentication

### Register New User

**Description**: Register a new user account with first name, last name, email, and password. Returns access and refresh tokens upon successful registration.

**Mandatory Fields**: `first_name`, `email`, `password`  
**Optional Fields**: `last_name`

```bash
POST http://localhost:8000/auth/register/
Content-Type: application/x-www-form-urlencoded

first_name=John&last_name=Doe&email=john@example.com&password=SecurePass123
```

**Response:**
```json
{
  "hasError": false,
  "statusCode": 200,
  "message": {
    "general": ["User registered successfully"]
  },
  "response": {
    "user": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access_token_expiry": 60,
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token_expiry": 10080
  }
}
```

---

### Login

**Description**: Authenticate an existing user with email and password. Returns access and refresh tokens upon successful login.

**Mandatory Fields**: `email`, `password`  
**Optional Fields**: None

```bash
POST http://localhost:8000/auth/login/
Content-Type: application/x-www-form-urlencoded

email=john@example.com&password=SecurePass123
```

**Response:**
```json
{
  "hasError": false,
  "statusCode": 200,
  "message": {
    "general": ["User login success."]
  },
  "response": {
    "user": {
      "first_name": "John",
      "last_name": "Doe",
      "email": "john@example.com"
    },
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access_token_expiry": 60,
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token_expiry": 10080
  }
}
```

---

## User Management

> **Authentication Required**: All user management endpoints require a valid JWT access token.

### Get Profile

**Description**: Retrieve the current authenticated user's profile details.

```bash
GET http://localhost:8000/user/profile/
Authorization: Bearer <your-access-token>
```

**Response:**
```json
{
  "hasError": false,
  "statusCode": 200,
  "message": {
    "general": ["User profile retrieved successfully"]
  },
  "response": {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com"
  }
}
```

---

### Update Profile

**Description**: Update user details. If `password` is provided, it will be hashed before storage.

```bash
PUT http://localhost:8000/user/profile/
Authorization: Bearer <your-access-token>
Content-Type: application/json

{
  "first_name": "Johnny",
  "password": "NewSecurePassword456"
}
```

---

### Delete Profile

**Description**: Permanently delete the user account.

```bash
DELETE http://localhost:8000/user/profile/
Authorization: Bearer <your-access-token>
```

---

### Manage Organization (Affiliation)

**Endpoints**: 
* `GET /user/org/` - View organization details (Returns 200 with null if not found)
* `POST /user/org/` - Create organization details
* `PUT /user/org/` - Update or create organization details
* `DELETE /user/org/` - Delete organization details

**Fields**: `name`, `type` (University/Institution/Organization), `website`

```bash
PUT http://localhost:8000/user/org/
Authorization: Bearer <your-access-token>
Content-Type: application/json

{
  "name": "Global Tech Institute",
  "type": "Institution",
  "website": "https://gti.example.edu"
}
```

---

## Documents

> **Authentication Required**: All document endpoints (except public verification) require a valid JWT access token.

### List All Documents

**Description**: Retrieve all documents belonging to the authenticated user. Includes blockchain transaction hashes.

```bash
GET http://localhost:8000/doc/document/
Authorization: Bearer <your-access-token>
```

**Response:**
```json
{
  "hasError": false,
  "statusCode": 200,
  "message": { "general": ["Documents retrieved successfully"] },
  "response": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Bachelor's Degree Certificate",
      "type": "certificate",
      "description": "Undergraduate degree from University XYZ",
      "issue_at": "2022-06-15",
      "expiry_at": null,
      "document_hash": "a3f5b7d...",
      "blockchain_tx_hash": "0xabc..."
    }
  ]
}
```

---

### Document Insights

**Description**: Get summary statistics of user's documents and activities (verifications, shares).

```bash
GET http://localhost:8000/doc/insight/
Authorization: Bearer <your-access-token>
```

**Response:**
```json
{
  "hasError": false,
  "statusCode": 200,
  "message": { "general": ["Insights retrieved successfully"] },
  "response": {
    "total_docs": 10,
    "public_docs": 4,
    "private_docs": 6,
    "total_verification": 15,
    "total_shared": 5
  }
}
```

---

### Create Document

**Description**: Upload a new document. Automatically performs OCR, generates a content hash, and anchors it to the Polygon blockchain.

```bash
POST http://localhost:8000/doc/document/
Authorization: Bearer <your-access-token>
Content-Type: multipart/form-data

title=Certificate Name&type=certificate&file=@document.pdf
```

---

## Verification (Public)

> **No Authentication**: These endpoints are designed for public use.

### Verify by File Upload

**Description**: Publicly verify a document's authenticity by uploading the file. The system extracts OCR text, hashes it, and checks if the hash matches a recorded blockchain entry.

```bash
POST http://localhost:8000/verify/document/
Content-Type: multipart/form-data

file=@document_to_verify.pdf
```

**Response (Success):**
```json
{
  "hasError": false,
  "statusCode": 200,
  "message": { "general": ["Document verified successfully"] },
  "response": {
      "id": "550e8400...",
      "title": "Verified Document",
      "type": "certificate",
      "document_hash": "a3f5b7d...",
      "blockchain_tx_hash": "0xabc..."
  }
}
```

---

### View Public Document by ID

**Description**: View details of a specific document if its owner has set `public_view: true` in settings.

```bash
GET http://localhost:8000/verify/view-document/550e8400-e29b-41d4-a716-446655440000/
```

**Response:**
```json
{
  "hasError": false,
  "statusCode": 200,
  "message": { "general": ["Document retrieved successfully"] },
  "response": {
    "id": "550e8400...",
    "title": "Bachelor's Degree Certificate",
    "type": "certificate",
    "description": "...",
    "source_url": "https://..."
  }
}
```
