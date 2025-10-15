"""SQL statement categorization interface."""

from loguru import logger

from src.taxonomy.cat.categorizer import Categorizer
from src.taxonomy.cat.tag_extractor import TagExtractor
from src.taxonomy.parse.parser import SqlParser


class Catter:
    """Main interface for categorizing SQL statements."""

    parser = SqlParser()
    tag_extractor = TagExtractor()
    categorizer = Categorizer()

    def get_category(self, sql: str):
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
            tags = self.tag_extractor.extract_tags(ast)
            return self.categorizer.get_category(tags.tag_set)
        except Exception as e:
            logger.debug(e)
            return None

    def get_sub_category(self, sql: str):
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
        tags = self.tag_extractor.extract_tags(ast)
        return self.categorizer.get_sub_category(tags.tag_set)

    def categorize(self, sql: str):
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
