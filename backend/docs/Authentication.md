# 05 - Authentication & Authorization Design

**Project:** AI Personal Assistant  
**Version:** 1.0  
**Owner:** Backend Team  
**Module:** Authentication & Authorization  
**Last Updated:** 18 July 2026

---

# 1. Purpose

This document defines the complete authentication and authorization architecture for the backend.

The authentication system is designed to be:

- Secure
- Stateless
- Scalable
- OAuth-ready
- Multi-device compatible
- Easy to integrate with frontend and AI services

---

# 2. Authentication Overview

The system uses a hybrid authentication model.

```
                User

                  │

            Email / OAuth

                  │

         Authentication Service

                  │

      Access Token + Refresh Token

                  │

          Protected API Requests
```

---

# 3. Authentication Methods

Supported authentication methods

```
Email + Password

Google OAuth

GitHub OAuth

Microsoft OAuth

Apple OAuth (Future)

Enterprise SSO (Future)
```

---

# 4. Authentication Flow

## Email Login

```
User

↓

POST /auth/login

↓

Validate Credentials

↓

Generate JWT

↓

Generate Refresh Token

↓

Hash Refresh Token

↓

Store Database

↓

Return Tokens
```

---

## OAuth Login

```
User

↓

Google Login

↓

Google OAuth

↓

Backend Callback

↓

Create User (If New)

↓

Generate Tokens

↓

Return JWT
```

---

# 5. Token Strategy

The backend uses two tokens.

## Access Token

Purpose

```
API Authentication
```

Properties

| Property | Value |
|----------|-------|
| Type | JWT |
| Lifetime | 15 minutes |
| Stored | Client Memory |
| Sent | Authorization Header |

---

## Refresh Token

Purpose

```
Generate New Access Tokens
```

Properties

| Property | Value |
|----------|-------|
| Type | Secure Random String |
| Lifetime | 30 Days |
| Stored | HttpOnly Cookie (Preferred) |
| Database | Hashed |
| Rotated | Every Refresh |

---

# 6. JWT Payload

Example

```json
{
  "sub": "user_uuid",
  "email": "user@example.com",
  "role": "user",
  "iat": 1750000000,
  "exp": 1750000900,
  "jti": "uuid"
}
```

Fields

| Field | Description |
|---------|------------|
| sub | User ID |
| email | User Email |
| role | User Role |
| iat | Issued At |
| exp | Expiration |
| jti | Token Identifier |

Never place sensitive information inside JWTs.

---

# 7. Refresh Token Rotation

Every refresh generates a new refresh token.

```
Client

↓

POST /auth/refresh

↓

Validate Token

↓

Generate New Access Token

↓

Generate New Refresh Token

↓

Revoke Old Token

↓

Store New Token

↓

Return New Tokens
```

Benefits

- Prevents replay attacks
- Limits token theft impact
- Enables session revocation

---

# 8. Password Policy

Requirements

- Minimum 12 characters
- Uppercase letter
- Lowercase letter
- Number
- Special character

Example

```
StrongPassword@123
```

Passwords should never be logged or returned in responses.

---

# 9. Password Hashing

Algorithm

```
Argon2id
```

Reasons

- Resistant to GPU attacks
- Memory hard
- Recommended for new applications

Never store plaintext passwords.

---

# 10. Session Management

Each login creates a new session.

Example

```
Laptop

↓

Session A

Phone

↓

Session B

Tablet

↓

Session C
```

Each session has its own refresh token.

Users may revoke sessions independently.

---

# 11. Logout

```
POST /auth/logout
```

Flow

```
Receive Refresh Token

↓

Mark Token Revoked

↓

Delete Cookie

↓

Return Success
```

Access tokens naturally expire after their TTL.

---

# 12. Logout From All Devices

```
POST /auth/logout-all
```

Process

```
Find All Refresh Tokens

↓

Mark Revoked

↓

Delete Sessions
```

---

# 13. Authorization

Authorization uses Role-Based Access Control (RBAC).

Roles

```
user

admin

system
```

Future

```
organization_admin

team_member
```

---

# 14. Route Protection

Public

```
POST /auth/login

POST /auth/register

POST /auth/refresh

GET /health
```

Protected

```
GET /users/me

POST /chats

GET /messages

GET /integrations
```

Admin

```
GET /admin/users

GET /admin/logs
```

---

# 15. Middleware Flow

```
Request

↓

Authorization Header

↓

Extract JWT

↓

Verify Signature

↓

Check Expiration

↓

Load User

↓

Attach User Context

↓

Continue Request
```

If validation fails

```
401 Unauthorized
```

---

# 16. OAuth Architecture

Supported providers

```
Google

GitHub

Microsoft
```

Flow

```
User

↓

OAuth Redirect

↓

Provider Login

↓

Authorization Code

↓

Backend Callback

↓

Exchange Code

↓

Receive Tokens

↓

Encrypt Tokens

↓

Store Database
```

---

# 17. OAuth Scopes

Google

```
openid

email

profile

gmail.readonly

calendar.readonly
```

GitHub

```
read:user

user:email

repo (optional)
```

Microsoft

```
openid

profile

email

offline_access
```

Request only the minimum permissions required.

---

# 18. Token Storage

Passwords

```
Argon2 Hash
```

Refresh Tokens

```
SHA-256 Hash
```

OAuth Tokens

```
AES-256 Encrypted
```

JWT

```
Not stored
```

---

# 19. Failed Login Protection

After repeated failures

```
5 Failed Attempts

↓

Temporary Lock

↓

Retry After 15 Minutes
```

Log suspicious activity for monitoring.

---

# 20. Security Headers

Include

```
Strict-Transport-Security

X-Content-Type-Options

X-Frame-Options

Content-Security-Policy

Referrer-Policy
```

Configured globally via middleware.

---

# 21. CSRF Protection

For cookie-based refresh tokens

- HttpOnly
- Secure
- SameSite=Lax (or Strict where applicable)

If refresh tokens are sent in cookies, enable CSRF protection.

---

# 22. Multi-Factor Authentication (Future)

Supported methods

```
Authenticator App (TOTP)

Email OTP

WebAuthn / Passkeys
```

Planned flow

```
Login

↓

Password Verified

↓

MFA Challenge

↓

Issue Tokens
```

---

# 23. Audit Logging

Record the following events

- Registration
- Login
- Logout
- Password Change
- Password Reset
- Token Refresh
- OAuth Connection
- Failed Login
- Session Revocation

Example

```json
{
  "user_id": "uuid",
  "event": "LOGIN_SUCCESS",
  "ip": "192.168.1.10",
  "user_agent": "Chrome",
  "timestamp": "2026-07-18T12:30:00Z"
}
```

Do not log passwords, tokens, or other secrets.

---

# 24. Environment Variables

```env
JWT_SECRET=

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=15

REFRESH_TOKEN_EXPIRE_DAYS=30

ARGON2_MEMORY_COST=

ARGON2_TIME_COST=

GOOGLE_CLIENT_ID=

GOOGLE_CLIENT_SECRET=

GITHUB_CLIENT_ID=

GITHUB_CLIENT_SECRET=

MICROSOFT_CLIENT_ID=

MICROSOFT_CLIENT_SECRET=

TOKEN_ENCRYPTION_KEY=
```

Secrets should be stored in a secure secrets manager in production.

---

# 25. Error Responses

Invalid credentials

```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password."
  }
}
```

Expired token

```json
{
  "success": false,
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "Access token has expired."
  }
}
```

Unauthorized

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Authentication required."
  }
}
```

---

# 26. Best Practices

- Use HTTPS in all environments except local development.
- Never expose refresh tokens to JavaScript.
- Rotate refresh tokens after every use.
- Encrypt OAuth tokens before storing them.
- Hash passwords using Argon2id.
- Use short-lived access tokens.
- Validate JWTs on every protected request.
- Implement rate limiting on authentication endpoints.
- Revoke tokens immediately when credentials change.

---

# 27. Definition of Done

The authentication system is complete when:

- User registration and login work.
- JWT access tokens are issued and validated.
- Refresh token rotation is implemented.
- Passwords are hashed with Argon2id.
- OAuth login is supported through a common provider interface.
- Protected routes enforce authentication.
- RBAC is available for future admin features.
- Audit logs capture authentication events.
- All authentication endpoints are documented and tested.
- Security headers, rate limiting, and session management are in place.

---

**End of Document**