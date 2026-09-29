# CodeCraftHub

CodeCraftHub is a beginner friendly REST API built with Python and Flask. It lets developers track courses they want to learn. Course data is stored in a local JSON file, so no database is required.

## Features

- Create, view, update, and delete courses
- Generate numeric course IDs automatically
- Record a creation timestamp for every course
- Store data persistently in `courses.json`
- Create `courses.json` automatically when needed
- Validate required fields, dates, and course status values
- Return JSON responses with suitable HTTP status codes
- Handle invalid input, missing courses, and file errors

## Project structure

```text
codecrafthub/
├── app.py
├── courses.json
├── requirements.txt
└── README.md
```

- `app.py` contains the Flask application and all API routes.
- `courses.json` stores the course data. The application creates it automatically.
- `requirements.txt` lists the required Python packages.
- `README.md` contains the project documentation.

## Requirements

- Python 3.9 or newer
- `curl` for testing the API from a terminal

Check your Python version on macOS or Linux:

```bash
python3 --version
```

## Installation

Open the project directory in a terminal:

```bash
cd codecrafthub
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

The dependency file contains:

```text
Flask==3.0.0
Werkzeug==3.0.1
```

## Running the application

Make sure the virtual environment is active, then run:

```bash
python app.py
```

The API is available at:

```text
http://127.0.0.1:5000
```

Keep this terminal open while testing the API. Press `Control+C` to stop the server.

## Course data

Each course contains the following fields:

| Field | Description |
| --- | --- |
| `id` | Automatically generated numeric identifier |
| `name` | Required course name |
| `description` | Required course description |
| `target_date` | Required date in `YYYY-MM-DD` format |
| `status` | `Not Started`, `In Progress`, or `Completed` |
| `created_at` | Automatically generated creation timestamp |

Example:

```json
{
  "id": 1,
  "name": "Python Basics",
  "description": "Learn Python fundamentals",
  "target_date": "2027-12-31",
  "status": "Not Started",
  "created_at": "2026-09-29T09:53:13.300841+02:00"
}
```

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/courses` | Create a course |
| `GET` | `/api/courses` | Retrieve all courses |
| `GET` | `/api/courses/<course_id>` | Retrieve one course |
| `PUT` | `/api/courses/<course_id>` | Replace a course's editable fields |
| `DELETE` | `/api/courses/<course_id>` | Delete a course |

### Create a course

```bash
curl -i -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python Basics",
    "description": "Learn Python fundamentals",
    "target_date": "2027-12-31",
    "status": "Not Started"
  }'
```

A successful request returns `201 Created` and the new course.

### Retrieve all courses

```bash
curl -i http://127.0.0.1:5000/api/courses
```

### Retrieve a specific course

```bash
curl -i http://127.0.0.1:5000/api/courses/1
```

### Update a course

This application treats `PUT` as a complete replacement of the editable fields. Send `name`, `description`, `target_date`, and `status` together:

```bash
curl -i -X PUT http://127.0.0.1:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Python Basics",
    "description": "Learn Python fundamentals",
    "target_date": "2027-12-31",
    "status": "In Progress"
  }'
```

The existing `id` and `created_at` values remain unchanged.

### Delete a course

```bash
curl -i -X DELETE http://127.0.0.1:5000/api/courses/1
```

## Error handling

The API returns JSON error responses for common problems:

- `400 Bad Request` for missing fields, malformed JSON, invalid dates, or invalid status values
- `404 Not Found` when a course or endpoint does not exist
- `405 Method Not Allowed` when an endpoint receives an unsupported HTTP method
- `500 Internal Server Error` when `courses.json` cannot be read or written

Example request with a missing `description` field:

```bash
curl -i -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Incomplete Course",
    "target_date": "2027-12-31",
    "status": "Not Started"
  }'
```

Example response:

```json
{
  "error": "Validation failed",
  "details": [
    "Missing required field: description"
  ]
}
```

## Testing

Start the Flask application in one terminal. Open a second terminal for the `curl` commands above.

A useful CRUD test sequence is:

1. Create a course with `POST`.
2. Retrieve all courses with `GET`.
3. Retrieve the new course by ID.
4. Update it with `PUT`.
5. Delete it with `DELETE`.
6. Request the deleted ID again and confirm that the API returns `404 Not Found`.

The completed tests should also confirm that data changes are written to `courses.json`.

## Troubleshooting

### Flask cannot be imported

Activate the virtual environment and install the dependencies again:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Port 5000 is already in use

Stop the other Flask process with `Control+C`, then start the application again.

### The API returns a JSON validation error

Check that all required fields are present, the date uses `YYYY-MM-DD`, and the status is exactly `Not Started`, `In Progress`, or `Completed`.

### A course cannot be found

Use `GET /api/courses` to check the available numeric IDs.

### `courses.json` contains invalid JSON

Stop the server, repair the file so that it contains a valid JSON array, and restart the application. An empty data file should contain:

```json
[]
```

## Learning scope

CodeCraftHub is intended as a local learning project. It uses a JSON file instead of a database and does not include authentication or multi-user access. A production application would require a database, authentication, additional tests, and a production WSGI server.
