FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY packages/ packages/
COPY services/ services/
COPY simulation/ simulation/
RUN python -m pip install --no-cache-dir ./packages/schemas ./packages/fsm_engine .

CMD ["python", "simulation/timeline_emitter/run_replay.py"]
