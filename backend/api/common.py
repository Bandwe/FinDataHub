# -*- coding: utf-8 -*-
"""Shared request validation for JSON APIs."""
from flask import request
from werkzeug.exceptions import BadRequest, UnsupportedMediaType

from services.industry_templates import ServiceError


def json_object():
    """Return a JSON object or raise a user-facing validation error."""
    try:
        payload = request.get_json()
    except UnsupportedMediaType as exc:
        raise ServiceError('请求Content-Type必须为application/json', 415) from exc
    except BadRequest as exc:
        raise ServiceError('请求JSON格式不正确') from exc

    if payload is None:
        return {}
    if not isinstance(payload, dict):
        raise ServiceError('请求体必须是JSON对象')
    return payload
