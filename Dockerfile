FROM python:3.11-slim

WORKDIR /leaderboardx-root

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY codebase ./codebase

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "codebase.main:fast_app", "--host", "0.0.0.0", "--port", "8000"]
