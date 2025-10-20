# MaskSQL Python API Design Document

## Executive Summary

This document proposes a comprehensive Python API design for MaskSQL, a privacy-preserving text-to-SQL framework. The API aims to provide an easy-to-use, production-ready interface that enables developers to integrate MaskSQL into their applications with minimal effort while maintaining flexibility for advanced users.

**Design Goals:**
- **Simplicity**: Single-function API for common use cases
- **Flexibility**: Configurable privacy policies and pipeline stages
- **Type Safety**: Strong typing with Pydantic models
- **Performance**: Async-first architecture with batch processing
- **Production-Ready**: Proper error handling, logging, and monitoring
- **Testability**: Dependency injection and mockable components

## Current Architecture Overview

### Pipeline Framework
The current implementation uses a stage-based pipeline architecture:

```python
Pipeline(stages: List[JsonListProcessor])
  ├─ JsonListProcessor (base class)
  │   ├─ JsonListTransformer (file I/O)
  │   └─ PromptProcessor (LLM interactions)
  └─ Executes stages sequentially on JSON data
```

### Three-Stage MaskSQL Process

1. **Abstraction Stage**: Schema filtering, value/schema linking, token abstraction
2. **SQL Generation Stage**: Abstract SQL generation via LLM with self-correction
3. **Reconstruction Stage**: Symbol restoration, execution, and repair

### Current Limitations

1. Hard-coded pipeline configuration
2. File-based intermediate storage (no in-memory processing)
3. Configuration scattered across environment variables
4. No clear external API
5. Tight coupling to RESDSQL
6. Limited privacy policy customization
7. No structured error handling
8. Minimal type safety
9. Difficult to test in isolation

---

## Proposed API Design

### 1. High-Level Simple API

For users who want a simple interface:

```python
from masksql import MaskSQL, PrivacyPolicy

# Initialize with configuration
masksql = MaskSQL(
    llm_model="openai/gpt-4.1",
    slm_model="qwen/qwen2.5-7b-instruct",
    database_path="./databases",
    privacy_policy=PrivacyPolicy.FULL  # or PrivacyPolicy.CATEGORY
)

# Single query
result = await masksql.query(
    question="How many patients did the New York Hospital admit with HIV status as positive?",
    db_id="hospital_db"
)

print(result.sql)              # Generated SQL
print(result.execution_result)  # Query execution result
print(result.metrics)          # Privacy & accuracy metrics
```

### 2. Batch Processing API

For processing multiple queries:

```python
from masksql import MaskSQL, QueryRequest

masksql = MaskSQL.from_config("config.yaml")

# Batch queries
queries = [
    QueryRequest(
        question="What is the average age of patients?",
        db_id="hospital_db"
    ),
    QueryRequest(
        question="List all doctors in New York",
        db_id="hospital_db"
    )
]

results = await masksql.query_batch(queries, max_concurrency=10)

for result in results:
    print(f"Query: {result.question}")
    print(f"SQL: {result.sql}")
    print(f"Accuracy: {result.metrics.execution_accuracy}")
    print(f"Privacy: {result.metrics.masking_recall}")
```

### 3. Advanced API (Pipeline Customization)

For advanced users who need fine-grained control:

```python
from masksql import (
    MaskSQLPipeline,
    AbstractionStage,
    SQLGenerationStage,
    ReconstructionStage,
    PrivacyPolicy
)
from masksql.config import MaskSQLConfig

# Create custom configuration
config = MaskSQLConfig(
    llm_model="openai/gpt-4.1",
    slm_model="qwen/qwen2.5-7b-instruct",
    database_path="./databases",
    privacy_policy=PrivacyPolicy.custom(
        mask_tables=True,
        mask_columns=True,
        mask_values=True,
        categories=["person", "location", "medical"]
    ),
    schema_filter=SchemaFilterConfig(
        top_k_tables=4,
        top_j_columns=5,
        use_resdsql=True
    )
)

# Build custom pipeline
pipeline = MaskSQLPipeline(config) \
    .add_stage(AbstractionStage()) \
    .add_stage(SQLGenerationStage(enable_self_correction=True)) \
    .add_stage(ReconstructionStage(enable_repair=True))

# Execute
result = await pipeline.execute(
    question="Your question here",
    db_id="database_id"
)
```

### 4. Streaming API

For real-time applications:

```python
from masksql import MaskSQL
from masksql.streaming import StreamingMode

masksql = MaskSQL(
    llm_model="openai/gpt-4.1",
    slm_model="qwen/qwen2.5-7b-instruct",
    streaming=StreamingMode.ENABLED
)

async for event in masksql.query_stream(
    question="How many patients?",
    db_id="hospital_db"
):
    if event.type == "abstraction_complete":
        print(f"Abstract question: {event.data.abstract_question}")
    elif event.type == "sql_generated":
        print(f"Abstract SQL: {event.data.abstract_sql}")
    elif event.type == "complete":
        print(f"Final SQL: {event.data.sql}")
```

---

## Core Components

### 1. Configuration System

```python
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum

class PrivacyPolicy(Enum):
    """Predefined privacy policies."""
    FULL = "full"           # Mask all schema elements and values
    CATEGORY = "category"   # Mask only specific categories
    MINIMAL = "minimal"     # Mask only PII
    CUSTOM = "custom"       # User-defined policy

@dataclass
class CustomPrivacyPolicy:
    """Custom privacy policy configuration."""
    mask_tables: bool = True
    mask_columns: bool = True
    mask_values: bool = True
    categories: Optional[List[str]] = None  # ["person", "location", etc.]

    # Fine-grained control
    table_whitelist: Optional[List[str]] = None
    column_whitelist: Optional[List[str]] = None
    value_patterns: Optional[List[str]] = None  # Regex patterns

@dataclass
class SchemaFilterConfig:
    """Schema filtering configuration."""
    use_resdsql: bool = True
    top_k_tables: int = 4
    top_j_columns: int = 5

    # Alternative: custom ranker
    custom_ranker: Optional[callable] = None

@dataclass
class ModelConfig:
    """Language model configuration."""
    llm_model: str = "openai/gpt-4.1"
    slm_model: str = "qwen/qwen2.5-7b-instruct"
    llm_temperature: float = 0.0
    slm_temperature: float = 0.0
    max_tokens: int = 2048
    timeout: float = 60.0

    # API configuration
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None

@dataclass
class PipelineConfig:
    """Pipeline execution configuration."""
    enable_schema_filtering: bool = True
    enable_value_linking: bool = True
    enable_sql_correction: bool = True
    enable_sql_repair: bool = True
    enable_attack_simulation: bool = False

    # Performance
    max_retries: int = 3
    cache_enabled: bool = True
    cache_ttl: int = 3600

@dataclass
class MaskSQLConfig:
    """Main configuration for MaskSQL."""
    database_path: str
    privacy_policy: PrivacyPolicy = PrivacyPolicy.FULL
    custom_policy: Optional[CustomPrivacyPolicy] = None

    models: ModelConfig = ModelConfig()
    schema_filter: SchemaFilterConfig = SchemaFilterConfig()
    pipeline: PipelineConfig = PipelineConfig()

    # Paths
    cache_dir: Optional[str] = None
    log_dir: Optional[str] = None

    @classmethod
    def from_yaml(cls, path: str) -> "MaskSQLConfig":
        """Load configuration from YAML file."""
        pass

    @classmethod
    def from_dict(cls, config: dict) -> "MaskSQLConfig":
        """Create configuration from dictionary."""
        pass
```

### 2. Data Models

```python
from dataclasses import dataclass
from typing import Optional, Dict, List, Any
from datetime import datetime

@dataclass
class QueryRequest:
    """Input query request."""
    question: str
    db_id: str
    hint: Optional[str] = None  # Optional hint for complex queries
    evidence: Optional[str] = None  # BIRD-style evidence

@dataclass
class AbstractionResult:
    """Result of abstraction stage."""
    abstract_question: str
    abstract_schema: Dict[str, Any]
    symbol_table: Dict[str, str]
    masked_terms: List[str]
    schema_links: Dict[str, str]
    value_links: Dict[str, str]

@dataclass
class SQLGenerationResult:
    """Result of SQL generation stage."""
    abstract_sql: str
    corrected_abstract_sql: Optional[str] = None
    generation_attempts: int = 1

@dataclass
class ReconstructionResult:
    """Result of reconstruction stage."""
    concrete_sql: str
    repaired_sql: Optional[str] = None
    execution_result: Optional[Any] = None
    execution_error: Optional[str] = None

@dataclass
class PrivacyMetrics:
    """Privacy evaluation metrics."""
    masking_recall: float
    reidentification_score: float
    masked_token_count: int
    total_token_count: int

@dataclass
class PerformanceMetrics:
    """Performance metrics."""
    total_latency_ms: float
    total_tokens: int
    llm_calls: int
    slm_calls: int
    memory_usage_mb: Optional[float] = None

@dataclass
class QueryResult:
    """Complete query result."""
    # Input
    question: str
    db_id: str

    # Output
    sql: str
    execution_result: Optional[Any] = None
    execution_error: Optional[str] = None

    # Intermediate results
    abstraction: Optional[AbstractionResult] = None
    generation: Optional[SQLGenerationResult] = None
    reconstruction: Optional[ReconstructionResult] = None

    # Metrics
    metrics: Optional[PrivacyMetrics] = None
    performance: Optional[PerformanceMetrics] = None

    # Evaluation
    execution_accuracy: Optional[float] = None
    gold_sql: Optional[str] = None
    gold_result: Optional[Any] = None

    # Metadata
    timestamp: datetime = None
    pipeline_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        pass

    def to_json(self) -> str:
        """Convert to JSON string."""
        pass
```

### 3. Main MaskSQL Class

```python
from typing import Optional, List, AsyncIterator
import asyncio
from loguru import logger

class MaskSQL:
    """Main MaskSQL interface for privacy-preserving text-to-SQL."""

    def __init__(
        self,
        llm_model: str = "openai/gpt-4.1",
        slm_model: str = "qwen/qwen2.5-7b-instruct",
        database_path: str = "./databases",
        privacy_policy: PrivacyPolicy = PrivacyPolicy.FULL,
        config: Optional[MaskSQLConfig] = None,
        **kwargs
    ):
        """
        Initialize MaskSQL.

        Parameters
        ----------
        llm_model : str
            Large language model identifier
        slm_model : str
            Small language model identifier
        database_path : str
            Path to database directory
        privacy_policy : PrivacyPolicy
            Privacy policy to use
        config : Optional[MaskSQLConfig]
            Full configuration object (overrides other params)
        **kwargs
            Additional configuration options
        """
        if config:
            self.config = config
        else:
            self.config = MaskSQLConfig(
                database_path=database_path,
                privacy_policy=privacy_policy,
                models=ModelConfig(
                    llm_model=llm_model,
                    slm_model=slm_model
                ),
                **kwargs
            )

        self._pipeline = self._build_pipeline()
        self._schema_repo = DatabaseSchemaRepo(database_path)

    @classmethod
    def from_config(cls, config_path: str) -> "MaskSQL":
        """Create MaskSQL instance from configuration file."""
        config = MaskSQLConfig.from_yaml(config_path)
        return cls(config=config)

    async def query(
        self,
        question: str,
        db_id: str,
        hint: Optional[str] = None,
        evidence: Optional[str] = None,
        return_intermediate: bool = False
    ) -> QueryResult:
        """
        Execute a single privacy-preserving text-to-SQL query.

        Parameters
        ----------
        question : str
            Natural language question
        db_id : str
            Database identifier
        hint : Optional[str]
            Optional hint for complex queries
        evidence : Optional[str]
            Optional evidence (BIRD-style)
        return_intermediate : bool
            Whether to return intermediate results

        Returns
        -------
        QueryResult
            Complete query result with SQL, metrics, and optional intermediate results

        Examples
        --------
        >>> masksql = MaskSQL()
        >>> result = await masksql.query(
        ...     question="How many patients?",
        ...     db_id="hospital_db"
        ... )
        >>> print(result.sql)
        """
        request = QueryRequest(
            question=question,
            db_id=db_id,
            hint=hint,
            evidence=evidence
        )

        try:
            result = await self._pipeline.execute(request)

            if not return_intermediate:
                # Clear intermediate results to save memory
                result.abstraction = None
                result.generation = None
                result.reconstruction = None

            return result

        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise MaskSQLException(f"Query execution failed: {str(e)}") from e

    async def query_batch(
        self,
        queries: List[QueryRequest],
        max_concurrency: int = 10,
        show_progress: bool = True
    ) -> List[QueryResult]:
        """
        Execute multiple queries in batch with concurrency control.

        Parameters
        ----------
        queries : List[QueryRequest]
            List of query requests
        max_concurrency : int
            Maximum number of concurrent queries
        show_progress : bool
            Whether to show progress bar

        Returns
        -------
        List[QueryResult]
            List of query results
        """
        semaphore = asyncio.Semaphore(max_concurrency)

        async def process_query(request: QueryRequest) -> QueryResult:
            async with semaphore:
                return await self.query(
                    question=request.question,
                    db_id=request.db_id,
                    hint=request.hint,
                    evidence=request.evidence
                )

        tasks = [process_query(q) for q in queries]

        if show_progress:
            # Use tqdm for progress tracking
            from tqdm.asyncio import tqdm
            results = await tqdm.gather(*tasks, desc="Processing queries")
        else:
            results = await asyncio.gather(*tasks)

        return results

    async def query_stream(
        self,
        question: str,
        db_id: str
    ) -> AsyncIterator[PipelineEvent]:
        """
        Execute query with streaming intermediate results.

        Parameters
        ----------
        question : str
            Natural language question
        db_id : str
            Database identifier

        Yields
        ------
        PipelineEvent
            Stream of pipeline events
        """
        request = QueryRequest(question=question, db_id=db_id)
        async for event in self._pipeline.execute_stream(request):
            yield event

    async def evaluate(
        self,
        dataset_path: str,
        output_path: Optional[str] = None,
        metrics: List[str] = ["accuracy", "privacy", "efficiency"]
    ) -> EvaluationReport:
        """
        Evaluate MaskSQL on a dataset.

        Parameters
        ----------
        dataset_path : str
            Path to evaluation dataset (JSON format)
        output_path : Optional[str]
            Path to save detailed results
        metrics : List[str]
            Metrics to compute

        Returns
        -------
        EvaluationReport
            Comprehensive evaluation report
        """
        pass

    def _build_pipeline(self) -> MaskSQLPipeline:
        """Build the execution pipeline based on configuration."""
        pass
```

### 4. Pipeline Architecture

```python
from abc import ABC, abstractmethod
from typing import List, Optional, AsyncIterator

class PipelineStage(ABC):
    """Base class for pipeline stages."""

    @abstractmethod
    async def execute(
        self,
        request: QueryRequest,
        context: PipelineContext
    ) -> PipelineContext:
        """Execute the stage."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Stage name."""
        pass

@dataclass
class PipelineContext:
    """Context passed between pipeline stages."""
    request: QueryRequest
    schema: Optional[DatabaseSchema] = None
    abstraction: Optional[AbstractionResult] = None
    generation: Optional[SQLGenerationResult] = None
    reconstruction: Optional[ReconstructionResult] = None
    metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}

class MaskSQLPipeline:
    """Execution pipeline for MaskSQL."""

    def __init__(self, config: MaskSQLConfig):
        self.config = config
        self.stages: List[PipelineStage] = []

    def add_stage(self, stage: PipelineStage) -> "MaskSQLPipeline":
        """Add a stage to the pipeline (builder pattern)."""
        self.stages.append(stage)
        return self

    async def execute(self, request: QueryRequest) -> QueryResult:
        """Execute the complete pipeline."""
        context = PipelineContext(request=request)

        for stage in self.stages:
            logger.debug(f"Executing stage: {stage.name}")
            context = await stage.execute(request, context)

        return self._context_to_result(context)

    async def execute_stream(
        self,
        request: QueryRequest
    ) -> AsyncIterator[PipelineEvent]:
        """Execute pipeline with streaming events."""
        context = PipelineContext(request=request)

        for stage in self.stages:
            yield PipelineEvent(
                type="stage_start",
                stage=stage.name,
                timestamp=datetime.now()
            )

            context = await stage.execute(request, context)

            yield PipelineEvent(
                type="stage_complete",
                stage=stage.name,
                data=context,
                timestamp=datetime.now()
            )

        yield PipelineEvent(
            type="complete",
            data=self._context_to_result(context),
            timestamp=datetime.now()
        )

    def _context_to_result(self, context: PipelineContext) -> QueryResult:
        """Convert pipeline context to query result."""
        pass
```

### 5. Built-in Pipeline Stages

```python
class AbstractionStage(PipelineStage):
    """Abstraction stage implementation."""

    def __init__(self, config: MaskSQLConfig):
        self.config = config
        self.schema_filter = SchemaFilter(config.schema_filter)
        self.value_detector = ValueDetector(config.models.slm_model)
        self.value_linker = ValueLinker(config.models.slm_model)
        self.schema_linker = SchemaLinker(config.models.slm_model)
        self.symbol_generator = SymbolGenerator()

    async def execute(
        self,
        request: QueryRequest,
        context: PipelineContext
    ) -> PipelineContext:
        """Execute abstraction."""
        # 1. Load and filter schema
        schema = await self._load_schema(request.db_id)
        filtered_schema = await self.schema_filter.filter(
            question=request.question,
            schema=schema
        )

        # 2. Detect values
        values = await self.value_detector.detect(
            question=request.question,
            schema=filtered_schema
        )

        # 3. Link values to columns
        value_links = await self.value_linker.link(
            question=request.question,
            values=values,
            schema=filtered_schema
        )

        # 4. Link schema references
        schema_links = await self.schema_linker.link(
            question=request.question,
            values=values,
            schema=filtered_schema
        )

        # 5. Generate symbols and abstract
        symbol_table = self.symbol_generator.generate(filtered_schema)
        abstract_question = self._abstract_question(
            question=request.question,
            schema_links=schema_links,
            value_links=value_links,
            symbol_table=symbol_table
        )
        abstract_schema = self._abstract_schema(
            schema=filtered_schema,
            symbol_table=symbol_table
        )

        # Update context
        context.schema = filtered_schema
        context.abstraction = AbstractionResult(
            abstract_question=abstract_question,
            abstract_schema=abstract_schema,
            symbol_table=symbol_table,
            masked_terms=[],  # Populate from links
            schema_links=schema_links,
            value_links=value_links
        )

        return context

    @property
    def name(self) -> str:
        return "Abstraction"

    def _abstract_question(self, ...) -> str:
        """Create abstract question."""
        pass

    def _abstract_schema(self, ...) -> Dict[str, Any]:
        """Create abstract schema."""
        pass

class SQLGenerationStage(PipelineStage):
    """SQL generation stage implementation."""

    def __init__(
        self,
        config: MaskSQLConfig,
        enable_self_correction: bool = True
    ):
        self.config = config
        self.llm = LLMClient(config.models.llm_model)
        self.enable_self_correction = enable_self_correction

    async def execute(
        self,
        request: QueryRequest,
        context: PipelineContext
    ) -> PipelineContext:
        """Execute SQL generation."""
        if not context.abstraction:
            raise ValueError("Abstraction result required")

        # Generate SQL
        prompt = self._build_prompt(context.abstraction)
        abstract_sql = await self.llm.generate(prompt)

        corrected_sql = None
        if self.enable_self_correction:
            correction_prompt = self._build_correction_prompt(
                context.abstraction,
                abstract_sql
            )
            corrected_sql = await self.llm.generate(correction_prompt)

        context.generation = SQLGenerationResult(
            abstract_sql=abstract_sql,
            corrected_abstract_sql=corrected_sql
        )

        return context

    @property
    def name(self) -> str:
        return "SQLGeneration"

class ReconstructionStage(PipelineStage):
    """Reconstruction stage implementation."""

    def __init__(
        self,
        config: MaskSQLConfig,
        enable_repair: bool = True
    ):
        self.config = config
        self.slm = LLMClient(config.models.slm_model)
        self.executor = SQLExecutor(config.database_path)
        self.enable_repair = enable_repair

    async def execute(
        self,
        request: QueryRequest,
        context: PipelineContext
    ) -> PipelineContext:
        """Execute reconstruction."""
        if not context.generation or not context.abstraction:
            raise ValueError("Generation and abstraction results required")

        # Get final abstract SQL (corrected or original)
        abstract_sql = (
            context.generation.corrected_abstract_sql
            or context.generation.abstract_sql
        )

        # Reconstruct concrete SQL
        symbol_table = context.abstraction.symbol_table
        concrete_sql = self._reconstruct_sql(abstract_sql, symbol_table)

        # Execute
        exec_result, exec_error = await self.executor.execute(
            sql=concrete_sql,
            db_id=request.db_id
        )

        # Repair if enabled and execution failed
        repaired_sql = None
        if self.enable_repair and exec_error:
            repair_prompt = self._build_repair_prompt(
                question=request.question,
                schema=context.schema,
                sql=concrete_sql,
                error=exec_error,
                exec_result=exec_result
            )
            repaired_sql = await self.slm.generate(repair_prompt)

            # Re-execute
            exec_result, exec_error = await self.executor.execute(
                sql=repaired_sql,
                db_id=request.db_id
            )

        context.reconstruction = ReconstructionResult(
            concrete_sql=concrete_sql,
            repaired_sql=repaired_sql,
            execution_result=exec_result,
            execution_error=exec_error
        )

        return context

    @property
    def name(self) -> str:
        return "Reconstruction"

    def _reconstruct_sql(self, abstract_sql: str, symbol_table: Dict) -> str:
        """Restore concrete SQL from abstract SQL using symbol table."""
        pass
```

---

## Privacy Policy Configuration

### Predefined Policies

```python
# Full Policy (ΨF)
policy = PrivacyPolicy.FULL
# Masks: All tables, columns, and values

# Category Policy (ΨC)
policy = PrivacyPolicy.CATEGORY
# Masks: Only tokens matching specific semantic categories

# Minimal Policy
policy = PrivacyPolicy.MINIMAL
# Masks: Only PII (names, SSN, emails, etc.)
```

### Custom Policy Example

```python
from masksql import CustomPrivacyPolicy

custom_policy = CustomPrivacyPolicy(
    mask_tables=True,
    mask_columns=True,
    mask_values=True,

    # Specify semantic categories to mask
    categories=[
        "person_name",
        "location",
        "medical_condition",
        "financial_info"
    ],

    # Whitelist specific elements
    table_whitelist=["public_stats"],
    column_whitelist=["id", "created_at"],

    # Regex patterns for value masking
    value_patterns=[
        r"\d{3}-\d{2}-\d{4}",  # SSN
        r"\b[A-Z][a-z]+ [A-Z][a-z]+\b"  # Names
    ]
)

masksql = MaskSQL(
    privacy_policy=PrivacyPolicy.CUSTOM,
    custom_policy=custom_policy
)
```

---

## Usage Examples

### Example 1: Basic Usage

```python
import asyncio
from masksql import MaskSQL, PrivacyPolicy

async def main():
    # Initialize
    masksql = MaskSQL(
        llm_model="openai/gpt-4.1",
        slm_model="qwen/qwen2.5-7b-instruct",
        database_path="./databases",
        privacy_policy=PrivacyPolicy.FULL
    )

    # Execute query
    result = await masksql.query(
        question="How many patients were admitted in 2023?",
        db_id="hospital_db"
    )

    # Access results
    print(f"Generated SQL: {result.sql}")
    print(f"Execution Result: {result.execution_result}")
    print(f"Execution Accuracy: {result.execution_accuracy}")
    print(f"Masking Recall: {result.metrics.masking_recall}")
    print(f"Re-identification Score: {result.metrics.reidentification_score}")
    print(f"Total Latency: {result.performance.total_latency_ms}ms")
    print(f"Total Tokens: {result.performance.total_tokens}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: Configuration from File

```yaml
# config.yaml
database_path: "./databases"
privacy_policy: "category"

models:
  llm_model: "openai/gpt-4.1"
  slm_model: "qwen/qwen2.5-7b-instruct"
  llm_temperature: 0.0
  slm_temperature: 0.0
  max_tokens: 2048

schema_filter:
  use_resdsql: true
  top_k_tables: 4
  top_j_columns: 5

pipeline:
  enable_schema_filtering: true
  enable_value_linking: true
  enable_sql_correction: true
  enable_sql_repair: true
  enable_attack_simulation: false
  max_retries: 3
  cache_enabled: true

custom_policy:
  categories:
    - person_name
    - location
    - occupation
```

```python
from masksql import MaskSQL

async def main():
    masksql = MaskSQL.from_config("config.yaml")
    result = await masksql.query(
        question="List all doctors in New York",
        db_id="hospital_db"
    )
    print(result.sql)

asyncio.run(main())
```

### Example 3: Batch Processing

```python
from masksql import MaskSQL, QueryRequest
import pandas as pd

async def main():
    masksql = MaskSQL.from_config("config.yaml")

    # Load queries from CSV
    df = pd.read_csv("queries.csv")
    queries = [
        QueryRequest(
            question=row["question"],
            db_id=row["db_id"]
        )
        for _, row in df.iterrows()
    ]

    # Process in batch
    results = await masksql.query_batch(
        queries,
        max_concurrency=10,
        show_progress=True
    )

    # Analyze results
    successful = sum(1 for r in results if r.execution_error is None)
    avg_accuracy = sum(r.execution_accuracy or 0 for r in results) / len(results)
    avg_privacy = sum(r.metrics.masking_recall for r in results) / len(results)

    print(f"Success Rate: {successful/len(results):.2%}")
    print(f"Avg Accuracy: {avg_accuracy:.2%}")
    print(f"Avg Privacy: {avg_privacy:.2%}")

asyncio.run(main())
```

### Example 4: Streaming Mode

```python
from masksql import MaskSQL

async def main():
    masksql = MaskSQL(
        llm_model="openai/gpt-4.1",
        slm_model="qwen/qwen2.5-7b-instruct"
    )

    async for event in masksql.query_stream(
        question="How many patients?",
        db_id="hospital_db"
    ):
        if event.type == "stage_start":
            print(f"Starting: {event.stage}")
        elif event.type == "stage_complete":
            print(f"Completed: {event.stage}")
            if event.stage == "Abstraction":
                ctx = event.data
                print(f"  Abstract Q: {ctx.abstraction.abstract_question}")
        elif event.type == "complete":
            result = event.data
            print(f"Final SQL: {result.sql}")

asyncio.run(main())
```

### Example 5: Evaluation on Dataset

```python
from masksql import MaskSQL

async def main():
    masksql = MaskSQL.from_config("config.yaml")

    # Run evaluation
    report = await masksql.evaluate(
        dataset_path="bird_dev.json",
        output_path="results/evaluation.json",
        metrics=["accuracy", "privacy", "efficiency"]
    )

    print(report.summary())
    # Output:
    # Execution Accuracy: 55.66%
    # Masking Recall: 61.36%
    # Re-identification Score: 75.47%
    # Avg Latency: 12.3s
    # Avg Tokens: 6114

asyncio.run(main())
```

### Example 6: Custom Pipeline

```python
from masksql import (
    MaskSQLPipeline,
    AbstractionStage,
    SQLGenerationStage,
    ReconstructionStage,
    MaskSQLConfig,
    PrivacyPolicy
)

async def main():
    config = MaskSQLConfig(
        database_path="./databases",
        privacy_policy=PrivacyPolicy.FULL
    )

    # Build custom pipeline
    pipeline = MaskSQLPipeline(config)
    pipeline.add_stage(AbstractionStage(config))
    pipeline.add_stage(SQLGenerationStage(
        config,
        enable_self_correction=True
    ))
    pipeline.add_stage(ReconstructionStage(
        config,
        enable_repair=True
    ))

    # Execute
    from masksql import QueryRequest
    request = QueryRequest(
        question="How many patients?",
        db_id="hospital_db"
    )

    result = await pipeline.execute(request)
    print(result.sql)

asyncio.run(main())
```

---

## Refactoring Tasks

### Phase 1: Core modules

#### 1.1 Configuration System
**Priority: High**

- [ ] Create `MaskSQLConfig` dataclass with full configuration hierarchy
- [ ] Implement `from_yaml()` and `from_dict()` loaders
- [ ] Add Pydantic models for validation
- [ ] Create `PrivacyPolicy` enum and `CustomPrivacyPolicy` class
- [ ] Migrate from environment variables to structured config
- [ ] Add configuration validation and error messages

**Files to create:**
- `src/masksql/config/models.py`
- `src/masksql/config/loader.py`
- `src/masksql/config/validator.py`
- `src/masksql/config/__init__.py`

**Files to refactor:**
- `config.py` → migrate to new structure
- `main.py` → use new config system

#### 1.2 Data Models
**Priority: High**

- [ ] Create `QueryRequest` dataclass
- [ ] Create `QueryResult` dataclass with nested results
- [ ] Create `AbstractionResult`, `SQLGenerationResult`, `ReconstructionResult`
- [ ] Create `PrivacyMetrics` and `PerformanceMetrics`
- [ ] Add serialization methods (`to_dict()`, `to_json()`, `from_dict()`)
- [ ] Add Pydantic validators

**Files to create:**
- `src/masksql/models/request.py`
- `src/masksql/models/result.py`
- `src/masksql/models/metrics.py`
- `src/masksql/models/__init__.py`

#### 1.3 Exception Hierarchy
**Priority: Medium**

- [ ] Create `MaskSQLException` base class
- [ ] Create specific exceptions:
  - `ConfigurationError`
  - `SchemaNotFoundError`
  - `AbstractionError`
  - `SQLGenerationError`
  - `ExecutionError`
  - `ValidationError`
- [ ] Add exception handling throughout codebase

**Files to create:**
- `src/masksql/exceptions.py`

### Phase 2: Pipeline Refactoring

#### 2.1 Abstract Pipeline Components
**Priority: High**

- [ ] Create `PipelineStage` abstract base class
- [ ] Create `PipelineContext` dataclass
- [ ] Refactor `MaskSQLPipeline` to use new abstractions
- [ ] Add streaming support (`execute_stream()`)
- [ ] Implement builder pattern for pipeline construction
- [ ] Add stage-level error handling and retry logic

**Files to create:**
- `src/masksql/pipeline/stage.py`
- `src/masksql/pipeline/context.py`
- `src/masksql/pipeline/pipeline.py`
- `src/masksql/pipeline/events.py`

**Files to refactor:**
- `src/pipe/pipeline.py` → new architecture
- `src/pipe/processor/list_processor.py` → adapt to `PipelineStage`

#### 2.2 Implement Core Stages
**Priority: High**

- [ ] Refactor `AbstractionStage`:
  - Extract schema filtering logic
  - Extract value detection logic
  - Extract linking logic
  - Extract symbol generation logic
- [ ] Refactor `SQLGenerationStage`:
  - Simplify prompt generation
  - Add self-correction logic
  - Improve error handling
- [ ] Refactor `ReconstructionStage`:
  - Improve symbol restoration
  - Add SQL repair logic
  - Improve execution handling

**Files to refactor:**
- All files in `src/pipe/` → new stage architecture

#### 2.3 Component Extraction
**Priority: Medium**

- [ ] Extract `SchemaFilter` component
  - Support RESDSQL and custom rankers
  - Make filtering optional
- [ ] Extract `ValueDetector` component
- [ ] Extract `ValueLinker` component
- [ ] Extract `SchemaLinker` component
- [ ] Extract `SymbolGenerator` component
- [ ] Extract `SQLExecutor` component

**Files to create:**
- `src/masksql/components/schema_filter.py`
- `src/masksql/components/value_detector.py`
- `src/masksql/components/linker.py`
- `src/masksql/components/symbol_generator.py`
- `src/masksql/components/executor.py`

### Phase 3: Public API

#### 3.1 Main MaskSQL Class
**Priority: High**

- [ ] Implement `MaskSQL` main class
- [ ] Implement `query()` method
- [ ] Implement `query_batch()` method
- [ ] Implement `query_stream()` method
- [ ] Implement `evaluate()` method
- [ ] Implement `from_config()` class method
- [ ] Add comprehensive docstrings and type hints

**Files to create:**
- `src/masksql/api.py`
- `src/masksql/__init__.py`

#### 3.2 Convenience Functions
**Priority: Medium**

- [ ] Create `masksql.query()` function (module-level)
- [ ] Create `masksql.query_batch()` function
- [ ] Create `masksql.evaluate()` function
- [ ] Add preset configurations (defaults for common use cases)

**Files to update:**
- `src/masksql/__init__.py`

### Phase 4: LLM Integration

#### 4.1 Unified LLM Client
**Priority: High**

- [ ] Create `LLMClient` abstract class
- [ ] Implement OpenAI client
- [ ] Implement OpenRouter client
- [ ] Add support for other providers (Anthropic, local models)
- [ ] Add retry logic with exponential backoff
- [ ] Add rate limiting
- [ ] Add token counting
- [ ] Add caching layer

**Files to create:**
- `src/masksql/llm/client.py`
- `src/masksql/llm/providers/openai.py`
- `src/masksql/llm/providers/openrouter.py`
- `src/masksql/llm/cache.py`
- `src/masksql/llm/retry.py`

**Files to refactor:**
- `src/pipe/llm_util.py` → migrate to new client

#### 4.2 Prompt Management
**Priority: Medium**

- [ ] Create `PromptTemplate` class
- [ ] Centralize all prompts in one location
- [ ] Support prompt versioning
- [ ] Add prompt validation
- [ ] Support custom prompts via config

**Files to create:**
- `src/masksql/prompts/templates.py`
- `src/masksql/prompts/loader.py`

**Files to refactor:**
- All prompt files in `src/pipe/*_prompts/` → centralize

### Phase 5: Database & Schema

#### 5.1 Schema Management
**Priority: High**

- [ ] Refactor `DatabaseSchemaRepo`
- [ ] Support multiple schema formats (YAML, JSON, SQL)
- [ ] Add schema validation
- [ ] Add schema caching
- [ ] Support dynamic schema loading

**Files to refactor:**
- `src/pipe/schema_repo.py`

**Files to create:**
- `src/masksql/schema/repository.py`
- `src/masksql/schema/validator.py`
- `src/masksql/schema/loader.py`

#### 5.2 SQL Execution
**Priority: High**

- [ ] Create `SQLExecutor` class
- [ ] Support multiple database types (SQLite, PostgreSQL, MySQL)
- [ ] Add connection pooling
- [ ] Add query timeout
- [ ] Add result formatting
- [ ] Add error handling

**Files to create:**
- `src/masksql/execution/executor.py`
- `src/masksql/execution/connection.py`

**Files to refactor:**
- `src/pipe/exec_conc_sql.py` → new executor

### Phase 6: Privacy & Evaluation

#### 6.1 Privacy Policies
**Priority: High**

- [ ] Implement `FullPolicy` (ΨF)
- [ ] Implement `CategoryPolicy` (ΨC)
- [ ] Implement `MinimalPolicy`
- [ ] Implement `CustomPolicy` with rules engine
- [ ] Add category detection using NER/LLM
- [ ] Add policy validation

**Files to create:**
- `src/masksql/privacy/policy.py`
- `src/masksql/privacy/category_detector.py`
- `src/masksql/privacy/validator.py`

#### 6.2 Metrics & Evaluation
**Priority: Medium**

- [ ] Implement `MaskingRecall` metric
- [ ] Implement `ReidentificationScore` metric
- [ ] Implement `ExecutionAccuracy` metric
- [ ] Implement attack simulation
- [ ] Create evaluation framework
- [ ] Add reporting (console, JSON, HTML)

**Files to create:**
- `src/masksql/evaluation/metrics.py`
- `src/masksql/evaluation/attack.py`
- `src/masksql/evaluation/reporter.py`

### Phase 7: Testing & Documentation

#### 7.1 Unit Tests
**Priority: High**

- [ ] Unit tests for configuration system
- [ ] Unit tests for data models
- [ ] Unit tests for pipeline stages
- [ ] Unit tests for components
- [ ] Unit tests for LLM client
- [ ] Unit tests for privacy policies
- [ ] Unit tests for evaluation metrics
- [ ] Achieve 80%+ code coverage

**Files to create:**
- `tests/unit/test_config.py`
- `tests/unit/test_models.py`
- `tests/unit/test_pipeline.py`
- `tests/unit/test_stages.py`
- `tests/unit/test_components.py`
- `tests/unit/test_llm.py`
- `tests/unit/test_privacy.py`
- `tests/unit/test_evaluation.py`

#### 7.2 Integration Tests
**Priority: High**

- [ ] End-to-end pipeline tests
- [ ] Batch processing tests
- [ ] Streaming tests
- [ ] Error handling tests
- [ ] Performance tests

**Files to create:**
- `tests/integration/test_e2e.py`
- `tests/integration/test_batch.py`
- `tests/integration/test_streaming.py`

#### 7.3 Documentation
**Priority: High**

- [ ] API reference documentation
- [ ] User guide with examples
- [ ] Configuration guide
- [ ] Privacy policy guide
- [ ] Developer guide for extending

**Files to create:**
- `docs/api/index.rst`
- `docs/user_guide/quickstart.md`
- `docs/user_guide/configuration.md`
- `docs/user_guide/privacy_policies.md`
- `docs/developer_guide/extending.md`
- `docs/migration.md`

### Phase 8: Performance & Production

#### 8.1 Performance Optimization
**Priority: Medium**

- [ ] Add caching layer (LRU cache for schema, prompts)
- [ ] Implement connection pooling for databases
- [ ] Add batch LLM requests where possible
- [ ] Optimize symbol table operations
- [ ] Add profiling instrumentation

**Files to create:**
- `src/masksql/cache/manager.py`
- `src/masksql/performance/profiler.py`

#### 8.2 Monitoring & Logging
**Priority: Medium**

- [ ] Structured logging with loguru
- [ ] Add telemetry (OpenTelemetry support)
- [ ] Add metrics collection (Prometheus format)
- [ ] Add health check endpoint
- [ ] Add debug mode with detailed tracing

**Files to create:**
- `src/masksql/monitoring/telemetry.py`
- `src/masksql/monitoring/metrics.py`
- `src/masksql/monitoring/logging.py`

#### 8.3 Production Readiness
**Priority: Medium**

- [ ] Add Docker support
- [ ] Add CLI tool
- [ ] Add REST API wrapper (FastAPI)
- [ ] Add input validation and sanitization
- [ ] Add security best practices
- [ ] Add deployment guide

**Files to create:**
- `Dockerfile`
- `src/masksql/cli/main.py`
- `src/masksql/api/rest.py`
- `docs/deployment.md`

### Phase 9: Optional Enhancements (Future)

#### 9.1 Advanced Features
**Priority: Low**

- [ ] Multi-database support
- [ ] Query optimization suggestions
- [ ] Interactive debugging mode
- [ ] Web UI for testing
- [ ] Dataset versioning and management
- [ ] Fine-tuning support for SLMs
- [ ] Differential privacy integration

#### 9.2 Integrations
**Priority: Low**

- [ ] Integration with dbt
- [ ] Integration with SQLAlchemy
- [ ] Integration with Pandas
- [ ] Integration with LangChain
- [ ] Integration with observability tools

---

## Testing Strategy

### Unit Testing

```python
# tests/unit/test_masksql.py
import pytest
from masksql import MaskSQL, PrivacyPolicy, QueryRequest

@pytest.fixture
def masksql():
    return MaskSQL(
        llm_model="mock/gpt-4",
        slm_model="mock/qwen",
        database_path="tests/fixtures/databases"
    )

@pytest.mark.asyncio
async def test_query_basic(masksql, mock_llm):
    result = await masksql.query(
        question="How many patients?",
        db_id="test_db"
    )

    assert result.sql is not None
    assert result.execution_accuracy is not None
    assert result.metrics.masking_recall >= 0.0
    assert result.metrics.reidentification_score >= 0.0

@pytest.mark.asyncio
async def test_query_with_policy(masksql):
    masksql.config.privacy_policy = PrivacyPolicy.CATEGORY

    result = await masksql.query(
        question="List doctors in NYC",
        db_id="test_db"
    )

    assert result.abstraction is not None
    assert len(result.abstraction.masked_terms) > 0
```

### Integration Testing

```python
# tests/integration/test_e2e.py
import pytest
from masksql import MaskSQL

@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_pipeline():
    masksql = MaskSQL.from_config("tests/fixtures/test_config.yaml")

    result = await masksql.query(
        question="What is the average salary of engineers?",
        db_id="company_db"
    )

    # Verify all stages completed
    assert result.abstraction is not None
    assert result.generation is not None
    assert result.reconstruction is not None

    # Verify SQL is valid
    assert result.sql.upper().startswith("SELECT")

    # Verify execution
    assert result.execution_result is not None or result.execution_error is not None

    # Verify metrics
    assert result.metrics.masking_recall >= 0.0
    assert result.performance.total_latency_ms > 0
```

---
