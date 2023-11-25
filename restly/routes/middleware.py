from functools import wraps
from flask import request, abort
from ..models import User


def user_authenticated(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            abort(401, description="No token provided")

        if token.startswith('Bearer '):
            token = token[7:]

        user = User.query.filter_by(token=token).first()

        if not user:
            abort(401, description="Invalid token")

        return f(user, *args, **kwargs)

    return decorated_function
