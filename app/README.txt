Code Functionality - utils.py

    Initialization:
        Sets up OpenAI and Elasticsearch API configurations.
        Initializes logging for debugging and monitoring.

    Token Counting:
        Uses the tiktoken library to estimate token counts for queries.

    Embedding Retrieval:
        Retrieves embeddings from the OLLAMA API, handling errors gracefully.

    Elasticsearch Data Fetching:
        Uses aggregations to fetch hierarchical data (supercategories, categories, subcategories).
        Performs vector searches to find the most relevant examples.

    Classification:
        Generates a structured prompt, either with or without vector search examples.
        Uses a hierarchical structure to ensure accurate classification.

    Output:
        Returns the most relevant supercategory, category, and subcategory, along with elapsed processing time.

Key Observations

    Error Handling:
        The code effectively handles errors, such as failed requests or Elasticsearch issues, with meaningful logging.

    Hierarchical Structure:
        The hierarchical classification ensures that the system selects the most relevant category and subcategory.

    Prompt Design:
        Prompts are detailed and provide clear instructions to the model, ensuring structured responses.



API Documentation - api.py

Overview

This Flask-based application provides various API endpoints to manage user registration, login, classification tasks, and memory storage using Elasticsearch. It incorporates JWT authentication for security, Redis for caching and rate-limiting, and Elasticsearch for storing and querying classified data.
Endpoints
1. /register - Register a new user

    Method: POST

    Description: Registers a new user in the system. Requires a valid JWT token for authentication.

    Request Body:

{
    "username": "string",
    "password": "string"
}

Response:

    201: User registered successfully
    400: Missing username or password, or user already exists

Example:

    {
        "msg": "User registered successfully"
    }

2. /login - Login a user

    Method: POST

    Description: Logs a user in and returns a JWT access token. No authentication required to access.

    Request Body:

{
    "username": "string",
    "password": "string"
}

Response:

    200: Successfully logged in with a JWT token
    401: Invalid credentials

Example:

    {
        "access_token": "JWT_ACCESS_TOKEN"
    }

3. /classify - Classify a user query

    Method: POST

    Description: Classifies a user query using AI. Caching and rate limiting are supported with Redis.

    Authentication: Requires JWT token

    Request Body:

{
    "title": "string",
    "message": "string"
}

Response:

    200: AI classification result (or cached response)
    400: Missing required fields (title, message)
    429: Rate limit exceeded

Example:

{
    "response": {
        "supercategory": "string",
        "category": "string",
        "subcategory": "string"
    },
    "cached": "false",
    "time": 2.47
}

4. /category-add - Store a new category

    Method: POST

    Description: Stores a new category with its embedding in Elasticsearch.

    Authentication: Requires JWT token

    Request Body:

{
    "Category": "string",
    "Supercategory": "string",
    "Subcategory": "string",
    "CategoryCode": "string",
    "SubcategoryCode": "string",
    "Significance": "string",
    "TCID": integer
}

Response:

    201: Document stored successfully
    400: Missing required fields
    500: Error storing document

Example:

    {
        "msg": "Document stored successfully"
    }


6. /category-delete - Delete Category by TCID
Description:

This endpoint allows users to delete a category from the system based on the unique TCID (Category ID). The category document will be removed from the Elasticsearch index if found.
HTTP Method:

DELETE
Endpoint:

/category-delete
Authentication:

JWT (JSON Web Token) authentication is required to access this endpoint. The user must be authenticated before they can delete a category.
Request Body:

The request body must contain the TCID field, which uniquely identifies the category to be deleted.
Request JSON Example:

{
  "TCID": 12345
}

    TCID (required): The unique identifier of the category to be deleted.

Responses:
Success Response:

    Status Code: 200 OK
    Response Body:

    {
      "msg": "Category deleted successfully"
    }

Failure Responses:

    Status Code: 400 Bad Request
        Response Body:

    {
      "msg": "TCID is required"
    }

    Occurs if the TCID is not provided in the request body.

Status Code: 404 Not Found

    Response Body:

    {
      "msg": "Category not found"
    }

    Occurs if no category with the provided TCID is found in the system.

Status Code: 500 Internal Server Error

    Response Body:

        {
          "msg": "Error deleting category: <error message>"
        }

        Occurs if an unexpected error happens while processing the request or interacting with Elasticsearch.

7. /category-update - Update Category by TCID
Description:

This endpoint allows users to update an existing category document in the system based on the unique TCID. The document is updated with the new category details provided in the request body. This includes fields such as CATEGORY, SUPERCATEGORY, SUBCATEGORY, CATEGORY_CODE, SUBCATEGORY_CODE, SIGNIFICANCE, and recalculated embedding.
HTTP Method:

PUT
Endpoint:

/category-update
Authentication:

JWT (JSON Web Token) authentication is required to access this endpoint. The user must be authenticated before they can update a category.
Request Body:

The request body must contain the TCID field (unique category identifier) and the other category fields that are to be updated.
Request JSON Example:

{
  "TCID": 12345,
  "Category": "Updated Category Name",
  "Supercategory": "Updated Supercategory",
  "Subcategory": "Updated Subcategory",
  "CategoryCode": "UpdatedCode",
  "SubcategoryCode": "UpdatedSubcode",
  "Significance": "High"
}

    TCID (required): The unique identifier of the category to be updated.
    Category (required): The name of the category.
    Supercategory (optional): The supercategory of the category. Defaults to "Unknown" if not provided.
    Subcategory (optional): The subcategory of the category. Defaults to "Unknown" if not provided.
    CategoryCode (optional): A code associated with the category. Defaults to "None" if not provided.
    SubcategoryCode (optional): A code associated with the subcategory. Defaults to "None" if not provided.
    Significance (optional): The significance of the category. Defaults to "Low" if not provided.

Responses:
Success Response:

    Status Code: 200 OK
    Response Body:

    {
      "msg": "Category updated successfully"
    }

Failure Responses:

    Status Code: 400 Bad Request
        Response Body:

    {
      "msg": "TCID and category are required"
    }

    Occurs if the TCID or Category is not provided in the request body.

Status Code: 404 Not Found

    Response Body:

    {
      "msg": "Category not found"
    }

    Occurs if no category with the provided TCID is found in the system.

Status Code: 500 Internal Server Error

    Response Body:

{
  "msg": "Error updating category: <error message>"
}

Occurs if an unexpected error happens while processing the request or interacting with Elasticsearch.






8. /example-add - Store a new example

    Method: POST

    Description: Stores a new example document with its embedding in Elasticsearch.

    Authentication: Requires JWT token

    Request Body:

{
    "Title": "string",
    "Message": "string",
    "Category": "string",
    "Supercategory": "string",
    "Subcategory": "string",
    "TCID": integer
}

Response:

    201: Document stored successfully
    400: Missing required fields
    500: Error storing document

Example:

    {
        "msg": "Document stored successfully"
    }

Configurations

    JWT Expiration: Config.JWT_EXPIRATION - The time after which the JWT token will expire.
    Rate Limiting: Uses Redis to store the rate limit count per user with Config.RATE_LIMIT_MAX_REQUESTS and a time window of Config.RATE_LIMIT_WINDOW_SECONDS.
    Redis Cache Expiration: Config.REDIS_CACHE_EXPIRATION - The time after which cached responses expire.
    Elasticsearch URL: Config.ELASTICSEARCH_URL - The URL of the Elasticsearch instance.

Error Handling

    400 Bad Request: Missing or invalid input.
    401 Unauthorized: Invalid credentials or missing JWT token.
    429 Too Many Requests: Rate limit exceeded.
    500 Internal Server Error: Error processing the request, such as issues with Elasticsearch or Redis.

Logging

The application uses Python’s logging module to log key actions and errors:

    Logs for API access (INFO)
    Warnings for missing or invalid inputs (WARNING)
    Errors during operations (ERROR)