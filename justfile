test:
    uv run -m unittest tests

lint:
    uv tool run ruff check ./rag_db

format:
    uv tool run ruff format
    uv tool run ruff check --select=FIX


dev:
    docker compose up -d
    sanic -p 8080 --dev rag_db:create_app

stop:
    docker compose down
