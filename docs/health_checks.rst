Health Checks
=============

Health checks may be used by the supervisor or process manager responsible of running the API. The
health check returns a 2xx status code if the application is in good shape, 500 otherwise.

Configure the process manager to check the status code returned by the ``/health/`` endpoint. This
is a good way to check if the api is ready to serve requests.
