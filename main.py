import mimetypes
import functions_framework
import json
from functools import cache
from flask import Request
from flask.typing import ResponseReturnValue
from google.cloud import storage
from google.api_core.exceptions import NotFound

BUCKET_NAME = "html-files-for-class"
PREFIX = "pages"

storage_client = storage.Client()

def get_file_from_bucket(filename: str) -> None | bytes: 
    blob = storage_client.bucket(BUCKET_NAME).blob(f'{PREFIX}/{filename}')
    try:
        return blob.download_as_bytes()
    except NotFound:
        print(f"The filename {filename} does not exist in GCS")

        # 2. Structured log: a single line of JSON on stdout. Cloud Logging parses it,
        #    uses "severity" as the log level, "message" as the summary, and keeps the
        #    other fields as searchable jsonPayload fields.
        print(json.dumps({
            "severity": "WARNING",
            "message": f"The filename {filename} does not exist in GCS",
            "status": 404,
            "filename": filename,
        }))

        return None
    
# This decorator marks the handle_request function as a flask http handler
# The Request param is a flask request object and it will wrap the return values in a 
# flask response object
# 
# API Expects a request path of "/<filename>.html" 
# and returns the contents of the file
@functions_framework.http
def handle_request(request: Request) -> ResponseReturnValue:
    match request.method:
        case "GET":
            filename = request.path.lstrip("/")
            contents = get_file_from_bucket(filename)

            if contents is None: 
                return (f"File not found: {filename}\n", 404)
            else: 
                content_type = mimetypes.guess_type(filename)[0] or "text/plain"
                return (contents, 200, {"Content-Type": content_type})
        case "POST":
            data = request.get_json()
            filename = data.get("filename")
            contents = get_file_from_bucket(filename)
            if contents is None: 
                return (f"File not found: {filename}\n", 404)
            else: 
                content_type = mimetypes.guess_type(filename)[0] or "text/plain"
                return (contents, 200, {"Content-Type": content_type})
            
        case _:
            print(json.dumps({
                "severity": "ERROR",
                "message": f"This service does not support messages other than GET or POST",
                "status": 501,
            }))
            return ("Method not allowed", 501, {"Allow": "GET, POST"})