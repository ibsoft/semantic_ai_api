API Documentation
Overview

This API provides functionalities for user registration, authentication, text classification, memory storage, and query handling using Flask. It integrates Elasticsearch for text indexing and search, Redis for caching and rate-limiting, and JWT for secure user authentication.
Prerequisites

    Elasticsearch: Text classification and document storage are backed by Elasticsearch.
    Redis: Used for caching and rate-limiting (optional).
    Flask-JWT-Extended: Manages authentication via JWT tokens.
    Flask-SQLAlchemy: Provides ORM support for user management.

Endpoints
1. User Registration

POST /register

Registers a new user by storing their username and password securely.

Request Body:

{
  "username": "example_user",
  "password": "example_password"
}

Response:

    201: User registered successfully.

{ "msg": "User registered successfully" }

400: Missing or duplicate username.

    { "msg": "Missing username or password" }
    { "msg": "User already exists" }

2. User Login

POST /login

Authenticates a user and generates a JWT access token.

Request Body:

{
  "username": "example_user",
  "password": "example_password"
}

Response:

    200: JWT token provided.

{ "access_token": "jwt_token_string" }

401: Invalid credentials.

    { "msg": "Invalid credentials" }

3. Text Classification

POST /classify

Classifies user queries with caching and rate-limiting.

Authentication: JWT required.

Request Body:

{
  "title": "Sample Title",
  "message": "Sample Message"
}

Response:

    200: Classification result.

{
  "response": "classification_result",
  "cached": "true/false",
  "time": 0.23
}

400: Missing title or message.

{ "msg": "Title and message are required" }

429: Rate limit exceeded.

    { "msg": "Rate limit exceeded, try again later." }

Caching:
Results are stored in Redis with configurable expiration time (Config.REDIS_CACHE_EXPIRATION).

Rate Limiting:
Limits are enforced using Redis (Config.RATE_LIMIT_MAX_REQUESTS).
4. Store Memory

POST /memory

Stores a new document with category, subcategory, description, and title.

Authentication: JWT required.

Request Body:

{
  "Title": "Sample Title",
  "Category": "Sample Category",
  "Subcategory": "Sample Subcategory",
  "Subsubcategory": "Sample Sub-Subcategory",
  "Description": "Sample Description"
}

Response:

    201: Document stored successfully.

{ "msg": "Document stored successfully" }

400: Missing parameters.

{ "msg": "Title, Category, Subcategory, Subsubcategory, and Description are required" }

500: Error generating embedding or storing document.

    { "msg": "Error storing document: <error_details>" }

Configuration

Environment Variables:

    ELASTICSEARCH_URL: URL for Elasticsearch.
    REDIS_CACHE_EXPIRATION: Expiration time for cached queries.
    RATE_LIMIT_MAX_REQUESTS: Maximum requests per rate-limit window.
    RATE_LIMIT_WINDOW_SECONDS: Rate-limit window duration.
    JWT_EXPIRATION: JWT token validity duration.

Utilities

    classify_text(query, es): Classifies the given query using Elasticsearch.
    get_embedding(text): Generates a 768-dimensional embedding vector for the provided text.
    redis_client: Manages Redis operations for caching and rate-limiting.

Logging

    Logs are captured at different levels (INFO, WARNING, DEBUG, ERROR).
    Log entries include endpoint access, validation errors, cache hits/misses, rate-limit violations, and Elasticsearch errors.

Security

    Password Storage: Passwords are hashed securely using werkzeug.security.
    JWT Authentication: Tokens ensure endpoint protection.
    Rate Limiting: Prevents abuse using Redis.

Error Handling

The API provides descriptive error messages for all invalid inputs and server errors.