import random
import os
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(user.is_email_verified) + str(timestamp)
        )

email_verification_token_generator = EmailVerificationTokenGenerator()

def generate_2fa_code(user_id):
    
    code = f"{random.randint(100000, 999999)}"
    cache_key = f"2fa_code_{user_id}"
    cache.set(cache_key, code, timeout=300)
    return code

def verify_2fa_code(user_id, code):
    cache_key = f"2fa_code_{user_id}"
    attempts_key = f"2fa_attempts_{user_id}"
    
    attempts = cache.get(attempts_key, 0)
    if attempts >= 5:
        return False, "Too many attempts. Please try logging in again."
    stored_code = cache.get(cache_key)
    if stored_code and stored_code == code:
        cache.delete(cache_key)
        cache.delete(attempts_key)
        return True, None
    
    cache.set(attempts_key, attempts + 1, timeout=300)
    return False, "Invalid code."




def send_2fa_code(user_id, email):
    code = generate_2fa_code(user_id)
    send_mail(
        "Your 2FA Login Code",
        f"Your verification code is: {code}",
       os.environ.get('EMAIL_HOST_USER'),
        [email],
        fail_silently=False,
    )