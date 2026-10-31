"""Default avatar: the usual grey person silhouette, the same for everyone without an uploaded photo."""

SILHOUETTE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">'
    '<rect width="100" height="100" fill="#E3E6EB"/>'
    '<circle cx="50" cy="39" r="17" fill="#A8AFBA"/>'
    '<path d="M17 100C17 75 32 63 50 63C68 63 83 75 83 100Z" fill="#A8AFBA"/>'
    '</svg>'
)


def default_avatar_svg(name=None):
    return SILHOUETTE_SVG
