import os
from datasette import hookimpl


@hookimpl
def prepare_jinja2_environment(env):
    env.filters["file_exists"] = lambda path: path and os.path.exists(path)
