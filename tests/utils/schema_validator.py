import xmlschema
from pathlib import Path

def is_pi_timeseries_valid(xml_path: str, schema_url: str = None) -> bool:
    """
    Validate an XML file against the PI timeseries XSD.

    Args:
        xml_path (str): Path to the XML file to validate.
        schema_url (str | None): URL or local path to the XSD schema.
            If None, defaults to the online Delft-FEWS pi_timeseries schema.

    Returns:
        bool: True if the XML is valid according to the schema, False otherwise.
    """
    # Default schema location (online)
    if schema_url is None:
        schema_url = (
            "https://fewsdocs.deltares.nl/schemas/version1.0/pi-schemas/pi_timeseries.xsd"
        )

    xml_file = Path(xml_path)
    if not xml_file.is_file():
        raise FileNotFoundError(f"XML file not found: {xml_path}")

    try:
        # Load the XML schema (from URL or local file)
        schema = xmlschema.XMLSchema(schema_url)

        # Validate and return result
        return schema.is_valid(xml_file)

    except Exception as e:
        # Any exception typically means validation failed or schema load failed
        print(f"Validation error: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    test_xml = "timeseries_import.xml"
    is_valid = is_pi_timeseries_valid(test_xml)
    if is_valid:
        print(f"'{test_xml}' is valid according to the PI timeseries schema.")
    else:
        print(f"'{test_xml}' is NOT valid according to the PI timeseries schema.")