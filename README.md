# FastAPI Storage Server

This app exposes your PC's storage as a secure REST API using FastAPI.

## Features
- List files
- Upload files
- Download files
- Delete files
- Basic HTTP authentication

## Usage

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the server:
   ```sh
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
3. API endpoints:
   - `GET /files` — List files
   - `POST /upload` — Upload file (multipart/form-data)
   - `GET /download/{filename}` — Download file
   - `DELETE /delete/{filename}` — Delete file

## Configuration
- Change storage directory or credentials by setting environment variables:
  - `STORAGE_DIR` (default: ./storage)
  - `API_USERNAME` (default: admin)
  - `API_PASSWORD` (default: password)

## Security
- Uses HTTP Basic Auth. Change the default credentials before exposing to the internet.
- For production, use HTTPS (behind a reverse proxy or with uvicorn's SSL options).

# Updated 02/06/2026 06:30:38
