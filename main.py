import mimetypes
import functions_framework
import json
from functools import cache
from flask import Request
from flask.typing import ResponseReturnValue
from google.cloud import storage
from google.api_core.exceptions import NotFound
from google.cloud import pubsub_v1

BUCKET_NAME = "html-files-for-class"
PREFIX = "pages"
FORBIDDEN_COUNTRIES = {
    "north korea",
    "iran",
    "cuba",
    "myanmar",
    "iraq",
    "libya",
    "sudan",
    "zimbabwe",
    "syria",
}
PROJECT_ID = "project-8aeecca0-4f70-4c6b-8e3"
TOPIC_ID = "forbidden-requests"


storage_client = storage.Client()
pubsub_client = pubsub_v1.PublisherClient()


# Publish a message indicating someone has tried to reach
# this service from a forbidden country.
def publish_forbidden_request(country: str | None, filename: str, client_ip: str | None):
    topic_path = pubsub_client.topic_path(PROJECT_ID, TOPIC_ID)

    # Messages must be bytes, which is why the dict is converted to JSON and then encoded
    message = json.dumps({
        "country": country,
        "filename": filename,
        "client_ip": client_ip,
    }).encode("utf-8")

    future = pubsub_client.publish(topic_path, message)
    # wait until Pub/Sub confirms it received the message
    future.result(timeout=10)



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


def is_forbidden_country(country: str | None) -> bool:
    return country is not None and country.strip().lower() in FORBIDDEN_COUNTRIES
    
# This decorator marks handle_request as a Flask HTTP handler. The request param is a
# Flask Request object, and the return value is wrapped in a Flask Response object.
#
# GET  /<filename>.html                   -> returns the file
# POST {"filename": "<filename>.html"}    -> returns the file
@functions_framework.http
def handle_request(request: Request) -> ResponseReturnValue:    
    match request.method:
        case "GET":
            filename = request.path.lstrip("/")
            country = request.headers.get("X-country")

            if is_forbidden_country(country):
                publish_forbidden_request(country, filename, request.headers.get("X-client-IP"))

                print(json.dumps({
                    "message": f"Permission denied: request for {filename} from forbidden country {country}",
                    "status": 400,
                    "country": "country",
                    "filename": "filename",
                }))
                return (f"Permission denied: requests from {country} are not allowed\n", 400)



            contents = get_file_from_bucket(filename)

            if contents is None: 
                return (f"File not found: {filename}\n", 404)
            else: 
                content_type = mimetypes.guess_type(filename)[0] or "text/plain"
                return (contents, 200, {"Content-Type": content_type})
        case "POST":
            data = request.get_json()
            filename = data.get("filename")
            country = request.headers.get("X-country")

            if is_forbidden_country(country):
                publish_forbidden_request(country, filename, request.headers.get("X-client-IP"))
                
                print(json.dumps({
                    "message": f"Permission denied: request for {filename} from forbidden country {country}",
                    "status": 400,
                    "country": "country",
                    "filename": "filename",
                }))
                return (f"Permission denied: requests from {country} are not allowed\n", 400)



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