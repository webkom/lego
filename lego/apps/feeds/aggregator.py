class FeedAggregator:
    """
    This feed aggregator groups events by target, verb and date by default. Verbs can have a
    custom aggregation_group variable for custom grouping.
    """

    def default_group_aggregate(self, activity):
        verb = activity.verb.id
        target_id = activity.target_id
        target_content_type = activity.target_content_type
        date = activity.time.date()
        group = '%s-%s-%s-%s' % (verb, target_id, target_content_type, date)
        return group

    def get_group(self, activity):
        verb_group = getattr(activity.verb, 'aggregation_group', None)
        if not verb_group:
            return self.default_group_aggregate(activity)

        options = {
            'verb': activity.verb.id,
            'target_id': activity.target_id,
            'target_content_type': activity.target_content_type,
            'object_id': activity.object_id,
            'object_content_type': activity.object_content_type,
            'actor_id': activity.actor_id,
            'actor_content_type': activity.actor_content_type,
            'date': activity.time.date(),
            'time': activity.time
        }
        return verb_group.format(**options)
