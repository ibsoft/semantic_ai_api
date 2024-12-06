# Install Semantic API docker container

docker build --no-cache --network=host -t semantic_categories_api .

docker run -p 8001:8001  --network=host -e OPENAI_API_KEY="your_key_here" semantic_categories_api

