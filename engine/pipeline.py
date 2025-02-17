from telegram import Telegram
from social_django.models import UserSocialAuth


def save_user(backend, user, response, *args, **kwargs):
    social_provider = backend.name
    user_email = user.email
    email = response.get('email', '')
    if social_provider == 'twitter':
        email = response.get('id')
        user_email = user.username
    existing_user = UserSocialAuth.objects.filter(uid=email).first()

    if existing_user:
        return
    else:
        try:

            Telegram.new_reg(user_email, social_provider)
        except Exception as e:
            print(f"Error: {e}")
