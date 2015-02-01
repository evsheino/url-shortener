# URL shortening service

POST /shorten
Parameters: Parameter link should contain the link to shorten. Accepted protocols are http, https, ftp and ftps.
Returns: Id for the shortened link in text/plain format.

GET /{id}
Returns: 301 redirects the user agent to a previously stored URL. 404 error if no link stored with given id.

Service available at https://radiant-castle-9848.herokuapp.com/
