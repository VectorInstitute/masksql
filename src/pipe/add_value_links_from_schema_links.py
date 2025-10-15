"""Module for extracting value links from schema links."""

from src.pipe.processor.list_transformer import JsonListTransformer


class AddValueLinksFromSchemaLinks(JsonListTransformer):
    """
    Processor for extracting value links from schema links.

    Separates value links (prefixed with 'VALUE:') from schema links,
    creating separate mappings for each.
    """

    async def _process_row(self, row):
        schema_links = row["schema_links"]
        value_links = {}
        updated_schema_links = {}
        for q_term, item in schema_links.items():
            if "VALUE:" in item:
                item = item.replace("VALUE:", "")
                value_links[q_term] = item
            else:
                updated_schema_links[q_term] = item
        row["schema_links"] = updated_schema_links
        row["value_links"] = value_links
        return row
