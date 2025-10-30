"""Tests for string manipulation utilities."""

from src.utils.strings import (
    Color,
    colored,
    delete_whitespace,
    get_colored_diff,
    is_quoted,
    pascal_to_snake,
    quote_str,
    shrink_whitespaces,
    split_pascal,
    split_to_snake,
)


class TestDeleteWhitespace:
    """Test suite for delete_whitespace function."""

    def test_delete_newlines(self):
        """Test deletion of newline characters."""
        assert delete_whitespace("hello\nworld") == "helloworld"

    def test_delete_carriage_returns(self):
        """Test deletion of carriage return characters."""
        assert delete_whitespace("hello\rworld") == "helloworld"

    def test_delete_mixed_whitespace(self):
        """Test deletion of mixed newlines and carriage returns."""
        assert delete_whitespace("hello\n\rworld\r\n") == "helloworld"

    def test_preserve_spaces_and_tabs(self):
        """Test that spaces and tabs are preserved."""
        assert delete_whitespace("hello world\ttab") == "hello world\ttab"

    def test_empty_string(self):
        """Test with empty string."""
        assert delete_whitespace("") == ""

    def test_only_newlines(self):
        """Test string with only newlines."""
        assert delete_whitespace("\n\n\n") == ""


class TestIsQuoted:
    """Test suite for is_quoted function."""

    def test_double_quoted(self):
        """Test detection of double-quoted strings."""
        assert is_quoted('"hello"') is True

    def test_single_quoted(self):
        """Test detection of single-quoted strings."""
        assert is_quoted("'hello'") is True

    def test_not_quoted(self):
        """Test detection of unquoted strings."""
        assert is_quoted("hello") is False

    def test_partial_quotes(self):
        """Test strings with partial quotes."""
        assert is_quoted('"hello') is False
        assert is_quoted('hello"') is False
        assert is_quoted("'hello") is False
        assert is_quoted("hello'") is False

    def test_mixed_quotes(self):
        """Test strings with mixed quote types."""
        assert is_quoted("\"hello'") is False
        assert is_quoted("'hello\"") is False

    def test_empty_quotes(self):
        """Test empty quoted strings."""
        assert is_quoted('""') is True
        assert is_quoted("''") is True

    def test_nested_quotes(self):
        """Test strings with nested quotes."""
        assert is_quoted("\"hello 'world'\"") is True
        assert is_quoted("'hello \"world\"'") is True


class TestQuoteStr:
    """Test suite for quote_str function."""

    def test_quote_unquoted_string(self):
        """Test quoting an unquoted string."""
        assert quote_str("hello") == "'hello'"

    def test_already_double_quoted(self):
        """Test string already wrapped in double quotes."""
        assert quote_str('"hello"') == '"hello"'

    def test_already_single_quoted(self):
        """Test string already wrapped in single quotes."""
        assert quote_str("'hello'") == "'hello'"

    def test_empty_string(self):
        """Test quoting empty string."""
        assert quote_str("") == "''"

    def test_string_with_spaces(self):
        """Test quoting string with spaces."""
        assert quote_str("hello world") == "'hello world'"


class TestShrinkWhitespaces:
    """Test suite for shrink_whitespaces function."""

    def test_multiple_spaces(self):
        """Test collapsing multiple spaces."""
        assert shrink_whitespaces("hello    world") == "hello world"

    def test_newlines_to_spaces(self):
        """Test converting newlines to spaces."""
        assert shrink_whitespaces("hello\nworld") == "hello world"

    def test_carriage_returns_to_spaces(self):
        """Test converting carriage returns to spaces."""
        assert shrink_whitespaces("hello\rworld") == "hello world"

    def test_mixed_whitespace(self):
        """Test normalizing mixed whitespace."""
        assert shrink_whitespaces("hello  \n\r  world") == "hello world"

    def test_leading_trailing_whitespace(self):
        """Test stripping leading and trailing whitespace."""
        assert shrink_whitespaces("  hello world  ") == "hello world"

    def test_tabs(self):
        """Test handling of tab characters."""
        assert shrink_whitespaces("hello\t\tworld") == "hello world"

    def test_none_input(self):
        """Test that None input returns None."""
        assert shrink_whitespaces(None) is None

    def test_empty_string(self):
        """Test with empty string."""
        assert shrink_whitespaces("") == ""

    def test_only_whitespace(self):
        """Test string with only whitespace."""
        assert shrink_whitespaces("   \n\r\t   ") == ""


class TestPascalToSnake:
    """Test suite for pascal_to_snake function."""

    def test_simple_pascal_case(self):
        """Test simple PascalCase conversion."""
        assert pascal_to_snake("BarBaz") == "bar_baz"

    def test_single_word(self):
        """Test single word conversion."""
        assert pascal_to_snake("Foo") == "foo"

    def test_multiple_capitals(self):
        """Test multiple consecutive capitals."""
        assert pascal_to_snake("HTTPServer") == "h_t_t_p_server"

    def test_already_lowercase(self):
        """Test already lowercase string."""
        assert pascal_to_snake("foo") == "foo"

    def test_mixed_case(self):
        """Test mixed case string."""
        assert pascal_to_snake("getUserID") == "get_user_i_d"

    def test_empty_string(self):
        """Test empty string."""
        assert pascal_to_snake("") == ""


class TestSplitPascal:
    """Test suite for split_pascal function."""

    def test_simple_pascal_case(self):
        """Test simple PascalCase splitting."""
        assert split_pascal("BarBaz") == "Bar Baz"

    def test_single_word(self):
        """Test single word splitting."""
        assert split_pascal("Foo") == "Foo"

    def test_multiple_words(self):
        """Test multiple words."""
        assert split_pascal("FooBarBaz") == "Foo Bar Baz"

    def test_consecutive_capitals(self):
        """Test consecutive capital letters."""
        # The regex splits each capital as a separate word
        assert split_pascal("HTTPServer") == "H T T P Server"

    def test_lowercase_word(self):
        """Test with lowercase words mixed in."""
        assert split_pascal("getUser") == "get User"

    def test_empty_string(self):
        """Test empty string."""
        assert split_pascal("") == ""


class TestSplitToSnake:
    """Test suite for split_to_snake function."""

    def test_simple_space_separated(self):
        """Test simple space-separated string."""
        assert split_to_snake("Bar Baz") == "bar_baz"

    def test_single_word(self):
        """Test single word."""
        assert split_to_snake("Foo") == "foo"

    def test_multiple_words(self):
        """Test multiple words."""
        assert split_to_snake("Foo Bar Baz") == "foo_bar_baz"

    def test_multiple_spaces(self):
        """Test multiple spaces between words."""
        assert split_to_snake("Foo  Bar   Baz") == "foo_bar_baz"

    def test_mixed_case(self):
        """Test mixed case words."""
        assert split_to_snake("HTTP Server") == "http_server"

    def test_empty_string(self):
        """Test empty string."""
        assert split_to_snake("") == ""


class TestColor:
    """Test suite for Color enum."""

    def test_color_values(self):
        """Test that color enum has expected ANSI codes."""
        assert Color.BLUE.value == "\033[94m"
        assert Color.GREEN.value == "\033[92m"
        assert Color.RED.value == "\033[91m"
        assert Color.ENDC.value == "\033[0m"

    def test_color_members(self):
        """Test that all expected colors are present."""
        color_names = [c.name for c in Color]
        assert "BLUE" in color_names
        assert "GREEN" in color_names
        assert "RED" in color_names
        assert "ENDC" in color_names


class TestColored:
    """Test suite for colored function."""

    def test_blue_text(self):
        """Test coloring text blue."""
        result = colored("hello", Color.BLUE)
        assert result == "\033[94mhello\033[0m"

    def test_green_text(self):
        """Test coloring text green."""
        result = colored("hello", Color.GREEN)
        assert result == "\033[92mhello\033[0m"

    def test_red_text(self):
        """Test coloring text red."""
        result = colored("hello", Color.RED)
        assert result == "\033[91mhello\033[0m"

    def test_empty_string(self):
        """Test coloring empty string."""
        result = colored("", Color.BLUE)
        assert result == "\033[94m\033[0m"

    def test_multiline_text(self):
        """Test coloring multiline text."""
        result = colored("hello\nworld", Color.GREEN)
        assert result == "\033[92mhello\nworld\033[0m"


class TestGetColoredDiff:
    """Test suite for get_colored_diff function."""

    def test_identical_strings(self):
        """Test diff of identical strings."""
        result = get_colored_diff("hello", "hello")
        assert result == "hello"

    def test_insertion(self):
        """Test diff with insertion."""
        result = get_colored_diff("hello", "hello world")
        assert Color.GREEN.value in result
        assert "world" in result

    def test_deletion(self):
        """Test diff with deletion."""
        result = get_colored_diff("hello world", "hello")
        assert Color.RED.value in result
        assert "world" in result

    def test_replacement(self):
        """Test diff with replacement."""
        result = get_colored_diff("hello", "hallo")
        assert Color.BLUE.value in result

    def test_case_insensitive(self):
        """Test that diff is case insensitive."""
        result = get_colored_diff("Hello", "hello")
        # Should be equal (case insensitive)
        assert result == "hello"

    def test_empty_strings(self):
        """Test diff of empty strings."""
        result = get_colored_diff("", "")
        assert result == ""

    def test_complex_diff(self):
        """Test complex diff with multiple changes."""
        result = get_colored_diff("the quick brown fox", "the slow brown cat")
        # Should contain colored sections for differences
        assert Color.ENDC.value in result
