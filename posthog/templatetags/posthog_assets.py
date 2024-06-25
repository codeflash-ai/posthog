import re
from functools import lru_cache
from typing import Dict, List

from django.conf import settings
from django.template import Library

from posthog.utils import absolute_uri as util_absolute_uri

register = Library()


@register.simple_tag
def absolute_uri(url: str = "") -> str:
    return util_absolute_uri(url)


@register.simple_tag
def absolute_asset_url(path: str) -> str:
    """
    Returns a versioned absolute asset URL (located within PostHog's static files).
    Example:
      {% absolute_asset_url 'dist/posthog.css' %}
      =>  "http://posthog.example.com/_static/74d127b78dc7daf2c51f/dist/posthog.css"
    """
    return absolute_uri(f"{settings.STATIC_URL.rstrip('/')}/{path.lstrip('/')}")


@register.simple_tag
def human_social_providers(providers: List[str]) -> str:
    """Converts a list of provider identifiers into human-friendly names.

    Parameters
    ----------
    providers : list of str
        The list of provider identifiers.

    Returns
    -------
    str
        The comma-separated human-friendly names of the providers.
    """

    @lru_cache(None)
    def build_provider_mapping() -> Dict[str, str]:
        """Builds and caches the mapping dictionary for provider identifiers.

        Returns
        -------
        dict
            A dictionary mapping provider identifiers to human-friendly names.
        """
        return {"google-oauth2": "Google", "github": "GitHub", "gitlab": "GitLab", "saml": "single sign-on (SAML)"}

    def precompute_provider_names(providers: List[str], mapping: Dict[str, str]) -> List[str]:
        """Precomputes the human-friendly names for the input providers.

        Parameters
        ----------
        providers : list of str
            The list of provider identifiers.
        mapping : dict of str to str
            The mapping dictionary for provider identifiers.

        Returns
        -------
        list of str
            The human-friendly names of the providers.
        """
        return [mapping.get(provider, "single sign-on (SAML)") for provider in providers]

    mapping = build_provider_mapping()
    friendly_names = precompute_provider_names(providers, mapping)
    return ", ".join(friendly_names)


@register.simple_tag
def strip_protocol(path: str) -> str:
    """
    Returns a URL removing the http/https protocol
    Example:
      {% strip_protocol 'https://app.posthog.com' %}
      =>  "app.posthog.com"
    """
    return re.sub(r"https?:\/\/", "", path)
