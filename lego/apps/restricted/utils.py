def split_address(address):
    """
    Split an email address into a local-part and domain.
    """
    local_part, at, domain = address.partition('@')
    if len(at) == 0:
        return local_part, None
    return local_part, domain
