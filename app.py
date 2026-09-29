from datetime import datetime, date
from pathlib import Path
import json
import re

from flask import Flask, jsonify, request


# Create the Flask application
app = Flask(__name__)


# Store courses.json in the same directory as this app.py file
DATA_FILE = Path(__file__).parent / "courses.json"


# These are the only valid course statuses
VALID_STATUSES = {
    "Not Started",
    "In Progress",
    "Completed",
}


class DataFileError(Exception):
    """
    Custom exception used when courses.json cannot be read or written.
    """
    pass


def ensure_data_file():
    """
    Create courses.json automatically if it does not exist.

    The file stores courses as a JSON array:
    [
        {
            "id": 1,
            "name": "Learn Flask",
            ...
        }
    ]
    """
    try:
        if not DATA_FILE.exists():
            with DATA_FILE.open("w", encoding="utf-8") as file:
                json.dump([], file, indent=4)
    except OSError as error:
        raise DataFileError(
            f"Could not create data file: {error}"
        ) from error


def load_courses():
    """
    Read and return all courses from courses.json.

    Returns:
        list: A list of course dictionaries.
    """
    ensure_data_file()

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            courses = json.load(file)

        # Make sure the JSON file contains a list
        if not isinstance(courses, list):
            raise DataFileError(
                "courses.json must contain a JSON array."
            )

        return courses

    except json.JSONDecodeError as error:
        raise DataFileError(
            f"courses.json contains invalid JSON: {error}"
        ) from error

    except OSError as error:
        raise DataFileError(
            f"Could not read courses.json: {error}"
        ) from error


def save_courses(courses):
    """
    Save the provided list of courses to courses.json.
    """
    try:
        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(courses, file, indent=4)

    except OSError as error:
        raise DataFileError(
            f"Could not write to courses.json: {error}"
        ) from error


def get_next_course_id(courses):
    """
    Generate the next course ID.

    IDs start at 1. If there are no courses, the next ID is 1.
    Otherwise, the next ID is one greater than the highest existing ID.
    """
    if not courses:
        return 1

    highest_id = max(course["id"] for course in courses)
    return highest_id + 1


def validate_course_data(course_data, require_all_fields=True):
    """
    Validate course input from a request.

    Args:
        course_data: Dictionary received from the request body.
        require_all_fields: If True, all required fields must be present.

    Returns:
        A list of validation error messages.
    """
    errors = []

    required_fields = [
        "name",
        "description",
        "target_date",
        "status",
    ]

    # Check that all required fields exist
    if require_all_fields:
        for field in required_fields:
            if field not in course_data:
                errors.append(f"Missing required field: {field}")

    # Validate name
    if "name" in course_data:
        if not isinstance(course_data["name"], str):
            errors.append("name must be a string")
        elif not course_data["name"].strip():
            errors.append("name cannot be empty")

    # Validate description
    if "description" in course_data:
        if not isinstance(course_data["description"], str):
            errors.append("description must be a string")
        elif not course_data["description"].strip():
            errors.append("description cannot be empty")

    # Validate target_date
    if "target_date" in course_data:
        target_date = course_data["target_date"]

        if not isinstance(target_date, str):
            errors.append("target_date must be a string")
        elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}", target_date):
            errors.append(
                "target_date must use YYYY-MM-DD format"
            )
        else:
            try:
                # This catches invalid dates such as 2026-02-30
                date.fromisoformat(target_date)
            except ValueError:
                errors.append(
                    "target_date must be a valid calendar date"
                )

    # Validate status
    if "status" in course_data:
        status = course_data["status"]

        if status not in VALID_STATUSES:
            errors.append(
                "status must be one of: "
                "\"Not Started\", \"In Progress\", or \"Completed\""
            )

    return errors


def find_course(courses, course_id):
    """
    Find a course by its ID.

    Returns:
        The matching course, or None if it does not exist.
    """
    return next(
        (course for course in courses if course["id"] == course_id),
        None
    )


@app.errorhandler(404)
def handle_not_found(error):
    """
    Return JSON instead of Flask's default HTML 404 response.
    """
    return jsonify({
        "error": "The requested endpoint was not found"
    }), 404


@app.errorhandler(405)
def handle_method_not_allowed(error):
    """
    Return JSON when the wrong HTTP method is used.
    """
    return jsonify({
        "error": "HTTP method is not allowed for this endpoint"
    }), 405


@app.route("/api/courses", methods=["POST"])
def create_course():
    """
    Create a new course.

    POST /api/courses
    """
    course_data = request.get_json(silent=True)

    if course_data is None:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    if not isinstance(course_data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    validation_errors = validate_course_data(course_data)

    if validation_errors:
        return jsonify({
            "error": "Validation failed",
            "details": validation_errors
        }), 400

    try:
        courses = load_courses()

        new_course = {
            "id": get_next_course_id(courses),
            "name": course_data["name"].strip(),
            "description": course_data["description"].strip(),
            "target_date": course_data["target_date"],
            "status": course_data["status"],
            "created_at": datetime.now().astimezone().isoformat(),
        }

        courses.append(new_course)
        save_courses(courses)

        return jsonify(new_course), 201

    except DataFileError as error:
        return jsonify({
            "error": "File operation failed",
            "details": str(error)
        }), 500


@app.route("/api/courses", methods=["GET"])
def get_courses():
    """
    Get all courses.

    GET /api/courses
    """
    try:
        courses = load_courses()
        return jsonify(courses), 200

    except DataFileError as error:
        return jsonify({
            "error": "File operation failed",
            "details": str(error)
        }), 500


@app.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):
    """
    Get one course by ID.

    GET /api/courses/<course_id>
    Example: GET /api/courses/1
    """
    try:
        courses = load_courses()
        course = find_course(courses, course_id)

        if course is None:
            return jsonify({
                "error": f"Course with ID {course_id} was not found"
            }), 404

        return jsonify(course), 200

    except DataFileError as error:
        return jsonify({
            "error": "File operation failed",
            "details": str(error)
        }), 500


@app.route("/api/courses/<int:course_id>", methods=["PUT"])
def update_course(course_id):
    """
    Replace an existing course.

    PUT /api/courses/<course_id>
    Example: PUT /api/courses/1

    PUT requires all editable course fields:
    - name
    - description
    - target_date
    - status
    """
    course_data = request.get_json(silent=True)

    if course_data is None:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    if not isinstance(course_data, dict):
        return jsonify({
            "error": "Request body must be a JSON object"
        }), 400

    validation_errors = validate_course_data(course_data)

    if validation_errors:
        return jsonify({
            "error": "Validation failed",
            "details": validation_errors
        }), 400

    try:
        courses = load_courses()
        course = find_course(courses, course_id)

        if course is None:
            return jsonify({
                "error": f"Course with ID {course_id} was not found"
            }), 404

        # Update only editable fields.
        # The ID and created_at timestamp are preserved.
        course["name"] = course_data["name"].strip()
        course["description"] = course_data["description"].strip()
        course["target_date"] = course_data["target_date"]
        course["status"] = course_data["status"]

        save_courses(courses)

        return jsonify(course), 200

    except DataFileError as error:
        return jsonify({
            "error": "File operation failed",
            "details": str(error)
        }), 500


@app.route("/api/courses/<int:course_id>", methods=["DELETE"])
def delete_course(course_id):
    """
    Delete a course by ID.

    DELETE /api/courses/<course_id>
    Example: DELETE /api/courses/1
    """
    try:
        courses = load_courses()
        course = find_course(courses, course_id)

        if course is None:
            return jsonify({
                "error": f"Course with ID {course_id} was not found"
            }), 404

        courses.remove(course)
        save_courses(courses)

        return jsonify({
            "message": "Course deleted successfully",
            "course": course
        }), 200

    except DataFileError as error:
        return jsonify({
            "error": "File operation failed",
            "details": str(error)
        }), 500


if __name__ == "__main__":
    # Make sure courses.json exists before starting the server
    try:
        ensure_data_file()
        print(f"Using data file: {DATA_FILE}")
    except DataFileError as error:
        print(f"Startup error: {error}")

    # debug=True is useful while learning and developing.
    # Do not use debug mode in production.
    app.run(debug=True)