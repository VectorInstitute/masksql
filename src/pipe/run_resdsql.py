"""Execute RESDSQL pipeline for schema filtering."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from src.pipe.processor.list_processor import JsonListProcessor
from src.pipe.util_processors import InitData
from src.utils.json_io import write_json
from src.utils.logging import console, log_error, log_success, logger


class RunResdsql(JsonListProcessor[InitData.Model, InitData.Model]):
    """
    Execute RESDSQL pipeline to generate schema predictions.

    This stage runs the complete RESDSQL pipeline which includes:
    1. Table transformation (NatSQL preprocessing)
    2. Dataset preprocessing
    3. Schema item classification (ML model)
    4. Text2SQL data generation
    5. Question ID alignment

    The input dataset is automatically taken from the previous pipeline stage
    (e.g., the output of LimitJson).

    Parameters
    ----------
    tables_path : str
        Path to tables JSON file
    db_path : str
        Path to databases directory
    output_path : str
        Path to output RESDSQL predictions file
    device : str, optional
        Device to use for inference (cpu, cuda, mps). Defaults to cpu.
    """

    tables_path: Path
    db_path: Path
    device: str
    resd_dir: Path
    resdsql_dir: Path
    python_exe: Any
    resd_input_path: Path
    resd_output_path: Path

    async def _process_row(self, row: InitData.Model) -> InitData.Model:
        """Pass through data unchanged - processing happens in RESDSQL."""
        return row

    def __init__(
        self,
        tables_path: str,
        db_path: str,
        output_path: str,
        device: str = "cpu",
    ) -> None:
        super().__init__(InitData.Model,force=False)
        self.tables_path = Path(tables_path).absolute()
        self.db_path = Path(db_path).absolute()
        self.resd_output_path = Path(output_path).absolute()
        self.device = device
        self.resd_dir = self.resd_output_path.parent / "resd"
        self.resdsql_dir = Path("resdsql").absolute()
        self.python_exe = sys.executable
        self.resd_input_path = self.resd_output_path.parent / "resd_input.json"

    async def run(self, input_data: list[InitData.Model]) -> list[InitData.Model]:
        """
        Override run to capture the input file from the pipeline.

        Parameters
        ----------
        input_file : str
            Path to input file from previous pipeline stage (e.g., LimitJson output)

        Returns
        -------
        str
            Path to output file
        """
        # Store the actual input from the pipeline (e.g., 2_LimitJson.json)
        write_json(str(self.resd_input_path), input_data)
        return input_data

    def _run_step(self, step_name: str, script: str, args: list[str]) -> None:
        """
        Run a single RESDSQL pipeline step.

        Parameters
        ----------
        step_name : str
            Human-readable name of the step
        script : str
            Path to Python script to run
        args : list[str]
            Command-line arguments for the script
        """
        cmd = [self.python_exe, script, *args]
        logger.info(f"  Running: [dim]{script}[/dim]")

        # Pass current environment to subprocess
        env = os.environ.copy()

        result = subprocess.run(
            cmd,
            cwd=str(self.resdsql_dir),
            capture_output=True,
            text=True,
            check=False,
            env=env,
        )

        if result.returncode != 0:
            log_error(
                f"RESDSQL step failed: {step_name}",
                script=script,
                exit_code=result.returncode,
                stderr=result.stderr[:500] if result.stderr else "No error output",
            )
            raise RuntimeError(f"RESDSQL step '{step_name}' failed")

        # Log output at debug level
        if result.stdout:
            logger.debug(f"STDOUT: {result.stdout}")

    def _table_transform(self) -> None:
        """Step 1: Transform tables for NatSQL compatibility."""
        console.print("[bold cyan]  → Table transformation[/bold cyan]")
        self._run_step(
            "table_transform",
            "NatSQL/table_transform.py",
            [
                "--in_file",
                str(self.tables_path),
                "--out_file",
                str(self.resd_dir / "test_tables_for_natsql.json"),
                "--correct_col_type",
                "--remove_start_table",
                "--analyse_same_column",
                "--table_transform",
                "--correct_primary_keys",
                "--use_extra_col_types",
                "--db_path",
                str(self.db_path),
            ],
        )

    def _preprocess_dataset(self) -> None:
        """Step 2: Preprocess input dataset."""
        console.print("[bold cyan]  → Dataset preprocessing[/bold cyan]")
        self._run_step(
            "preprocessing",
            "preprocessing.py",
            [
                "--mode",
                "test",
                "--table_path",
                str(self.tables_path),
                "--input_dataset_path",
                str(self.resd_input_path),
                "--output_dataset_path",
                str(self.resd_dir / "preprocessed_test.json"),
                "--db_path",
                str(self.db_path),
                "--target_type",
                "sql",
            ],
        )

    def _classify_schema_items(self) -> None:
        """Step 3: Run schema item classifier ML model."""
        console.print(
            f"[bold cyan]  → Schema classification[/bold cyan] [dim]({self.device})[/dim]"
        )
        model_path = Path("models/text2sql_schema_item_classifier").absolute()

        self._run_step(
            "schema_item_classifier",
            "schema_item_classifier.py",
            [
                "--batch_size",
                "32",
                "--device",
                self.device,
                "--seed",
                "42",
                "--save_path",
                str(model_path),
                "--dev_filepath",
                str(self.resd_dir / "preprocessed_test.json"),
                "--output_filepath",
                str(self.resd_dir / "test_with_probs.json"),
                "--use_contents",
                "--add_fk_info",
                "--mode",
                "test",
            ],
        )

    def _generate_text2sql_data(self) -> None:
        """Step 4: Generate text2sql data with ranked schema items."""
        console.print("[bold cyan]  → Text2SQL data generation[/bold cyan]")
        self._run_step(
            "text2sql_data_generator",
            "text2sql_data_generator.py",
            [
                "--input_dataset_path",
                str(self.resd_dir / "test_with_probs.json"),
                "--output_dataset_path",
                str(self.resd_dir / "resd_output_orig.json"),
                "--topk_table_num",
                "4",
                "--topk_column_num",
                "5",
                "--mode",
                "test",
                "--use_contents",
                "--add_fk_info",
                "--output_skeleton",
                "--target_type",
                "sql",
            ],
        )

    def _add_question_ids(self) -> None:
        """Step 5: Add question IDs from original input."""
        console.print("[bold cyan]  → Adding question IDs[/bold cyan]")
        self._run_step(
            "add_qid",
            "add_qid.py",
            [
                "--src",
                str(self.resd_input_path),
                "--dst",
                str(self.resd_dir / "resd_output_orig.json"),
                "--out",
                str(self.resd_output_path),
                "--prop",
                "question_id",
            ],
        )

    def _pre_run(self) -> None:
        """Execute RESDSQL pipeline before processing rows."""
        # Skip if RESDSQL output already exists and force is not enabled
        if not self.force and self.resd_output_path.exists():
            logger.info(
                f"[dim]⏭  Skipping RESDSQL pipeline - output exists:[/dim] "
                f"{self.resd_output_path.name}"
            )
            return

        # Set TORCH_DEVICE environment variable
        if "TORCH_DEVICE" not in os.environ:
            os.environ["TORCH_DEVICE"] = self.device

        # Create output directory
        self.resd_dir.mkdir(parents=True, exist_ok=True)

        console.print("[bold blue]Starting RESDSQL pipeline...[/bold blue]")

        try:
            # Execute pipeline steps
            self._table_transform()
            self._preprocess_dataset()
            self._classify_schema_items()
            self._generate_text2sql_data()
            self._add_question_ids()

            log_success(
                "RESDSQL pipeline completed",
                output_file=str(self.resd_output_path),
            )

        except Exception as e:
            log_error(f"RESDSQL pipeline failed: {e}")
            raise
