from django.shortcuts import redirect
from django.urls import reverse


def redirect_to_profile(strategy, details, user=None, *args, **kwargs):
    if user:
        username = user.username
        return redirect(reverse('profile', kwargs={'username': username}))
    else:
        return redirect('login')
