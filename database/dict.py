from .db import engine
from sqlalchemy import text


def query_database(query_string):
    # Define the SQL query as a string using SQLAlchemy's text function
    query = text(query_string)

    # Connect to the database and execute the query
    with engine.connect() as connection:
        result = connection.execute(query)

        # Return the results of the query as a list of tuples
        return result.fetchall()
