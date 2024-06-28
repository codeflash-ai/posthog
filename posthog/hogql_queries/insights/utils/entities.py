from posthog.schema import ActionsNode, EventsNode, FunnelExclusionActionsNode, FunnelExclusionEventsNode
from posthog.types import AnyPropertyFilter, EntityNode, ExclusionEntityNode
from collections import Counter
from rest_framework.exceptions import ValidationError
from functools import lru_cache


def is_equal_type(a: EntityNode, b: EntityNode | ExclusionEntityNode) -> bool:
    if isinstance(a, EventsNode):
        return isinstance(b, EventsNode) or isinstance(b, FunnelExclusionEventsNode)
    elif isinstance(a, ActionsNode):
        return isinstance(b, ActionsNode) or isinstance(b, FunnelExclusionActionsNode)
    else:
        raise ValidationError(detail=f"Type comparision for {type(a)} and {type(b)} not implemented.")


def is_equal(a: EntityNode, b: EntityNode | ExclusionEntityNode, compare_properties=True) -> bool:
    """Checks if two entities are semantically equal."""

    # different type
    if not is_equal_type(a, b):
        return False

    # different action
    if (
        isinstance(a, ActionsNode | FunnelExclusionActionsNode)
        and isinstance(b, ActionsNode | FunnelExclusionActionsNode)
        and a.id != b.id
    ):
        return False

    # different event
    if (
        isinstance(a, EventsNode | FunnelExclusionEventsNode)
        and isinstance(b, EventsNode | FunnelExclusionEventsNode)
        and a.event != b.event
    ):
        return False

    # different properties
    if compare_properties and _sorted_property_reprs(a.properties) != _sorted_property_reprs(b.properties):
        return False

    # different fixed properties
    if compare_properties and _sorted_property_reprs(a.fixedProperties) != _sorted_property_reprs(b.fixedProperties):
        return False

    # TODO: compare math (only for trends)

    return True


def is_superset(a: EntityNode, b: EntityNode | ExclusionEntityNode) -> bool:
    """Checks if this entity is a superset version of other. The nodes match and the properties of (a) is a subset of the properties of (b)."""

    if not is_equal(a, b, compare_properties=False):
        return False

    properties_a = Counter(_sorted_property_reprs(a.properties))
    properties_b = Counter(_sorted_property_reprs(b.properties))

    if len(properties_a - properties_b) != 0:
        return False

    fixed_properties_a = Counter(_sorted_property_reprs(a.fixedProperties))
    fixed_properties_b = Counter(_sorted_property_reprs(b.fixedProperties))

    return len(fixed_properties_a - fixed_properties_b) == 0


def _sorted_property_reprs(properties: list[AnyPropertyFilter] | None) -> list[str]:
    """Sort and generate string representations for property filters

    Parameters
    ----------
    properties : list[AnyPropertyFilter] | None
        List of property filters to process

    Returns
    -------
    list[str]
        Sorted string representation of property filters.
    """
    if properties is None:
        return []
    reprs = (_semantic_property_repr(prop) for prop in properties)
    return sorted([rep for rep in reprs if rep])


@lru_cache(maxsize=None)
def _semantic_property_repr(property: AnyPropertyFilter) -> str:
    """Generate string representation for given property

    Parameters
    ----------
    property : AnyPropertyFilter
        The property to generate the string representation for

    Returns
    -------
    str
        String representation of the property
    """
    return _get_repr_format(property).format(
        type=property.type, key=property.key, operator=getattr(property, "operator", ""), value=property.value
    )


def _get_repr_format(property: AnyPropertyFilter) -> str:
    """Get the appropriate format string based on the property type

    Parameters
    ----------
    property : AnyPropertyFilter
        The property to get the representation format string for

    Returns
    -------
    str
        The format string for the given property type
    """
    return FORMAT_STRINGS.get(type(property), "{type}: {key} {operator} {value}")


@lru_cache(maxsize=None)
def _semantic_property_repr(property: AnyPropertyFilter) -> str:
    """Generate string representation for given property

    Parameters
    ----------
    property : AnyPropertyFilter
        The property to generate the string representation for

    Returns
    -------
    str
        String representation of the property
    """
    return _get_repr_format(property).format(
        type=property.type, key=property.key, operator=getattr(property, "operator", ""), value=property.value
    )
