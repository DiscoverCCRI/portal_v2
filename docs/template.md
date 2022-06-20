# Template

details

- Uses [mixins](./mixins.md)

## Database 

### Model

```
- created (from AuditModelMixin)
- created_by (from AuditModelMixin)
- id (from Basemodel)
- modified (from AuditModelMixin)
- modified_by (from AuditModelMixin)
- uuid
```

### Methods

- `is_something`: return `True` if user is **Is Something**

## API

### Overview

"X" in the table below denotes User permission to interact with the endpoint

Endpoint | `is_active` | `is_experimenter` | `is_pi` | `is_operator` | `is_site_admin` | `as_self`
:--------|:-----------:|:-----------------:|:-------:|:-------------:|:---------------:|:-----:
GET: [/examples]() | X | X | X | X | X |
POST: [/examples]() | | | | | |
GET: [/examples/{example_id}]() | X | X | X | X | X |
PUT: [/examples/{example_id}]() | X | X | X | X | X | X
PATCH: [/examples/{example_id}]() | X | X | X | X | X | X
DELETE: [/examples/{example_id}]() | | | | | |

Notes:

- `is_active`: User is currently Active
- `is_experimenter`: User is currently an **Exerimenter**
- `is_pi`: User is currently a **PI**
- `is_operator`: User is currently an **Operator**
- `is_site_admin`: User is currently a **Site Admin**
- `as_self`: `user_id ` must match requesting User's ID

## API Details

### GET [/examples](): 

Request URL

- `http://127.0.0.1:8000/api/examples`

Request parameters / data

- None

Response (`200`)

- Paginated JSON object

```json
{}
```

Example

```console
$ curl -s -X "GET" -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" "http://127.0.0.1:8000/api/examples" | jq .
{}
```

Notes


### POST [/examples](): 

Request URL

- Not Implmented

Request parameters / data

- Not Implmented

Response (`405`)

- JSON object

```json
{}
```

Example

```console
$ curl -s -X "POST" -d ${DATA} -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" "http://127.0.0.1:8000/api/examples" | jq .
{}
```

Notes


### GET [/examples/{example_id}](): 

Request URL

- `http://127.0.0.1:8000/api/examples/{example_id}`

Request parameters / data

- None

Response

- JSON object

```json
{}
```

Example

```console
$ curl -s -X "GET" -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" "http://127.0.0.1:8000/api/examples/1" | jq .
{}
```

Notes

### PUT [/examples/{example_id}](): 

Request URL

- `http://127.0.0.1:8000/api/examples/{example_id}`

Request parameters / data

```json
{}
```

Response (204)

- No Content

Example (showing headers)

```console
$ curl -s -i -X "PUT" -d ${DATA} -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" "http://127.0.0.1:8000/api/examples/1"
HTTP/1.1 204 No Content
```

Notes

   

### PATCH [/examples/{example_id}](): 

Request URL

- `http://127.0.0.1:8000/api/examples/{example_id}`

Request parameters / data

```json
{}
```

Response (204)

- No Content

Example (showing headers)

```console
$ curl -s -i -X "PATCH" -d ${DATA} -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" "http://127.0.0.1:8000/api/examples/1"
HTTP/1.1 204 No Content
```

Notes
   

### DELETE [/examples/{example_id}](): 

Request URL

- `http://127.0.0.1:8000/api/examples/{example_id}`

Request parameters / data

- None

Response (`405`)

- Paginated JSON object

```json
{}
```

Example

```console
$ curl -s -X "DELETE" -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" "http://127.0.0.1:8000/api/examples/1" | jq .
```

Notes

