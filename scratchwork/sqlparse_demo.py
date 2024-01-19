import os
import sqlparse
import csv

def find_sql_files(directory):
    """Recursively find all SQL files in the given directory."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.sql'):
                yield os.path.join(root, file)

def process_tokens(tokens):
    """Process tokens to classify and extract information."""
    # This function needs to be implemented based on your specific needs
    tables = set()
    columns = set()
    comments = []
    for token in tokens:
        if token.ttype is sqlparse.tokens.Name:
            # Extract table or column names
            pass
        elif isinstance(token, sqlparse.sql.Comment):
            # Extract comments
            pass
    return tables, columns, comments

def parse_sql_file(file_path):
    """Parse a single SQL file."""
    with open(file_path) as f:
        sql_content = f.read()
    parsed = sqlparse.parse(sql_content)
    all_tables = set()
    all_columns = set()
    all_comments = []
    for statement in parsed:
        tables, columns, comments = process_tokens(statement.tokens)
        all_tables.update(tables)
        all_columns.update(columns)
        all_comments.extend(comments)
    return all_tables, all_columns, all_comments

def parse_sql_files_and_write_to_csv(directory, csv_file):
    """Parse SQL files and write extracted information to a CSV file."""
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['File Path', 'Tables', 'Columns', 'Comments'])
        for sql_file in find_sql_files(directory):
            writer.writerow([f"# FILEPATH: {sql_file}"])
            tables, columns, comments = parse_sql_file(sql_file)
            writer.writerow([sql_file, ', '.join(tables), ', '.join(columns), '; '.join(comments)])

# Directory containing SQL files
sql_directory = 'C:\Users\kylew\Source Path Digital\Client Resources - Documents'

# CSV file path
csv_output = 'output.csv'

# Parse SQL files and write to CSV
parse_sql_files_and_write_to_csv(sql_directory, csv_output)
