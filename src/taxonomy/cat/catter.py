"""SQL statement categorization interface."""

from src.utils.logging import logger

from src.taxonomy.cat.categorizer import Categorizer
from src.taxonomy.cat.statement_category import StatementCategory
from src.taxonomy.cat.sub_category import SubCategory
from src.taxonomy.cat.tag_extractor import TagExtractor
from src.taxonomy.parse.parser import SqlParser


class Catter:
    """Main interface for categorizing SQL statements."""

    parser = SqlParser()
    tag_extractor = TagExtractor()
    categorizer = Categorizer()

    def get_category(self, sql: str) -> StatementCategory | None:
        """Get the category of a SQL statement.

        Parameters
        ----------
        sql : str
            The SQL statement to categorize.

        Returns
        -------
        StatementCategory or None
            The statement category or None if an error occurs.
        """
        try:
            ast = self.parser.parse(sql)
            if ast is None:
                return None
            tags = self.tag_extractor.extract_tags(ast)
            return self.categorizer.get_category(tags.tag_set)
        except Exception as e:
            logger.debug(e)
            return None

    def get_sub_category(self, sql: str) -> SubCategory:
        """Get the sub-category of a SQL statement.

        Parameters
        ----------
        sql : str
            The SQL statement to categorize.

        Returns
        -------
        SubCategory
            The sub-category of the statement.
        """
        ast = self.parser.parse(sql)
        if ast is None:
            return SubCategory("unknown", frozenset())
        tags = self.tag_extractor.extract_tags(ast)
        return self.categorizer.get_sub_category(tags.tag_set)

    def categorize(self, sql: str) -> tuple[StatementCategory | None, SubCategory]:
        """Get both category and sub-category of a SQL statement.

        Parameters
        ----------
        sql : str
            The SQL statement to categorize.

        Returns
        -------
        tuple
            A tuple of (StatementCategory, SubCategory).
        """
        return self.get_category(sql), self.get_sub_category(sql)
