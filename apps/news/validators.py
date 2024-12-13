from django.core.exceptions import ValidationError


def validate_tg_id(value):
    if not str(value).startswith("-100"):
        raise ValidationError("ID канала должен начинаться с '-100'")
    return value
