import json
import logging
import time
from elasticsearch import Elasticsearch
from flask import Blueprint, Response, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from .models import db, User
from .utils import classify_text, get_embedding
from . import redis_client
from datetime import timedelta
from .config import Config
import logging
from flask import request

logger = logging.getLogger()

es = Elasticsearch(Config.ELASTICSEARCH_URL)

api_bp = Blueprint('api', __name__)

@api_bp.route('/register', methods=['POST'])
@jwt_required()
def register_user():
    logging.info("Register endpoint accessed")
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        logging.warning("Missing username or password in registration request")
        return jsonify({"msg": "Missing username or password"}), 400

    # Check if the user already exists
    user = User.query.filter_by(username=username).first()
    if user:
        logging.warning(f"User registration failed: User '{username}' already exists")
        return jsonify({"msg": "User already exists"}), 400

    new_user = User(username=username)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    logging.info(f"User '{username}' registered successfully")
    return jsonify({"msg": "User registered successfully"}), 201

@api_bp.route('/login', methods=['POST'])
def login_user():
    logging.info("Login endpoint accessed")
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        logging.warning(f"Invalid login attempt for username '{username}'")
        return jsonify({"msg": "Invalid credentials"}), 401

    # Generate JWT token
    access_token = create_access_token(identity=username, expires_delta=timedelta(seconds=Config.JWT_EXPIRATION))
    logging.info(f"User '{username}' logged in successfully")
    return jsonify(access_token=access_token)

@api_bp.route('/classify', methods=['POST'])
@jwt_required()
def get_ai_response():
    """Classify a user query with caching and rate limiting."""
    logging.info("Classify endpoint accessed")
    user_identity = get_jwt_identity()
    rate_limit_key = f"rate_limit:{user_identity}"
    logging.debug(f"Rate limiting key: {rate_limit_key}")

    start_time = time.time()  # Start tracking response time

    # Get current count of requests made in the rate-limit window
    current_count = redis_client.get(rate_limit_key) if Config.USE_REDIS else None
    if current_count:
        logging.debug(f"Current request count for user '{user_identity}': {current_count.decode()}")

    # Check rate limit
    if Config.USE_REDIS and current_count and int(current_count) >= Config.RATE_LIMIT_MAX_REQUESTS:
        logging.warning(f"Rate limit exceeded for user '{user_identity}'")
        return jsonify({"msg": "Rate limit exceeded, try again later."}), 429

    # Retrieve the user query
    data = request.get_json()
    title = data.get("title")
    message = data.get("message")

    if not title or not message:
        logging.warning("Classify request missing 'title' or 'message' parameter")
        return jsonify({"msg": "Title and message are required"}), 400

    # Combine title and message to form the query
    query = f"{title} {message}"

    # Check Redis cache for a stored result
    if Config.USE_REDIS:
        cached_result = redis_client.get(query)
        if cached_result:
            elapsed_time = round(time.time() - start_time, 2)
            logging.info(f"Cache hit for query: '{query}'")
            decoded_result = json.loads(cached_result)
            return jsonify({
                "response": decoded_result,
                "cached": "true",
                "time": elapsed_time
            })

    # If not cached, query Elasticsearch and classify
    try:
        logging.info(f"Cache miss for query: '{query}', querying Elasticsearch")
        ai_response, _ = classify_text(query, es)
    except Exception as e:
        logging.error(f"Error during Elasticsearch query: {str(e)}")
        return jsonify({"msg": f"Error getting AI response: {str(e)}"}), 500

    elapsed_time = round(time.time() - start_time, 2)

    # Cache the response in Redis and increment rate limit count
    if Config.USE_REDIS:
        # Increment rate limit count or set it if not present
        if current_count:
            redis_client.incr(rate_limit_key)
            logging.debug(f"Incremented rate limit count for user '{user_identity}'")
        else:
            redis_client.setex(rate_limit_key, Config.RATE_LIMIT_WINDOW_SECONDS, 1)
            logging.debug(f"Rate limit key set for user '{user_identity}' with a window of {Config.RATE_LIMIT_WINDOW_SECONDS} seconds")

        # Convert sets to lists before serializing
        if isinstance(ai_response, set):
            ai_response = list(ai_response)
        
        logging.debug(f"ai_response type: {type(ai_response)}, content: {ai_response}")
        
        # Cache the AI response
        redis_client.setex(query, Config.REDIS_CACHE_EXPIRATION, json.dumps(ai_response, ensure_ascii=False))

        logging.info(f"Cached response for query: '{query}' with expiration {Config.REDIS_CACHE_EXPIRATION} seconds")

    # Return the AI response
    response = {
        "response": ai_response,
        "cached": "false",
        "time": elapsed_time
    }
    logging.info(f"Returning AI response completed!")
    return Response(json.dumps(response, ensure_ascii=False), mimetype='application/json; charset=utf-8')


@api_bp.route('/memory', methods=['POST'])
@jwt_required()
def store_memory():
    """Store a new document with category, subcategory, description, and title."""
    logging.info("Memory endpoint accessed")

    # Get current user identity
    user_identity = get_jwt_identity()

    # Get the data from the request
    data = request.get_json()
    title = data.get("Title")
    category = data.get("Category")
    sub_category = data.get("Subcategory")
    sub_sub_category = data.get("Subsubcategory")
    description = data.get("Description")

    if not title or not category or not sub_category or not sub_sub_category or not description:
        logging.warning("Missing title, category, subcategory, subsubcategory or description in memory request")
        return jsonify({"msg": "Title, Category, Subcategory, subsubcategory and Description are required"}), 400

    # Generate embedding for the title + description combined
    combined_text = title + " " + description
    embedding = get_embedding(combined_text)
    if not embedding or len(embedding) != 768:
        logging.error("Failed to generate valid embedding for the title and description")
        return jsonify({"msg": "Error generating embedding for the title and description"}), 500

    # Index document in Elasticsearch
    document = {
        "Title": title,
        "Description": description,
        "Category": category,
        "Sub-Category": sub_category,
        "Sub-sub-Category":sub_sub_category,
        "embedding": embedding
    }

    try:
        es.index(index="categories_index", document=document)
        logging.info("Document indexed successfully")
        return jsonify({"msg": "Document stored successfully"}), 201
    except Exception as e:
        logging.error(f"Error indexing document: {str(e)}")
        return jsonify({"msg": f"Error storing document: {str(e)}"}), 500

