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


def clean_entity_properties(
    properties: list[dict[str, object]] | dict[str, object] | None
) -> list[dict[str, object]] | None:
    """Clean and normalize entity properties."""
    if properties is None or len(properties) == 0:
        return None
    elif is_old_style_properties(properties):
        return transform_old_style_properties(properties)
    elif isinstance(properties, list):
        return [clean_property(prop) for prop in properties]
    elif (
        isinstance(properties, dict)
        and properties.get("type") in ["AND", "OR"]
        and not any(property.get("type") in ["AND", "OR"] for property in properties["values"])
    ):
        return [clean_property(prop) for prop in properties["values"]]
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
    """Clean and normalize a property dictionary."""
    cleaned_property = {**property}

    _type = cleaned_property.get("type")

    if _type == "events":
        cleaned_property["type"] = "event"
    elif _type in ("precalculated-cohort", "static-cohort"):
        cleaned_property["type"] = "cohort"

    cleaned_property["value"] = cleaned_property.pop("values", cleaned_property.get("value"))

    if cleaned_property.get("type") == "cohort" and cleaned_property.get("key") != "id":
        cleaned_property["key"] = "id"

    if is_property_with_operator(cleaned_property):
        cleaned_property.setdefault("operator", "exact")
    else:
        cleaned_property.pop("operator", None)

    if isinstance(cleaned_property.get("value"), list):
        cleaned_property["value"] = [x for x in cleaned_property["value"] if x is not None]  # type: ignore

    return {key: value for key, value in cleaned_property.items() if value is not None}


def is_property_with_operator(property: dict):
    return property.get("type") not in ("cohort", "hogql")


def is_old_style_properties(properties: dict[str, object] | None) -> bool:
    """Check if the properties dictionary is in old-style format."""
    return isinstance(properties, dict) and len(properties) == 1 and properties.get("type") not in ("AND", "OR")


def transform_old_style_properties(properties: dict[str, object]) -> list[dict[str, object]]:
    """Transform old-style properties dictionary to new-style properties list."""
    key, value = next(iter(properties.items()))
    key_split = key.split("__")
    operator = key_split[1] if len(key_split) > 1 else "exact"
    return [{"key": key_split[0], "value": value, "operator": operator, "type": "event"}]


def is_old_style_properties(properties: dict[str, object] | None) -> bool:
    """Check if the properties dictionary is in old-style format."""
    return isinstance(properties, dict) and len(properties) == 1 and properties.get("type") not in ("AND", "OR")


def transform_old_style_properties(properties: dict[str, object]) -> list[dict[str, object]]:
    """Transform old-style properties dictionary to new-style properties list."""
    key, value = next(iter(properties.items()))
    key_split = key.split("__")
    operator = key_split[1] if len(key_split) > 1 else "exact"
    return [{"key": key_split[0], "value": value, "operator": operator, "type": "event"}]


def clean_property(property: dict[str, object]) -> dict[str, object]:
    """Clean and normalize a property dictionary."""
    cleaned_property = {**property}

    _type = cleaned_property.get("type")

    if _type == "events":
        cleaned_property["type"] = "event"
    elif _type in ("precalculated-cohort", "static-cohort"):
        cleaned_property["type"] = "cohort"

    cleaned_property["value"] = cleaned_property.pop("values", cleaned_property.get("value"))

    if cleaned_property.get("type") == "cohort" and cleaned_property.get("key") != "id":
        cleaned_property["key"] = "id"

    if is_property_with_operator(cleaned_property):
        cleaned_property.setdefault("operator", "exact")
    else:
        cleaned_property.pop("operator", None)

    if isinstance(cleaned_property.get("value"), list):
        cleaned_property["value"] = [x for x in cleaned_property["value"] if x is not None]  # type: ignore

    return {key: value for key, value in cleaned_property.items() if value is not None}
