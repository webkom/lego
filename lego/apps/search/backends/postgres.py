from .. import registry


from lego.apps.search.backend import SearchBacked


class PostgresBackend(SearchBacked):

    name = "postgres"

    max_results = 10

    def update_many(self, tuple_list):
        pass  # NOOP, we use the native data source

    def remove_many(self, tuple_list):
        pass  # NOOP, we use the native data source

    def clear(self):
        pass  # NOOP, we use the native data source

    def search(self, query, content_types=None, filters=None):
        return self.autocomplete(query, content_types)

    def autocomplete(self, query, content_types=None):
        if content_types is None or len(content_types) == 0:
            content_types = registry.index_registry.keys()

        max_results_per_type = self.max_results
        results_by_content_type = {content_type: [] for content_type in content_types}
        for content_type in content_types:
            search_index = self.get_search_index(content_type)
            db_results = search_index.autocomplete(query)[:max_results_per_type]
            results_by_content_type[content_type] = list(db_results)

        # Interleave results so results are not only of one type if there are many matches
        results = []
        for i in range(max_results_per_type):
            for content_type in content_types:
                if len(results_by_content_type[content_type]):
                    results.append(results_by_content_type[content_type].pop(0))

        return results

    def serialize_object(self, object, search_type):
        from lego.utils.content_types import instance_to_content_type_string
        content_type = instance_to_content_type_string(object)
        search_index = self.get_search_index(content_type)
        serializer = search_index.get_serializer(object)
        fields = search_index.get_autocomplete_result_fields() \
            if search_type == 'autocomplete' \
            else search_index.get_result_fields()
        result = {field: serializer.data[field] for field in fields}
        result.update(
            {
                "id": object.pk,
                "content_type": content_type,
                "text": "text",
            }
        )
        return result

    def serialize(self, objects, search_type='autocomplete'):
        return list(map(lambda o: self.serialize_object(o, search_type), objects[:self.max_results]))

    def get_django_object(self, el):
        return el
