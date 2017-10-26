import bleach


def sanitize_html(value, allow_images=True):
    """
    Remove dangerous tags from HTML.
    """
    tags = [
            'p', 'b', 'i', 'u', 'h1', 'h2', 'code', 'pre', 'blockquote', 'strong', 'strike',
            'ul', 'cite', 'li', 'em', 'hr', 'div', 'a'
    ]
    if allow_images:
        tags.append('img')

    safe_content = bleach.clean(
        value,
        tags=tags,
        attributes={
            'a': ['href'],
            'img': ['data-file-key'],
        },
        strip=True,
        strip_comments=True
    )
    return safe_content
