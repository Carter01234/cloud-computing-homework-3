# Common Commands 

Authenticating this with gcloud locally: `gcloud auth application-default login`

Calling the server handler with curl: 
```
curl -i http://localhost:8080/test.html
curl -i -X POST http://localhost:8080 -H "Content-Type: application/json" -d '{"filename": "test.html"}'
```

Running the server locally: `functions-framework --target=handle_request --debug`

You need to have the --debug flag or an existing bug with storage.Client() on MacOS will break everything at runtime.

Running the client which exists in a different directory: `./http-client -d localhost -p 8080 -b none -w none -n 5 -v`
