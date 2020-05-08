import requests
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable


class HealthCheckArticlesBackend(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self):
        response = requests.get("http://localhost:8000/api/v1/articles/")

        # Check that the HTTP code was 200
        if response.status_code != 200:
            raise ServiceUnavailable("Articles did not return 200")

        # Check that the endpoint returns some results
        if len(response.json()["results"]) == 0:
            raise ServiceUnavailable("Articles did not return any articles")

    def identifier(self):
        return self.__class__.__name__


class HealthCheckEventsBackend(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self):
        response = requests.get("http://localhost:8000/api/v1/events/")

        # Check that the HTTP code was 200
        if response.status_code != 200:
            raise ServiceUnavailable("Events did not return 200")

        # Check that the endpoint returns some results
        if len(response.json()["results"]) == 0:
            raise ServiceUnavailable("Events did not return any events")

    def identifier(self):
        return self.__class__.__name__


class HealthCheckJoblistingsBackend(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self):
        response = requests.get("http://localhost:8000/api/v1/joblistings/")

        # Check that the HTTP code was 200
        if response.status_code != 200:
            raise ServiceUnavailable("Joblistings did not return 200")

        # Check that the endpoint returns some results
        if len(response.json()["results"]) == 0:
            raise ServiceUnavailable("Joblistings did not return any jobs")

    def identifier(self):
        return self.__class__.__name__


class HealthCheckPagesBackend(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self):
        response = requests.get("http://localhost:8000/api/v1/pages/")

        # Check that the HTTP code was 200
        if response.status_code != 200:
            raise ServiceUnavailable("Pages did not return 200")

        # Check that the endpoint returns some results
        if len(response.json()["results"]) == 0:
            raise ServiceUnavailable("Pages did not return any pages")

    def identifier(self):
        return self.__class__.__name__


class HealthCheckSiteMetaBackend(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self):
        response = requests.get("http://localhost:8000/api/v1/site-meta/")

        # Check that the HTTP code was 200
        if response.status_code != 200:
            raise ServiceUnavailable("Site-Meta did not return 200")

        if len(response.json()["site"]) == 0:
            raise ServiceUnavailable("Site-Meta did not return any meta")

        if len(response.json()["isAllowed"]) == 0:
            raise ServiceUnavailable("Site-Meta did not return any permissions")

    def identifier(self):
        return self.__class__.__name__
