# Projects and ProjectPersonnel

details

- Uses [mixins](./mixins.md)

## Database 

### Model `Projects`

```
- created (from AuditModelMixin)
- created_by (from AuditModelMixin)
- description
- id (from Basemodel)
- is_public
- modified (from AuditModelMixin)
- modified_by (from AuditModelMixin)
- name
- project_creator (fk)
- uuid
```

### Methods

- `is_something`: return `True` if user is **Is Something**

### Model `ProjectPersonnel`

```
granted_by
granted_date
id (from Basemodel)
is_project_member
is_project_owner
project
user
```

## API

### Overview

"X" in the table below denotes User permission to interact with the endpoint

Endpoint | `is_active` | `is_experimenter` | `is_pi` | `is_operator` | `is_site_admin` | `creator` | `member` | `owner`
:--------|:-----------:|:-----------------:|:-------:|:-------------:|:---------------:|:-----------:|:---------:|:--------:|:------:
GET: [/projects]() | X | X | X | X | X | X | X | X
POST: [/projects]() | | | X | | |
GET: [/projects/{project_id}]() | X | X | X | X | X | X | X | X
PUT: [/projects/{project_id}]() | | | | | | X | | X
PATCH: [/projects/{project_id}]() | | | | | | X | | X
DELETE: [/projects/{project_id}]() | | | | | | X | 

Notes:

- `is_active`: User is currently Active
- `is_experimenter`: User is currently an **Exerimenter**
- `is_pi`: User is currently a **PI**
- `is_operator`: User is currently an **Operator**
- `is_site_admin`: User is currently a **Site Admin**
- `creator`: `project_creator` must match requesting User's ID
- `member`: `project_member` must match requesting User's ID
- `owner`: `project_owner` must match requesting User's ID

## API Details

### GET [/projects](): 

Request URL

- `http://127.0.0.1:8000/api/projects `

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


### POST [/projects](): 

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


### GET [/projects/{project_id}](): 

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

### PUT [/projects/{project_id}](): 

Request URL

- `http://127.0.0.1:8000/api/projects/{project_id}`

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

   

### PATCH [/projects/{project_id}](): 

Request URL

- `http://127.0.0.1:8000/api/projects/{project_id}`

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
   

### DELETE [/projects/{project_id}](): 

Request URL

- `http://127.0.0.1:8000/api/projects/{project_id}`

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

