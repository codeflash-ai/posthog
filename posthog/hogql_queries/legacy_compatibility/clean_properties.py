def clean_global_properties(properties: dict | list[dict] | None):
    if properties is None or len(properties) == 0:
        # empty properties
        return None
    elif is_old_style_properties(properties):
        # old style properties
        properties = transform_old_style_properties(properties)
        properties = {
            "type": "AND",
            "values": [{"type": "AND", "values": properties}],
        }
        return clean_property_group_filter(properties)
    elif isinstance(properties, list):
        # list of property filters
        properties = {
            "type": "AND",
            "values": [{"type": "AND", "values": properties}],
        }
        return clean_property_group_filter(properties)
    elif (
        isinstance(properties, dict)
        and properties.get("type") in ["AND", "OR"]
        and not any(property.get("type") in ["AND", "OR"] for property in properties["values"])
    ):
        # property group filter value
        properties = {
            "type": "AND",
            "values": [properties],
        }
        return clean_property_group_filter(properties)
    else:
        # property group filter
        return clean_property_group_filter(properties)


def clean_entity_properties(properties: list[dict] | dict | None):
    if properties is None or len(properties) == 0:
        # empty properties
        return None
    elif is_old_style_properties(properties):
        # old style properties
        return transform_old_style_properties(properties)
    elif isinstance(properties, list):
        # list of property filters
        return list(map(clean_property, properties))
    elif (
        isinstance(properties, dict)
        and properties.get("type") in ["AND", "OR"]
        and not any(property.get("type") in ["AND", "OR"] for property in properties["values"])
    ):
        # property group filter value
        return list(map(clean_property, properties["values"]))
    else:
        raise ValueError("Unexpected format of entity properties.")


def clean_property_group_filter(properties: dict):
    properties["values"] = clean_property_group_filter_values(properties["values"])
    return properties


def clean_property_group_filter_values(properties: list[dict]):
    cleaned = [clean_property_group_filter_value(property) for property in properties if property]
    return cleaned


def clean_property_group_filter_value(property: dict):
    if property.get("type") in ["AND", "OR"]:
        # property group filter value
        property["values"] = clean_property_group_filter_values(property["values"])
        return property
    else:
        # property filter
        return clean_property(property)


def clean_property(property: dict[str, object]) -> dict[str, object]:
    """Clean the property dictionary by applying several corrections.

    Args:
        property (dict): The property dictionary to clean.

    Returns:
        dict: The cleaned property dictionary."""

    # Create a copy of the dictionary
    cleaned_property = {**property}

    # Transformations and clean-up steps
    type_corrections = {"events": "event", "precalculated-cohort": "cohort", "static-cohort": "cohort"}

    if cleaned_property.get("type") in type_corrections:
        cleaned_property["type"] = type_corrections[cleaned_property.get("type")]

    if cleaned_property.get("values") is not None and cleaned_property.get("value") is None:
        cleaned_property["value"] = cleaned_property.pop("values")

    if cleaned_property.get("type") == "cohort" and cleaned_property.get("key") != "id":
        cleaned_property["key"] = "id"

    if is_property_with_operator(cleaned_property) and cleaned_property.get("operator") is None:
        cleaned_property["operator"] = "exact"
    elif not is_property_with_operator(cleaned_property) and cleaned_property.get("operator") is not None:
        del cleaned_property["operator"]

    if isinstance(cleaned_property.get("value"), list):
        cleaned_property["value"] = [v for v in cleaned_property.get("value") if v is not None]

    return {k: v for k, v in cleaned_property.items() if v is not None}


def is_property_with_operator(property: dict[str, object]) -> bool:
    """Check if a property dictionary requires an operator.

    Args:
        property (dict): The property dictionary to check.

    Returns:
        bool: True if the property type needs an operator."""
    return property.get("type") not in ("cohort", "hogql")


# old style dict properties e.g. {"utm_medium__icontains": "email"}
def is_old_style_properties(properties):
    return isinstance(properties, dict) and len(properties) == 1 and properties.get("type") not in ("AND", "OR")


def transform_old_style_properties(properties):
    key = next(iter(properties.keys()))
    value = next(iter(properties.values()))
    key_split = key.split("__")
    return [
        {
            "key": key_split[0],
            "value": value,
            "operator": key_split[1] if len(key_split) > 1 else "exact",
            "type": "event",
        }
    ]


def is_property_with_operator(property: dict[str, object]) -> bool:
    """Check if a property dictionary requires an operator.

    Args:
        property (dict): The property dictionary to check.

    Returns:
        bool: True if the property type needs an operator."""
    return property.get("type") not in ("cohort", "hogql")
