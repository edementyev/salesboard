from app import config


def admin_lambda():
    return lambda m: m.from_user.id in config.admins


def not_admin_lambda():
    return lambda m: m.from_user.id not in config.admins
