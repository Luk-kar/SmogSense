# Python
from pathlib import Path


# SQLAlchemy
from sqlalchemy import text

# Commmon
from common.utils.database.session_handling import get_database_session


def load_sql_query(file_path: Path) -> str:
    """Reads and returns the content of an SQL file."""
    with file_path.open("r", encoding="utf-8") as f:
        return f.read()


def get_module_path(module):
    """Returns the absolute path of a given module."""

    module_dir = Path(module.__file__).parent

    if not module_dir.is_dir():
        raise NotADirectoryError(f"The path {module_dir} is not a directory.")

    return module_dir


def execute_sql_view_creation(context, sql_path):
    query = load_sql_query(sql_path)

    with get_database_session(context) as session:
        try:
            context.log.info(f"Executing SQL file: {sql_path.name}")
            session.execute(text(query))
            session.commit()

            # Select the name of the executed file and log it
            table_name, extension = sql_path.name.split(".")
            check_up_query = f"SELECT * FROM {table_name} LIMIT 10;"
            context.log.info(f"Checking the view with: {check_up_query}")
            result = session.execute(text(check_up_query))
            session.commit()

            # Log the outcome of the check-up query execution
            rows = result.fetchall()
            if rows:

                log_query_results(context, result, rows)

            else:
                context.log.warning("Check-up query returned no rows.")

            context.log.info(f"Successfully executed: {sql_path.name}")
        except Exception as e:
            session.rollback()
            context.log.error(f"Error executing {sql_path.name}: {str(e)}")
            raise


def log_query_results(context, result, rows):
    """Logs the outcome of the check-up query execution."""

    header = result.keys()

    # Convert rows to strings and get column headers
    str_header = [str(col) for col in header]
    str_rows = [[str(cell) for cell in row] for row in rows]

    # Calculate column widths
    col_widths = [
        max(len(str_header[i]), max(len(row[i]) for row in str_rows))
        for i in range(len(str_header))
    ]

    # Create format string for table rows
    row_format = " | ".join([f"{{:<{width}}}" for width in col_widths])

    # Build table components
    separator = "-+-".join(["-" * width for width in col_widths])
    table_header = row_format.format(*str_header)
    table_rows = [row_format.format(*row) for row in str_rows]

    # Combine into final table
    rendered_table = f"\n{table_header}\n" f"{separator}\n" + "\n".join(table_rows)

    context.log.info(f"Check-up query returned {len(rows)} rows:\n{rendered_table}")
