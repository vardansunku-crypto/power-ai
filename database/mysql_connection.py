from sqlalchemy import create_engine, inspect


def get_mysql_engine(
    mysql_user,
    mysql_password,
    mysql_host,
    mysql_port,
    selected_db
):
    engine = create_engine(
        f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{selected_db}"
    )

    return engine


def get_database_schema(engine):
    schema_text = ""

    inspector = inspect(engine)
    tables = inspector.get_table_names()

    for table in tables:
        columns = inspector.get_columns(table)

        column_names = []

        for column in columns:
            column_names.append(column["name"])

        schema_text += f"""
{table}(
    {", ".join(column_names)}
)
"""

    return schema_text
