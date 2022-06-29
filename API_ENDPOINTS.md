# API Endpoints

Provide examples of how to interrogate the API endpoints remotely using [cURL](https://developer.ibm.com/articles/what-is-curl-command/).

- Prior to executing any cURL commands the user should export their `access_token` into their local environment
- The example token below has been shortened for readability

    ```bash
    export TOKEN='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...UqbthpwM4_be4d1or2qpdd_w_3TjjDxiT85f3kvwWbI'
    ```

The user `TOKEN` is then attached as part of the request header along with other information when issuing a cURL command.

Common Headers:

- Bearer Token: `-H "Authorization: Bearer ${TOKEN}"`
- **GET** requests: `-H "Accept: application/json"`
- **POST**, **PUT**, **PATCH** requests: `-H "Content-Type: application/json"`
    - Any request that includes request data as part of the body in JSON format (`-d ${DATA}` where `DATA` is in JSON format)


The request header "preamble" will be excluded from the examples below for readability, but it is required for the cURL command to execute successfully within the appropriate context option (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).

## canonical-experiment-number

### `/canonical-experiment-number`

- **GET** paginated list of all used (but not deleted) canonical experiment numbers
    - Access: role = `operator`

### `/canonical-experiment-number/{int:pk}`

- **GET** detailed information about a single canonical number by ID 
    - Access: role = `operator`

### `/canonical-experiment-number/current`

- **GET** the current canonical experiment number which would be issued to the next experiment
    - Access: user `is_active`
- **PUT** a new current canonical experiment number
    - Access: role = `operator`
    - Parameter (optional): `number` as integer
        - e.g. `/canonical-experiment-number/current?number=100`

## canonical-experiment-resource

### `/canonical-experiment-resource`

- **GET** paginated list of all canonical experiment resource definitions
    - Access: role = `operator`
    - Parameter (optional): `experiment_id`
        - e.g. `/canonical-experiment-resource?experiment_id=10`
    - Parameter (optional): `resource_id`
        - e.g. `/canonical-experiment-resource?resource_id=5`
    - Parameter (optional): `experiment_id` and `resource_id`
        - e.g. `/canonical-experiment-resource?experiment_id=10&resource_id=5`
        
### `/canonical-experiment-resource/{int:pk}`

- **GET** detailed information about a single canonical canonical experiment resource definition by ID
    - Access: role = `operator` 

## experiments

### `/experiments`

- **GET** paginated list of all experiments
    - Access: role = `operator`
    - Access: user has project membership in the project containing the experiment
    - Parameter (optional): `search`
        - e.g. `/experiments?search=wheeler`
- **POST** create new experiment
    - Access: user has experiment membership
    - Data (required):
        - `description` - experiment description as string
        - `name` - experiment name as string
        - `project_id` - ID of project which to add experiment to as integer
        - Example:

            ```json
            {
                "description": "my project description",
                "name": "my project",
                "project_id": 5
            }
            ```

### `/experiments/{int:pk}`

- **GET** detailed information about a single experiment by ID
    - Access: role = `operator`
    - Access: user has project membership in the project containing the experiment

### `/experiments/{int:pk}/membership`

- **GET**: list of `experiment_members` for a single experiment by ID
    - Access: user has experiment membership
- **PUT**: update `experiment_members ` for a single experiment by ID
    - Access: user has experiment membership
    - Data (optional):
        - `experiment_members` - experiment members by user ID (users must have membership within the project associated to the experiment) as array of integers
        - Example:
            
            ```json
            {
                "experiment_members": [1, 3, 10]
            }
            ```

### `/experiments/{int:pk}/resources`

- **GET**: list of `experiment_resources` for a single experiment by ID
    - Access: user has experiment membership
- **PUT**: update `experiment_resources ` for a single experiment by ID
    - Access: user has experiment membership
    - Data (optional):
        - `experiment_resources` - array of resource IDs
        - Example:
            
            ```json
            {
                "experiment_resources": [1, 2]
            }
            ```
            
## projects

### `/projects`

- **GET** paginated list of all projects
    - Access: user is active
    - Parameter (optional): `search`
        - e.g. `/projects?search=demo`
- **POST** create new project
    - Access: role = `pi`
    - Data (required):
        - `description` - project description as string
        - `is_public` - project is publicly viewable as boolean
        - `name` - project name as string
        - Example:

            ```json
            {
                "description": "my project description",
                "is_public": true,
                "name": "my project"
            }
            ```

### `/projects/{int:pk}`

- **GET** detailed information about a single project by ID
    - Access: role = `operator`
    - Access: user has project membership
    - Access: user is active and project `is_public` (limited view)

### `/projects/{int:pk}/experiments`

- **GET**: list of `experiments` for a single project by ID
    - Access: user has project membership

### `/projects/{int:pk}/membership`

- **GET**: list of `project_members` and `project_owners` for a single project by ID
    - Access: user has project membership
- **PUT**: update `project_members` and/or `project_owners` for a single project by ID
    - Access: user is `project_creator`
    - Access: user is `project_owner`
    - Data (optional):
        - `project_members` - project members by user ID as array of integers
        - `project_owners` - project owners by user ID as array of integers
        - Example:
            
            ```json
            {
                "project_members": [1, 3, 10],
                "project_owners": [1]
            }
            ```

## resources

### `/resources`

- **GET** paginated list of all resources
    - Access: user is active
    - Parameter (optional): `search`
        - e.g. `/resources?search=ugv`
- **POST** create new resource
    - Access: role = `operator`
    - Data (* denotes required):
        - *`description` - resource description as string
        - `hostname` - resource hostname as string
        - `ip_address` - resource IP Address as string
        - *`is_active` - resource is active as boolean (default = `False`)
        - `location` - resource location as string
        - *`name` - resource name as string
        - `ops_notes` - operator notes as string
        - *`resource_class` - resource class as string (default = ``)
        - *`resource_mode` - resource mode as string
        - *`resource_type` - resource type as string
        - Example:

            ```json
            {
                "description": "Centennial Campus Node 1",
                "hostname": "aerpaw182",
                "ip_address": "123.23.34.678",
                "is_active": true,
                "location": "Centennial Campus",
                "name": "CC1",
                "ops_notes": "",
                "resource_class": "canonical",
                "resource_mode": "testbed",
                "resource_type": "AFRN"
            }
            ```

### `/resources/{int:pk}`

- **GET** detailed information about a single resource by ID
    - Access: user is active

### `/resources/{int:pk}/experiments`

### `/resources/{int:pk}/projects`

## sessions

### `/sessions`

- **GET** paginated list of all experiment sessions
    - Access: role = `operator`
    - Parameter (optional): `experiment_id`
        - e.g. `/sessions?experiment_id=10`

### `/sessions/{int:pk}`

- **GET** detailed information about a single experiment session by ID 
    - Access: role = `operator`

## user-experiment

### `/user-experiment`

- **GET** paginated list of all user experiment definitions
    - Access: role = `operator`
    - Parameter (optional): `experiment_id`
        - e.g. `/user-experiment?experiment_id=10`
    - Parameter (optional): `user_id`
        - e.g. `/user-experiment?user_id=5`
    - Parameter (optional): `experiment_id` and `user_id `
        - e.g. `/user-experiment?experiment_id=10&user_id=5`

### `/user-experiment/{int:pk}`

- **GET** detailed information about a single user experiment definition by ID 
    - Access: role = `operator`

## user-project

### `/user-project`

- **GET** paginated list of all user project definitions
    - Access: role = `operator`
    - Parameter (optional): `project_id`
        - e.g. `/user-project?project_id=10`
    - Parameter (optional): `user_id`
        - e.g. `/user-project?user_id=5`
    - Parameter (optional): `project_id` and `user_id `
        - e.g. `/user-project?project_id=10&user_id=5`

### `/user-project/{int:pk}`

- **GET** detailed information about a single user project definition by ID 
    - Access: role = `operator`

## users

### `/users`

- **GET** paginated list of all users
    - Access: user is active
    - Parameter (optional): `search`
        - e.g. `/projects?search=bob`

### `/users/{int:pk}`

- **GET** detailed information about a single user by ID
    - Access: user as self
    - Access: user is active (limited view)

### `/users/{int:pk}/credentials`

### `/users/{int:pk}/tokens`

- **GET** detailed information about tokens by user by ID
    - Access: user as self

### `/token/refresh`

- **POST** generate a new `access_token`
    - Access: user as self
    - Data (required): `refresh_token`
    - **NOTE**: this endpoint does not update data in the User's profile
    - Example:
    
        ```json
        {
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...n3VM2kzzXOF4AWOSb4M3QmEgitnByaokmecTO423vXI"
        }
        ```

## cURL Examples

Set up basic exports

```console
export API_URL='http://aerpaw-dev.renci.org:8000/api'
export ACCESS_TOKEN='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...yYACY9QZqmKXppXluUeW_A95lZVLqm9Xt0AXFCAV1Xg'
```

### create a new project

Define a request body in JSON format for the project to POST

```console
PROJECT='{
    "description": "demo project description",
    "is_public": true,
    "name": "demo project"
}'
```

Use the POST command to create a new project

```console
$ curl -X "POST" -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "Content-Type: application/json" -d ${PROJECT} "${API_URL}/projects"

{
  "created_date": "2022-06-28T20:56:25.581196-04:00",
  "description": "demo project description",
  "is_public": true,
  "last_modified_by": 1,
  "modified_date": "2022-06-28T20:56:25.581243-04:00",
  "name": "demo project",
  "project_creator": 1,
  "project_id": 3,
  "project_members": [],
  "project_owners": [
    {
      "granted_by": 1,
      "granted_date": "2022-06-28T20:56:25.586423-04:00",
      "user_id": 1
    }
  ]
}
```

From the above we can see a new project was created with `project_id=3`

### add some project members

Search for "Yufeng" from the users endpoint

```console
$ curl -X "GET" -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "Accept: application/json" "${API_URL}/users?search=yufeng"

{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "display_name": "Yufeng Xin",
      "email": "yxin@email.unc.edu",
      "user_id": 2,
      "username": "yxin@email.unc.edu"
    }
  ]
}
```

Yufeng has a `user_id=2` which is used to add him to the project members

Define a request body in JSON format for project members to PUT

```console
PROJECT_MEMBERS='{
    "project_members": [2]
}'
```
And then use the PUT command to add the project members

```console
$ curl -X "PUT" -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "Content-Type: application/json" -d ${PROJECT_MEMBERS} "${API_URL}/projects/3/membership"

{
  "project_members": [
    {
      "granted_by": 1,
      "granted_date": "2022-06-28T21:04:05.604689-04:00",
      "user_id": 2
    }
  ],
  "project_owners": [
    {
      "granted_by": 1,
      "granted_date": "2022-06-28T20:56:25.586423-04:00",
      "user_id": 1
    }
  ]
}
```

### create an experiment

Next define an experiment to the project with JSON

```console
EXPERIMENT='{
    "description": "demo experiment description",
    "name": "demo experiment",
    "project_id": 3
}'
```

And POST to the experiments endpoint

```console
$ curl -X "POST" -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "Content-Type: application/json" -d ${EXPERIMENT} "${API_URL}/experiments"

{
  "canonical_number": 1,
  "created_date": "2022-06-28T21:08:40.290333-04:00",
  "description": "demo experiment description",
  "experiment_creator": 1,
  "experiment_id": 3,
  "experiment_members": [
    {
      "granted_by": 1,
      "granted_date": "2022-06-28T21:08:40.292835-04:00",
      "user_id": 1
    }
  ],
  "experiment_state": "saved",
  "is_canonical": false,
  "is_retired": false,
  "last_modified_by": 1,
  "modified_date": "2022-06-28T21:08:40.290350-04:00",
  "name": "demo experiment",
  "project_id": 3,
  "resources": []
}
```
We can see that a new experiment was created with `experiment_id=3` and it's linked to `project_id=3`

Finally find a canonical resource named "CC1" to add to the experiment

```console
$ curl -X "GET" -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "Accept: application/json" "${API_URL}/resources?search=cc1"


  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "description": "Centennial Campus Node 1",
      "is_active": true,
      "location": "Centennial Campus",
      "name": "CC1",
      "resource_class": "canonical",
      "resource_id": 1,
      "resource_mode": "testbed",
      "resource_type": "AFRN"
    }
  ]
}
```

CC1 has `resource_id=1`, define some JSON to experess this

```console
EXP_RESOURCES='{
    "experiment_resources": [1]
}'
```

Use PUT to add the resource to the experiment

```console
$ curl -X "PUT" -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "Content-Type: application/json" -d ${EXP_RESOURCES} "${API_URL}/experiments/3/resources"

[
  {
    "description": "Centennial Campus Node 1",
    "is_active": true,
    "location": "Centennial Campus",
    "name": "CC1",
    "resource_class": "canonical",
    "resource_id": 1,
    "resource_mode": "testbed",
    "resource_type": "AFRN"
  }
]
```
We can see the array of resource associate to the project (currently just CC1)

With all of the resources for the experiment of class "canonical", the experiment itself should also be denoted as "canonical"

```console
$ curl -X "GET" -H "Authorization: Bearer ${ACCESS_TOKEN}" -H "Accept: application/json" "${API_URL}/experiments/3"

{
  "canonical_number": 1,
  "created_date": "2022-06-28T21:08:40.290333-04:00",
  "description": "demo experiment description",
  "experiment_creator": 1,
  "experiment_id": 3,
  "experiment_members": [
    {
      "granted_by": 1,
      "granted_date": "2022-06-28T21:08:40.292835-04:00",
      "user_id": 1
    }
  ],
  "experiment_state": "saved",
  "is_canonical": true,
  "is_retired": false,
  "last_modified_by": 1,
  "modified_date": "2022-06-28T21:15:06.635979-04:00",
  "name": "demo experiment",
  "project_id": 3,
  "resources": [
    1
  ]
}
```
