# Users

Extend User model - reference: [https://docs.djangoproject.com/en/4.0/ref/contrib/auth/](https://docs.djangoproject.com/en/4.0/ref/contrib/auth/)

- Uses [mixins](./mixins.md)

## Database 

### Model

```
- created (from AuditModelMixin)
- created_by (from AuditModelMixin)
- date_joined (from AbstractUser)
- display_name
- email (from AbstractUser)
- first_name (from AbstractUser)
- groups (from AbstractUser)
- id (from Basemodel)
- is_active (from AbstractUser)
- is_staff (from AbstractUser)
- is_superuser (from AbstractUser)
- last_login (from AbstractUser)
- last_name (from AbstractUser)
- modified (from AuditModelMixin)
- modified_by (from AuditModelMixin)
- oidc_email
- oidc_sub
- password (from AbstractUser)
- profile
- user_permissions (from AbstractUser)
- username (from AbstractUser)
- uuid
```

### Methods

- `is_active`: return `True` if user is **Active**
- `is_experimenter`: return `True` if user is an **Exerimenter**
- `is_pi`: return `True` if user is a **PI**
- `is_operator`: return `True` if user is an **Operator**
- `is_site_admin`: return `True` if user is a **Site Admin**

## API

### Overview

"X" in the table below denotes User permission to interact with the endpoint

Endpoint | `is_active` | `is_experimenter` | `is_pi` | `is_operator` | `is_site_admin` | `as_self`
:--------|:-----------:|:-----------------:|:-------:|:-------------:|:---------------:|:-----:
GET: [/users]() | X | X | X | X | X |
POST: [/users]() | | | | | |
GET: [/users/{user_id}]() | X | X | X | X | X |
PUT: [/users/{user_id}]() | X | X | X | X | X | X
PATCH: [/users/{user_id}]() | X | X | X | X | X | X
DELETE: [/users/{user_id}]() | | | | | |

Notes:

- `is_active`: User is currently Active
- `is_experimenter`: User is currently an **Exerimenter**
- `is_pi`: User is currently a **PI**
- `is_operator`: User is currently an **Operator**
- `is_site_admin`: User is currently a **Site Admin**
- `as_self`: `user_id ` must match requesting User's ID

## API Details

### GET [/users](): 

Request URL

- `http://127.0.0.1:8000/api/users`

Request parameters / data

- None

Response (`200`)

- Paginated JSON object

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "display_name": "Michael J. Stealey",
      "email": "stealey@unc.edu",
      "user_id": 1,
      "username": "stealey@unc.edu"
    }
  ]
}
```

Example

```console
$ curl -s -X "GET" -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" "http://127.0.0.1:8000/api/users" | jq .
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "display_name": "Michael J. Stealey",
      "email": "stealey@unc.edu",
      "user_id": 1,
      "username": "stealey@unc.edu"
    }
  ]
}
```

Notes

### POST [/users](): 

Request URL

- Not Implmented

Request parameters / data

- Not Implmented

Response (`405`)

- JSON object

```json
{
  "detail": "Method \"POST: /users\" not allowed."
}
```

Example

```console
$ curl -s -X "POST" -d ${DATA} -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" "http://127.0.0.1:8000/api/users" | jq .
{
  "detail": "Method \"POST: /users\" not allowed."
}
```

Notes

### GET [/users/{user_id}](): 

Request URL

- `http://127.0.0.1:8000/api/users/{user_id}`

Request parameters / data

- None

Response

- JSON object

```json
{
  "aerpaw_roles": [
    "pi"
  ],
  "display_name": "Michael J. Stealey",
  "email": "stealey@unc.edu",
  "is_active": true,
  "oidc_sub": "http://cilogon.org/serverA/users/242181",
  "profile": {},
  "user_id": 1,
  "username": "stealey@unc.edu"
}
```

Example

```console
$ curl -s -X "GET" -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" "http://127.0.0.1:8000/api/users/1" | jq .
{
  "aerpaw_roles": [
    "pi"
  ],
  "display_name": "Michael J. Stealey",
  "email": "stealey@unc.edu",
  "is_active": true,
  "oidc_sub": "http://cilogon.org/serverA/users/242181",
  "profile": {},
  "user_id": 1,
  "username": "stealey@unc.edu"
}
```

Notes

### PUT [/users/{user_id}](): 

Request URL

- `http://127.0.0.1:8000/api/users/{user_id}`

Request parameters / data

```json
{
  "display_name": "Michael J. Stealey"
}
```

Response (`204`)

- No Content

Example (showing headers)

```console
$ curl -s -i -X "PUT" -d ${DATA} -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" "http://127.0.0.1:8000/api/users/1"
HTTP/1.1 204 No Content
Date: Mon, 13 Jun 2022 20:48:27 GMT
Server: WSGIServer/0.2 CPython/3.10.4
Vary: Accept
Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
X-Frame-Options: DENY
Content-Length: 0
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Cross-Origin-Opener-Policy: same-origin
```

Notes

- `display_name` is the only field which can be updated at this time

### PATCH [/users/{user_id}](): 

Request URL

- `http://127.0.0.1:8000/api/users/{user_id}`

Request parameters / data

```json
{
  "display_name": "Michael J. Stealey"
}
```

Response (`204`)

- No Content

Example (showing headers)

```console
$ curl -s -i -X "PATCH" -d ${DATA} -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" "http://127.0.0.1:8000/api/users/1"
HTTP/1.1 204 No Content
Date: Mon, 13 Jun 2022 20:48:37 GMT
Server: WSGIServer/0.2 CPython/3.10.4
Vary: Accept
Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
X-Frame-Options: DENY
Content-Length: 0
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Cross-Origin-Opener-Policy: same-origin
```

Notes
   
- `display_name` is the only field which can be updated at this time

### DELETE [/users/{user_id}](): 

Request URL

- `http://127.0.0.1:8000/api/users/{user_id}`

Request parameters / data

- None

Response (`405`)

- Paginated JSON object

```json
{
  "detail": "Method \"DELETE: /users/{user_id}\" not allowed."
}
```

Example

```console
$ curl -s -X "DELETE" -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" "http://127.0.0.1:8000/api/users/1" | jq .
{
  "detail": "Method \"DELETE: /users/{user_id}\" not allowed."
}
```

Notes

