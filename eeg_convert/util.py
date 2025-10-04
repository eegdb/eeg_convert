import os

def detect_format(path):
    ext = os.path.splitext(path)[1].lower()
    return ext

def is_valid_enum_value(enum_class, value):
    return any(member.value == value for member in enum_class)