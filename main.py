import mimetypes
import functions_framework

from flask import Request
from flask.typing import ResponseReturnValue
from google.cloud import storage
from google.api_core.exceptions import NotFound

BUCKET_NAME = "html-files-for-class"
PREFIX = "pages"
storage_client = storage.Client()

def get_file_from_bucket(filename: str) -> bytes: 
    blob = storage_client.bucket(BUCKET_NAME).blob(f'{PREFIX}/{filename}')
    return blob.download_as_bytes()
    

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
            content_type = mimetypes.guess_type(filename)[0] or "text/plain"
            return (contents, 200, {"Content-Type": content_type})
        case "POST":
            data = request.get_json()
            filename = data.get("filename")
            contents = get_file_from_bucket(filename)
            content_type = mimetypes.guess_type(filename)[0] or "text/plain"
            return (contents, 200, {"Content-Type": content_type})
            
        case _:
            return ("Method not allowed", 405, {"Allow": "GET, POST"})