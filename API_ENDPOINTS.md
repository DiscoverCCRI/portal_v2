# API Endpoints

Provide examples of how to interrogate the API endpoints remotely using [cURL](https://developer.ibm.com/articles/what-is-curl-command/).

- Prior to executing any cURL commands the user should export their `access_token` into their local environment
- The example token below has been shortened for readability

    ```bash
    export TOKEN='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...UqbthpwM4_be4d1or2qpdd_w_3TjjDxiT85f3kvwWbI'
    ```

The user `TOKEN` will be attached as part of the request header, along with other information, when issuing a cURL command.

```bash
curl -X "GET" -H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json" 
```

Much of this request header "preamble" will be excluded from the examples below for readability, but it is required for the cURL command to execute successfully.

## canonical-experiment-number

`/canonical-experiment-number` paginated

- **GET** paginated list of all used (but not deleted) canonical experiment numbers (Access level `operator`)

`/canonical-experiment-number/{int:pk}`

- **GET** detailed information about a single canonical number by ID (Access level `operator`)

`/canonical-experiment-number/current`

- **GET** the current canonical experiment number which would be issued to the next experiment (Access level `is_active`)
- **PUT** a new current canonical experiment number with parameter: `number` (e.g. `?number=100`) (Access level `operator`)

## canonical-experiment-resource

`canonical-experiment-resource` paginated

- **GET** paginated list of all canonical experiment resource definitions with parameters: `experiment_id` and `resource_id` (e.g. `?experiment_id=10` or `?resource_id=5` or `?experiment_id=10&resource_id=5`) (Access level `operator`)

`canonical-experiment-resource/{int:pk}`

- **GET** detailed information about a single canonical canonical experiment resource definition by ID (Access level `operator`) 

## experiments

`/experiments` paginated

`/experiments/{int:pk}`

`/experiments/{int:pk}/membership`

`/experiments/{int:pk}/resources`

## projects

`/projects` paginated

`/projects/{int:pk}`

`/projects/{int:pk}/experiments`

`/projects/{int:pk}/membership`

## resources

`/resources` paginated

`/resources/{int:pk}`

`/resources/{int:pk}/experiments`

`/resources/{int:pk}/projects`

## sessions

`/sessions` paginated

`/sessions/{int:pk}`

## user-experiment

`/user-experiment` paginated

`/user-experiment/{int:pk}`

## user-project

`/user-project` paginated

`/user-project/{int:pk}`

## users

`/users` paginated

`/users/{int:pk}`

`/users/{int:pk}/credentials`

`/users/{int:pk}/tokens`

`/token/refresh` <-- provided by DRF

