FROM python:3.11

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-cache --dev --no-install-project

COPY . .

RUN uv sync --frozen --no-cache --dev

ENV PATH="/app/.venv/bin:$PATH"
RUN echo 'alias masksql="python3 /app/main.py"' >> ~/.bashrc

CMD ["tail", "-f", "/dev/null"]
