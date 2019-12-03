from django.contrib.auth.hashers import BCryptSHA256PasswordHasher


class MyBCryptPasswordHasher(BCryptSHA256PasswordHasher):
    """
    A subclass of BCryptSHA256PasswordHasher that uses 100 times more iterations
    """
    iterations = BCryptSHA256PasswordHasher.rounds * 100
