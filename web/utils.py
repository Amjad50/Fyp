from functools import wraps
from io import BytesIO
from typing import List, Tuple, Optional, Any

from PIL import Image
from flask import request, abort, send_file


def json_arguments(required_args: List[Tuple[str, type]], optional_args: Optional[List[Tuple[str, type, Any]]] = None):
    def decorator(func):
        @wraps(func)
        def wrapper():
            json_data = request.get_json()

            if json_data is None:
                abort(400, "Must specify `json` data body")

            for (name, ty) in required_args:
                # for required args, make sure the arg is present and is of the required type
                if name not in json_data:
                    abort(400, f"argument `{name}` is not found")
                if not isinstance(json_data[name], ty):
                    abort(400, f"argument `{name}` must be of type `{ty.__name__}`")

            if optional_args is not None:
                # for optional args, if it exist, the type must be the same as specified
                # if it does not exist, then use the default value, and make sure the default
                # value is of the correct type
                for (name, ty, default) in optional_args:
                    if name in json_data:
                        if not isinstance(json_data[name], ty):
                            abort(400, f"argument `{name}` must be of type `{ty.__name__}`")
                    else:
                        assert isinstance(default, ty), \
                            f"Cannot use default value {default} of as it is not of type {ty}"
                        json_data[name] = default

            return func(json_data)

        return wrapper

    return decorator


def response_image(img: Image):
    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')
