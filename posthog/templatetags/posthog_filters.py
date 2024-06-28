from typing import Optional, Union

from django import template

from posthog.utils import compact_number

register = template.Library()

Number = Union[int, float]

register.filter(compact_number)


@register.filter
def percentage(value: Optional[Number], decimals: int = 1) -> str:
    """
    Returns a rounded formatted with a specific number of decimal digits and a % sign.

    Parameters
    ----------
    value : Optional[Number]
        The number to be converted to a percentage.

    decimals : int, default=1
        The number of decimal places to include in the formatted percentage.

    Returns
    -------
    str
        Formatted percentage string or '-' if value is None.

    Example
    -------
    >>> percentage(0.2283113)
    '22.8%'
    """
    return "-" if value is None else f"{value * 100:.{decimals}f}%"
