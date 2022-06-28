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
    - Access: role = `operator`
    - Access: user is active
    - Parameter (optional): `search`
        - e.g. `/projects?search=demo`
- **POST** create new project
    - Access: role = `pi`
    - Data (required):
        - `description` - project description as string
        - `is_public` - project is publicly vieable as boolean
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

### `/sessions/{int:pk}`

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

### `/users/{int:pk}`

### `/users/{int:pk}/credentials`

### `/users/{int:pk}/tokens`

### `/token/refresh`

## Examples

Set up basic exports

```console
export API_URL=''
export ACCESS_TOKEN=''
```

### create a new project

```console
PROJECT='{
    "description": "demo project description",
    "is_public": true,
    "name": "demo project"
}'
```

### create an experiment

```console
EXPERIMENT='{
    "description": "demo experiment description",
    "name": "demo experiment",
    "project_id": 2
}'
```
