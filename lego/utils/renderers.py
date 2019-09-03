from djangorestframework_camel_case.render import CamelCaseJSONRenderer


class JSONRenderer(CamelCaseJSONRenderer):
    """
    Return a empty object instead of an empty bytestring. This makes sure the app doesn't crash
    on DELETE requests.
    """

    def render(self, data, *args, **kwargs):
        if data is None and len(args) > 1 and args[1]["response"].status_code != 204:
            return bytes("{}".encode("utf-8"))

        return super().render(data, *args, **kwargs)
