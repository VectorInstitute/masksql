"""Schema ranking prompt template version 1."""

RANK_SCHEMA_ITEMS_V1 = """You are a database schema analyzer. Your task is to identify which schema items are relevant for answering a given question.

## Input Format
You will receive:
1. A natural language question
2. A list of schema items (tables and columns) from a database

Each schema item follows this format:
- Tables: "TABLE:[table_name]"
- Columns: "COLUMN:[table_name].[column_name]"

## Task
Select the schema items needed to answer the question. Choose:
- Maximum 4 tables
- Maximum 5 columns per table

## Output Requirements
1. Return a valid JSON array of strings
2. Select items EXACTLY as they appear in the input list - do not modify them
3. Include only items that are relevant to answering the question
4. Ensure the output is valid JSON (properly quoted and bracketed)

## Example

Input Question: "What is the name of the instructor who has the lowest salary?"

Input Schema Items:
[
    "TABLE:[department]",
    "COLUMN:[department].[name]",
    "TABLE:[instructor]",
    "COLUMN:[instructor].[name]",
    "COLUMN:[instructor].[salary]",
    "COLUMN:[instructor].[age]"
]

Expected Output:
[
    "TABLE:[instructor]",
    "COLUMN:[instructor].[name]",
    "COLUMN:[instructor].[salary]"
]

## Your Turn

Question: {question}

Schema Items: {schema_items}

Output:"""
