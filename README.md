This app shows a list of movies on localhost:8000/movies/ from the Ghibli API.
For each movie, it lists the people that are in it.

Features:
 * Succesful calls to the Ghibli API are cached for 1 minute.
 * Returns HTTP 500 when unable to connect to the Ghibli API.
 * Requests to the Ghibli API time out after 10 seconds.
 * Extensive testsuite.

Limitations:
 * Not threadsafe.
 * Request exceptions are not cached. So if the Ghibli API is down, we keep
   hitting it when the user refreshes (maybe this is a feature?).
 * Doesn't use the 'limit' parameter of the Ghibli API, because the API doesn't
   seem to support pagination anyway.

Run the server:
```
FLASK_DEBUG=1 FLASK_RUN_PORT=8000 flask run
```

Testing:
```
pytest test.py -s
```


Development:
Run `black8` for pep8-compliance (with default settings, so 88 max line length).
