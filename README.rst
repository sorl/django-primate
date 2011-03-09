django-primate
==============

- A modular django user.

I am not going to discuss if this is a good idea or not. This Django
application monkey patches django in order to have a custom User model that
plugs into the ``django.contrib.auth`` application.


Installation
------------
First of all install the module by checking out the latest code or use pip::

    pip install django-primate

In order to monkey patch we need to do this early. I have created a small
modified ``manage.py`` file that you can use for your development. This sets up
your environment and right before you run your management command (such as
`runserver``) we apply the patch. Copy this into your project and overwrite the
default ``manage.py``::

    #!/usr/bin/env python
    from django.core.management import setup_environ, ManagementUtility
    import imp
    try:
        imp.find_module('settings') # Assumed to be in the same directory.
    except ImportError:
        import sys
        sys.stderr.write(
            "Error: Can't find the file 'settings.py' in the directory "
            "containing %r. It appears you've customized things.\nYou'll have to "
            "run django-admin.py, passing it your settings module.\n" % __file__
            )
        sys.exit(1)

    import settings

    if __name__ == "__main__":
        setup_environ(settings)
        import primate
        primate.patch()
        ManagementUtility().execute()

To monkey patch your deployment you would apply the patch right after setting up
the ``DJANGO_SETTINGS_MODULE``.


Now add ``django.contrib.auth`` to your ``INSTALLED_APPS``


Using
-----
After installing this patch you effectively have no User model at all. You have
to create one on your own and define it in your settings. I will give you an
example on how to do this.

``project/users/models.py``::

    from primate.models import UserBase, UserMeta
    from django.db import models

    class CustomUser(UserBase):
        __metaclass__ = UserMeta
        name = models.CharField(max_length=500, default='Jon Deg')
        title = models.CharField(max_length=20, blank=True)


``settings.py``::

    ``AUTH_USER_MODEL = 'users.models.CustomUser'``


Now you can import this model by ``from django.contrib.auth.models import
User`` or ``from project.users.models import CustomUser``


Custom fields and overriding default fields
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
It's simple

- To add a field just add a field to the model as you would normally.
- To override a field just override the field name and it will be used instead
  of the one defined in UserBase.

The overriding feature is something special not available in normal Django
model abstract classes and is done in the custom metaclass. You can also remove
fields defined in the ``UserBase`` class by altering the metaclass a little, you
can have a look in the code, its a really simple.


Admin
^^^^^
To make the admin work I have made the monkey patch ``primate.patch`` patch the
``admin.autodiscover`` so that it does not register the default admin class for
``django.contrib.auth.User``. This means that you will need to register that
your self. The easiest way to do that is to first add ``users`` to your
``INSTALLED_APPS`` and then add something like this to ``ùsers.admin``::

    from primate.admin import UserAdminBase
    from django.contrib import admin
    from django.contrib.auth.models import User


    class UserAdmin(UserAdminBase):
        pass


    admin.site.register(User, UserAdmin)


What's new in the default user model?
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
I have made some minor changes:

1. Removed ``first_name`` and ``last_name``
2. Added ``name``
3. ``username`` is now max 50 chars
3. Made ``email`` unique
4. ``get_profile`` method just returns self

As stated earlier, you can now change all this, remove add and override fields
in your user model.


South
^^^^^
I was worried, this is a major feature, luckely Andrew already thought of this:
qoute from the documentation under ``SOUTH_MIGRATION_MODULES``:

"Note that the keys in this dictionary are ‘app labels’, not the full paths to
apps; for example, were I to provide a migrations directory for
django.contrib.auth, I’d want to use auth as the key here."

So the time has come, just add this to your settings::

    SOUTH_MIGRATION_MODULES = {
        'auth': 'users.migrations',
    }


