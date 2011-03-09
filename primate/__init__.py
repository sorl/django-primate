def patch():
    """
    Monkeypatches the django.contrib.auth.models module and the admin
    autodiscover function
    """
    import django.contrib.auth
    import primate.auth.models
    django.contrib.auth.models = primate.auth.models
    import django.contrib.admin
    import primate.admin
    django.contrib.admin.autodiscover = primate.admin.autodiscover
