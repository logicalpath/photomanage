import os
from urllib.parse import quote

from datasette import hookimpl
from markupsafe import Markup, escape


@hookimpl
def render_cell(value, column, table, database, datasette):
    """Show the photo thumbnail in the id column of embeddings-vlm2.embeddings."""
    if database != "embeddings-vlm2" or table != "embeddings" or column != "id":
        return None
    if not isinstance(value, str) or not value.startswith("./"):
        return None

    thumb_url = datasette.urls.path("/-/media/thumb/" + quote(value[2:]))
    photo_url = datasette.urls.path("/photo/" + quote(os.path.basename(value)))
    return Markup(
        '<a href="{photo}"><img src="{thumb}" alt="{alt}" loading="lazy" '
        'style="display:block; max-width:150px; max-height:150px; '
        'width:auto; height:auto; object-fit:contain"></a>'
        "{label}"
    ).format(photo=photo_url, thumb=thumb_url, alt=value, label=escape(value))
