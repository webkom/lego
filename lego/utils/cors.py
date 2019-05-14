import re


def generate_cors_origin_regex_list(domains):
    regex_list = []
    for domain in domains:
        regex_list.append(r"^(https?://)?(.*\.)?{0}$".format(re.escape(domain)))
    return regex_list
