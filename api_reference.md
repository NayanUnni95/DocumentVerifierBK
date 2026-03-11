# Complete API Route Examples - DocumentVerifierBK

This document provides **working examples** for **ALL** API endpoints in the project, organized by category.

---

## Table of Contents

1. [Common](#common)
2. [Authentication](#authentication)
3. [User Management](#user-management)
4. [Documents](#documents)
5. [Document Activity](#document-activity)
6. [Verification (Public)](#verification-public)

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

> **Authentication Required**: All document management endpoints require a valid JWT access token in the `Authorization` header.

---

### 1. List All Documents

**Description**: Retrieve a summary list of all documents owned by the authenticated user.

*   **URL**: `GET http://localhost:8000/doc/document/`
*   **Method**: `GET`
*   **Response**:
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

### 2. Get Specific Document

**Description**: Retrieve full details of a specific document, including settings and storage URL.

*   **URL**: `GET http://localhost:8000/doc/document/<uuid:id>/`
*   **Method**: `GET`
*   **Response**:
    ```json
    {
      "hasError": false,
      "statusCode": 200,
      "message": { "general": ["Documents retrieved successfully"] },
      "response": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Bachelor Degree",
        "type": "certificate",
        "description": "Final degree certificate",
        "recipient_name": "John Doe",
        "recipient_email": "john@example.com",
        "issuing_affiliation": "Global Tech Institute",
        "public_view": true,
        "allow_download": false,
        "source_url": "https://s3.amazonaws.com/...",
        "issue_at": "2022-06-15",
        "expiry_at": null,
        "document_hash": "a3f5b7d...",
        "blockchain_tx_hash": "0xabc..."
      }
    }
    ```

---

### 3. Create Document

**Description**: Upload a new document. Performs OCR, generates a hash, and anchors it to the Polygon blockchain.

*   **URL**: `POST http://localhost:8000/doc/document/`
*   **Method**: `POST`
*   **Content-Type**: `multipart/form-data`
*   **Body Fields**:
    *   `title` (String, Required): Name of the document.
    *   `type` (String, Required): Category (e.g., certificate, report, transcript).
    *   `file` (File, Required): The document file (PDF, JPG, PNG).
    *   `description` (String): Brief summary or notes.
    *   `recipient_name` (String): Name of the person the document belongs to.
    *   `recipient_email` (String): Email of the recipient.
    *   `issuing_affiliation` (String): The organization issuing the document.
    *   `issue_at` (Date, YYYY-MM-DD): Date of issuance.
    *   `expiry_at` (Date, YYYY-MM-DD): Date of expiration (if any).
    *   `public_view` (Boolean): Set to `true` to allow anyone with the link to view.
    *   `allow_download` (Boolean): Set to `true` to allow public users to download the file.
*   **Response**:
    ```json
    {
      "hasError": false,
      "statusCode": 200,
      "message": { "general": ["Document created successfully with OCR"] },
      "response": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "title": "Bachelor Degree",
        "document_hash": "a3f5b7d...",
        "blockchain_tx_hash": "0xabc..."
      }
    }
    ```

---

### 4. Update Document

**Description**: Update metadata or replace the file of an existing document. Supports partial updates (only fields provided will be changed).

*   **URL**: `PUT http://localhost:8000/doc/document/<uuid:id>/`
*   **Method**: `PUT`
*   **Content-Type**: `multipart/form-data`
*   **Body Fields**: Same as **Create Document** (all fields optional).
*   **Example**: Change visibility and title.
    ```bash
    PUT http://localhost:8000/doc/document/550e8400-e29b-41d4-a716-446655440000/
    Authorization: Bearer <your-access-token>
    Content-Type: multipart/form-data

    title=Final Bachelor Certificate&public_view=false
    ```

---

### 5. Delete Document

**Description**: Permanently delete a document from the system.

*   **URL**: `DELETE http://localhost:8000/doc/document/<uuid:id>/`
*   **Method**: `DELETE`
*   **Response**:
    ```json
    {
      "hasError": false,
      "statusCode": 200,
      "message": { "general": ["Document deleted successfully"] },
      "response": {}
    }
    ```

---

### 6. Document Insights

**Description**: Retrieve summary statistics for the user's dashboard.

*   **URL**: `GET http://localhost:8000/doc/insight/`
*   **Method**: `GET`
*   **Response**:
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

## Document Activity

> **Authentication Required**: Requires a valid JWT access token.

### List Document Activity

**Description**: Retrieve a history of activities related to the user's documents. Activities include:
*   `upload`: When a new document is created.
*   `check`: When a document is verified (publicly).
*   `shared`: When a document's `public_view` setting is changed.

*   **URL**: `GET http://localhost:8000/doc/activity/`
*   **Method**: `GET`
*   **Response**:
    ```json
    {
      "hasError": false,
      "statusCode": 200,
      "message": { "general": ["Activities retrieved successfully"] },
      "response": [
        {
          "id": "770e8400-e29b-41d4-a716-446655440001",
          "user": "550e8400-e29b-41d4-a716-446655440000",
          "username": "john_doe",
          "doc": "880e8400-e29b-41d4-a716-446655440002",
          "doc_title": "Bachelor Degree",
          "doc_type": "certificate",
          "activity_type": "upload",
          "created_at": "2026-03-11T11:53:36Z"
        },
        {
          "id": "770e8400-e29b-41d4-a716-446655440003",
          "user": null,
          "username": null,
          "doc": "880e8400-e29b-41d4-a716-446655440002",
          "doc_title": "Bachelor Degree",
          "doc_type": "certificate",
          "activity_type": "check",
          "created_at": "2026-03-11T11:58:10Z"
        }
      ]
    }
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
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Verified Document",
      "type": "certificate",
      "description": "...",
      "issue_at": "2024-01-01",
      "expiry_at": null,
      "document_hash": "a3f5b7d...",
      "blockchain_tx_hash": "0xabc..."
  }
}
```

---

### View Public Document by ID

**Description**: View details of a specific document if its owner has set `public_view: true`. No authentication required.

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
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Bachelor Degree",
    "type": "certificate",
    "description": "...",
    "recipient_name": "John Doe",
    "issuing_affiliation": "Global Tech Institute",
    "public_view": true,
    "allow_download": false,
    "source_url": "https://...",
    "document_hash": "a3f5b7d...",
    "blockchain_tx_hash": "0xabc..."
  }
}
```
