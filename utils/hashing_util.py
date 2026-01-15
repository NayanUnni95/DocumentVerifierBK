from django.contrib.auth.hashers import make_password, check_password


class Hash:
    @staticmethod
    def encrypt_password(password: str):
        return make_password(password)

    @staticmethod
    def verify_password(password: str, hashed_password: str):
        return check_password(password, hashed_password)