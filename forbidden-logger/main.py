import base64
import json
from datetime import datetime, timezone
from functools import cache
 
import functions_framework
from cloudevents.http import CloudEvent
from google.api_core.exceptions import NotFound, PreconditionFailed
from google.cloud import storage
 
BUCKET_NAME = "html-files-for-class"
PREFIX="forbidden-logs"
LOG_OBJECT = "forbidden_requests.txt"


storageClient = storage.Client()
 


# Pull the published JSON payload and publish time out of a Pub/Sub CloudEvent.
# The event looks like:
#   {
#    "message": 
#       {
#        "data": "<encodedbytes>",
#        "messageId": "<message>", 
#        "publishTime": "<time>"
#       }, 
#    "subscription": "..."
#   }
def decode_message(cloud_event: CloudEvent) -> tuple[dict, str]:
    message = cloud_event.data["message"]
    stringData = base64.b64decode(message.get("data", "")).decode("utf-8")
    payload = json.loads(stringData)
    published_at = message.get("publishTime") or datetime.now(timezone.utc).isoformat()
    return payload, published_at
 


# Append one line to the log file in GCS.
# GCS objects can't be modified in place, so "append" means: read the current file,
# add the line, and write the whole thing back.
def append_line(line: str) -> None:
    blob = storageClient.bucket(BUCKET_NAME).blob(f'{PREFIX}/{LOG_OBJECT}')
    existing = blob.download_as_text()
    blob.upload_from_string(
        existing + line + "\n",
        content_type="text/plain"
    )
 
 
# Triggered by every message published to the forbidden-requests Pub/Sub topic.
@functions_framework.cloud_event
def handle_forbidden_request(cloud_event: CloudEvent) -> None:
    payload, published_at = decode_message(cloud_event)
 
    country = payload.get("country", "unknown country")
    filename = payload.get("filename", "unknown file")
    client_ip = payload.get("client_ip", "unknown IP")
 
    error_message = (
        f"[{published_at}] ERROR: Forbidden request from {country} "
        f"(client IP {client_ip}) for file {filename}. "
        f"Export of this material to {country} is prohibited."
    )
 
    # 1. Print to standard output (shows up in Cloud Logging).
    print(error_message)
 
    # 2. Append to the log file in its own directory in the bucket.
    append_line(error_message)