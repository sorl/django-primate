from django.utils.crypto import constant_time_compare as ctcmp
from django.utils.encoding import smart_str


class BcryptMixin(object):
    rounds = 12

    def check_password(self, raw_password):
        import bcrypt
        if self.password.startswith('bcrypt$'):
            hash_ = self.password[6:] # remove bcrypt prefix
            salt = hash_[:29]
            return ctcmp(hash_, bcrypt.hashpw(raw_password, salt))
        if super(BcryptMixin, self).check_password(raw_password):
            # Convert the password to the new, more secure format.
            self.set_password(raw_password)
            self.save()
            return True
        return False

    def set_password(self, raw_password):
        import bcrypt
        if raw_password is None:
            self.set_unusable_password()
        else:
            raw_password = smart_str(raw_password)
            salt = bcrypt.gensalt(self.rounds)
            self.password = 'bcrypt%s' % bcrypt.hashpw(raw_password, salt)

