# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.12-slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

ENV PYTHONPATH=/app

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
RUN adduser -u 2755 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# Expose the correct port and set Uvicorn to listen on all interfaces
EXPOSE 80
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]