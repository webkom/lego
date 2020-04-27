import requests
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable


class HealthCheckArticlesBackend(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self):
        response = requests.get("http://localhost:8000/api/v1/articles/")
        if response.status_code != 200:
            raise ServiceUnavailable("Articles did not return 200")

    def identifier(self):
        return self.__class__.__name__


class HealthCheckEventsBackend(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self):
        response = requests.get("http://localhost:8000/api/v1/events/")
        if response.status_code != 200:
            raise ServiceUnavailable("Events did not return 200")

    def identifier(self):
        return self.__class__.__name__


class HealthCheckGroupsBackend(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self):
        response = requests.get("http://localhost:8000/api/v1/groups/")
        if response.status_code != 401:
            raise ServiceUnavailable("Groups did not return 401")

    def identifier(self):
        return self.__class__.__name__


class HealthCheckPagesBackend(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self):
        response = requests.get("http://localhost:8000/api/v1/pages/")
        if response.status_code != 200:
            raise ServiceUnavailable("Pages did not return 200")

    def identifier(self):
        return self.__class__.__name__


class HealthCheckUsersBackend(BaseHealthCheckBackend):
    critical_service = True

    def check_status(self):
        response = requests.get("http://localhost:8000/api/v1/users/")
        if response.status_code != 401:
            raise ServiceUnavailable("Users did not return 401")

    def identifier(self):
        return self.__class__.__name__
