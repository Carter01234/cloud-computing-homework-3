# One microservice will consist of a cloud function 
# that can accept HTTP GET and HTTP POST requests from web clients.  
# The service should be able to respond to requests for the files in your bucket 
# that you created in homework 2 and return the contents of the requested file 
# along with a 200-OK status. If the request is a GET then the file should be part of the path.  
# If the request is a POST then the file should be part of the POST payload. Run 
# this microservice as a separate special user that has permissions to access your bucket 
# and publish to your pub-sub channel (see below)