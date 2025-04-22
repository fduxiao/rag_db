test:
    uv run -m unittest tests

lint:
    uv tool run ruff check ./rag_db

format:
    uv tool run ruff format
    uv tool run ruff check --select=FIX
