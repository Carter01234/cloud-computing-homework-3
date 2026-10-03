import mimetypes
import os
import functions_framework

from flask import Request
from flask.typing import ResponseReturnValue
from google.cloud import storage
from google.api_core.exceptions import NotFound

BUCKET_NAME = "html-files-for-class"
storage_client = storage.Client()






# This decorator marks the handle_request function as a flask http handler
# The Request param is a flask request object and it will wrap the return values in a 
# flask response object
@functions_framework.http
def handle_request(request: Request) -> ResponseReturnValue:
    match request.method:
        case "GET":
            print("GET path:", request.path)
            print("Headers:", dict(request.headers))
            return (f"You asked for {request.path}\n", 200)
        case "POST":
            print("POST content-type:", request.content_type)
            print("POST body:", request.get_data(as_text=True))
            return ("Got your POST\n", 200)
        case _:
            return ("Method not allowed", 405, {"Allow": "GET, POST"})