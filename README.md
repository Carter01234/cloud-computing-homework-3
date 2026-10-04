# Common Commands 

Activate venv first: `source venv/bin/activate`

Authenticating this with gcloud locally: `gcloud auth application-default login`

Calling the server handler locally with curl: 
```
curl -i http://localhost:8080/test.html
curl -i -X POST http://localhost:8080 -H "Content-Type: application/json" -d '{"filename": "test.html"}'
```


Calling the server handler remotely with curl:
```
curl -i https://us-central1-project-8aeecca0-4f70-4c6b-8e3.cloudfunctions.net/file-server/200.html

curl -i -X POST https://us-central1-project-8aeecca0-4f70-4c6b-8e3.cloudfunctions.net/file-server \
  -H "Content-Type: application/json" \
  -d '{"filename": "1164.html"}'
```


Running the server locally: `functions-framework --target=handle_request --debug`

You need to have the --debug flag or an existing bug with storage.Client() on MacOS will break everything at runtime.

Running the client for the local server: `./http-client -d localhost -p 8080 -b none -w none -i 9999 -n 5 -v`

Running the client for the cloud function: `./http-client -d file-server-3b5obgmrla-uc.a.run.app -b none -w none -s -i 9999 -n 100 -v`

Deploying the server to google cloud: 

```
gcloud functions deploy file-server \
  --gen2 \
  --runtime=python312 \
  --region=us-central1 \
  --source=. \
  --entry-point=handle_request \
  --trigger-http \
  --allow-unauthenticated \
  --service-account=homework3@project-8aeecca0-4f70-4c6b-8e3.iam.gserviceaccount.com
```
