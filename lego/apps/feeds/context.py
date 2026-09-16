def collect_refs(obj):
    """
    Given one aggregated feed object, return the set of actor/object/target
    strings referenced by its activities.
    """
    refs = set()
    for activity in obj.activities:
        for attr in ("actor", "object", "target"):
            ref = getattr(activity, attr, None)
            if ref:
                refs.add(ref)
    return refs


def resolve_context(obj, lookup):
    refs = collect_refs(obj)
    return {ref: lookup[ref] for ref in refs if ref in lookup}
