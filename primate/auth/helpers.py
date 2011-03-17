import datetime
from django.contrib.auth.signals import user_logged_in
from django.contrib import auth
from django.utils.crypto import constant_time_compare
from django.utils.encoding import smart_str
from django.utils.hashcompat import md5_constructor, sha_constructor


__all__ = ('SiteUserNotAvailable', 'get_hexdigest', 'check_password',
           'update_last_login', '_user_get_all_permissions', '_user_has_perm',
           '_user_has_module_perms')


class SiteUserNotAvailable(Exception):
    pass


def get_hexdigest(algorithm, salt, raw_password):
    """
    Returns a string of the hexdigest of the given plaintext password and salt
    using the given algorithm ('md5', 'sha1' or 'crypt').
    """
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == 'crypt':
        try:
            import crypt
        except ImportError:
            raise ValueError('"crypt" password algorithm not supported in this '
                             'environment')
        return crypt.crypt(raw_password, salt)

    if algorithm == 'md5':
        return md5_constructor(salt + raw_password).hexdigest()
    elif algorithm == 'sha1':
        return sha_constructor(salt + raw_password).hexdigest()
    raise ValueError("Got unknown password algorithm type in password.")


def check_password(raw_password, enc_password):
    """
    Returns a boolean of whether the raw_password was correct. Handles
    encryption formats behind the scenes.
    """
    algo, salt, hsh = enc_password.split('$')
    return constant_time_compare(hsh, get_hexdigest(algo, salt, raw_password))


def update_last_login(sender, user, **kwargs):
    """
    A signal receiver which updates the last_login date for
    the user logging in.
    """
    user.last_login = datetime.datetime.now()
    user.save()
user_logged_in.connect(update_last_login)


# A few helper functions for common logic between User and AnonymousUser.
def _user_get_all_permissions(user, obj):
    permissions = set()
    anon = user.is_anonymous()
    for backend in auth.get_backends():
        if not anon or backend.supports_anonymous_user:
            if hasattr(backend, "get_all_permissions"):
                if obj is not None:
                    if backend.supports_object_permissions:
                        permissions.update(
                            backend.get_all_permissions(user, obj)
                        )
                else:
                    permissions.update(backend.get_all_permissions(user))
    return permissions


def _user_has_perm(user, perm, obj):
    anon = user.is_anonymous()
    active = user.is_active
    for backend in auth.get_backends():
        if (not active and not anon and backend.supports_inactive_user) or \
                    (not anon or backend.supports_anonymous_user):
            if hasattr(backend, "has_perm"):
                if obj is not None:
                    if (backend.supports_object_permissions and
                        backend.has_perm(user, perm, obj)):
                        return True
                else:
                    if backend.has_perm(user, perm):
                        return True
    return False


def _user_has_module_perms(user, app_label):
    anon = user.is_anonymous()
    active = user.is_active
    for backend in auth.get_backends():
        if (not active and not anon and backend.supports_inactive_user) or \
                    (not anon or backend.supports_anonymous_user):
            if hasattr(backend, "has_module_perms"):
                if backend.has_module_perms(user, app_label):
                    return True
    return False

