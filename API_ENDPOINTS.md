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
    - Parameter (optional): `number`
        - e.g. `/canonical-experiment-number/current?number=100`

## canonical-experiment-resource

### `canonical-experiment-resource`

- **GET** paginated list of all canonical experiment resource definitions
    - Access: role = `operator`
    - Parameter (optional): `experiment_id`
        - e.g. `/canonical-experiment-resource?experiment_id=10`
    - Parameter (optional): `resource_id`
        - e.g. `/canonical-experiment-resource?resource_id=5`
    - Parameter (optional): `experiment_id` and `resource_id`
        - e.g. `/canonical-experiment-resource/experiment_id=10&resource_id=5`
        
### `canonical-experiment-resource/{int:pk}`

- **GET** detailed information about a single canonical canonical experiment resource definition by ID
    - Access: role = `operator` 

## experiments

### `/experiments`

- **GET** paginated list of all experiments
    - Access: role = `operator`
    - Access: user has project membership in the project containing the experiment
    - Parameter (optional): `search`
        - e.g. `/experiments?search=wheeler`

### `/experiments/{int:pk}`

- **GET** detailed information about a single experiment by ID
    - Access: role = `operator`
    - Access: user has project membership in the project containing the experiment
- **POST** create new experiment
    - Access: user has experiment membership
    - Data (required):
        - `description` - experiment description
        - `name` - experiment name
        - `project_id` - ID of project which to add experiment to
        - Example:

            ```json
            {
                "description": "my project description",
                "name": "my project",
                "project_id": 5
            }
            ```

### `/experiments/{int:pk}/membership`

- **GET**: list of `experiment_members` for a single experiment by ID
    - Access: user has experiment membership
- **PUT**: update `experiment_members ` for a single experiment by ID
    - Access: user has experiment membership
    - Data (optional):
        - `experiment_members` - array of user IDs (users must also have membership within the project associated to the experiment)
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

```
{
    "description": "my project description",
    "is_public": true,
    "name": "my project"
}
```

### `/projects/{int:pk}`

### `/projects/{int:pk}/experiments`

### `/projects/{int:pk}/membership`

## resources

### `/resources`

### `/resources/{int:pk}`

### `/resources/{int:pk}/experiments`

### `/resources/{int:pk}/projects`

## sessions

### `/sessions`

### `/sessions/{int:pk}`

## user-experiment

### `/user-experiment`

### `/user-experiment/{int:pk}`

## user-project

### `/user-project`

### `/user-project/{int:pk}`

## users

### `/users`

### `/users/{int:pk}`

### `/users/{int:pk}/credentials`

### `/users/{int:pk}/tokens`

### `/token/refresh`


```
# Project
{
    "description": "stealey test description",
    "is_public": true,
    "name": "stealey test project"
}

# Experiment
{
    "description": "stealey test experiment",
    "name": "stealey test experiment",
    "project_id": 2
}
```
