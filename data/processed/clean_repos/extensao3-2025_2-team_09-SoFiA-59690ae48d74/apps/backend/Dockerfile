FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install poetry
RUN poetry config virtualenvs.in-project true
COPY pyproject.toml poetry.lock ./
RUN ls -la .
RUN echo "======== pyproject.toml inside container ========"; cat pyproject.toml
RUN echo "======== poetry.lock inside container (first 40 lines) ========"; head -n 40 poetry.lock
RUN poetry install --no-root --no-interaction --no-ansi

FROM python:3.12-slim
WORKDIR /app
RUN useradd --create-home --shell /bin/bash appuser
COPY --from=builder /app/.venv ./.venv
COPY --chown=appuser:appuser ./src ./src
COPY --chown=appuser:appuser ./scripts ./scripts
RUN mkdir /app/data && chown appuser:appuser /app/data
ENV PATH="/app/.venv/bin:$PATH"
USER appuser
EXPOSE 8000
COPY --chown=appuser:appuser ./scripts ./scripts
COPY --chown=appuser:appuser entrypoint.sh .
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]