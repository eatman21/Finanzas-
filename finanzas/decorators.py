"""
Custom decorators for the Finanzas application.
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.cache import cache


def require_financial_profile(view_func):
    """
    Decorator to require user to have a financial profile.
    Redirects to profile creation if not found.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'perfilfinanciero'):
            messages.error(
                request,
                'Primero debes crear tu perfil financiero.'
            )
            return redirect('finanzas:editar_perfil')
        return view_func(request, *args, **kwargs)
    return wrapper


def cache_page_per_user(timeout):
    """
    Cache decorator that caches per user.
    Usage: @cache_page_per_user(600)  # Cache for 10 minutes
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return view_func(request, *args, **kwargs)

            # Create cache key based on user and view
            cache_key = f'{view_func.__name__}_{request.user.id}_{request.GET.urlencode()}'
            response = cache.get(cache_key)

            if response is None:
                response = view_func(request, *args, **kwargs)
                cache.set(cache_key, response, timeout)

            return response
        return wrapper
    return decorator


def invalidate_cache_on_save(cache_keys):
    """
    Decorator to invalidate cache when a function is called.
    Usage: @invalidate_cache_on_save(['dashboard_{user_id}'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)

            # Invalidate specified caches
            for key_pattern in cache_keys:
                if '{user_id}' in key_pattern:
                    key = key_pattern.replace('{user_id}', str(request.user.id))
                    cache.delete(key)

            return response
        return wrapper
    return decorator
