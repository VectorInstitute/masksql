"""Pipeline configuration definitions."""

import os

from src.pipe.add_schema import AddFilteredSchema, AddSchema
from src.pipe.add_symb_schema import AddSymbolicSchema
from src.pipe.copy_transformer import AddGoldValues, CopyTransformer
from src.pipe.det_mask import AddSymbolicQuestion
from src.pipe.detect_entities import DetectValues
from src.pipe.exec_acc import CalcExecAcc
from src.pipe.exec_conc_sql import ExecuteConcreteSql
from src.pipe.gen_masked_sql import GenerateSymbolicSql
from src.pipe.gen_sql import GenSql
from src.pipe.link_schema import LinkSchema
from src.pipe.processor.gen_sql_eval import GenSqlEval
from src.pipe.processor.limit_list import LimitJson
from src.pipe.processor.print_results import PrintResults
from src.pipe.processor.schema_link_eval import SchemaLinkEval
from src.pipe.processor.value_link_eval import ValueLinkEval
from src.pipe.rank_schema import RankSchemaResd
from src.pipe.repair_sql import RepairSQL
from src.pipe.repair_symb_sql import RepairSymbolicSQL
from src.pipe.symb_table import AddSymbolTable
from src.pipe.unmask import AddConcreteSql
from src.pipe.value_links import LinkValues


# Model configurations
LLM_MODEL = os.getenv("LLM_MODEL")
PRIVATE_MODEL = os.getenv("PRIVATE_MODEL")
SLM_MODEL = os.getenv("SLM_MODEL")

# Path configurations - these should be set appropriately for your environment
database_path = os.getenv("DATABASE_PATH", "../parser/data/bird/database")
tables_path = os.getenv("TABLES_PATH", "out/tables.json")

# Aliases for backwards compatibility
ExecAccCalc = CalcExecAcc
WrongExecAccOutput = ExecuteConcreteSql

unmask_pipe_llm = [
    LimitJson("limit"),
    RankSchemaResd(tables_path),
    AddSchema(tables_path),
    GenSql("pred_sql", model="openai/gpt-4.1"),
    ExecAccCalc(database_path),
]

unmask_pipe_slm = [
    LimitJson("limit"),
    RankSchemaResd(tables_path),
    AddSchema(tables_path),
    GenSql("pred_sql", model=PRIVATE_MODEL),
    ExecAccCalc(database_path),
    PrintResults(),
]

value_link_eval = [
    LimitJson("limit"),
    RankSchemaResd(tables_path),
    AddFilteredSchema(tables_path),
    AddSymbolTable(tables_path),
    DetectValues("values", model=SLM_MODEL),
    LinkValues("value_links", model=SLM_MODEL),
    CopyTransformer("value_links", "filtered_value_links"),
    ValueLinkEval(),
]

schema_link_eval = [
    LimitJson("limit"),
    RankSchemaResd(tables_path),
    AddFilteredSchema(tables_path),
    AddSymbolTable(tables_path),
    CopyTransformer("gold_value_links", "filtered_value_links"),
    AddGoldValues(),
    LinkSchema("schema_links", model=SLM_MODEL),
    CopyTransformer("schema_links", "filtered_schema_links"),
    SchemaLinkEval(),
]

gen_sql_eval = [
    LimitJson("limit"),
    RankSchemaResd(tables_path),
    AddFilteredSchema(tables_path),
    AddSymbolTable(tables_path),
    CopyTransformer("gold_value_links", "value_links"),
    CopyTransformer("gold_value_links", "filtered_value_links"),
    AddGoldValues(),
    CopyTransformer("gold_schema_links", "schema_links"),
    CopyTransformer("gold_schema_links", "filtered_schema_links"),
    AddSymbolicSchema("symbolic", tables_path),
    AddSymbolicQuestion(),
    GenerateSymbolicSql("symbolic", model=LLM_MODEL),
    RepairSymbolicSQL("symbolic", model=LLM_MODEL),
    AddConcreteSql(),
    WrongExecAccOutput(database_path),
    GenSqlEval(),
]

full_gold = [
    LimitJson("limit"),
    RankSchemaResd(tables_path),
    AddFilteredSchema(tables_path),
    AddSymbolTable(tables_path),
    CopyTransformer("gold_value_links", "value_links"),
    CopyTransformer("gold_value_links", "filtered_value_links"),
    AddGoldValues(),
    CopyTransformer("gold_schema_links", "schema_links"),
    CopyTransformer("gold_schema_links", "filtered_schema_links"),
    AddSymbolicSchema("symbolic", tables_path),
    AddSymbolicQuestion(),
    GenerateSymbolicSql("symbolic", model=LLM_MODEL),
    RepairSymbolicSQL("symbolic", model=LLM_MODEL),
    AddConcreteSql(),
    WrongExecAccOutput(database_path),
    RepairSQL("pred_sql", model=SLM_MODEL),
    ExecAccCalc(database_path),
    PrintResults(),
]
