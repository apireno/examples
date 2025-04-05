
from graph_examples.helpers.constants import * 
from graph_examples.helpers import loggers     
import tqdm
import numpy as np
import pandas as pd
import os
from surrealdb import Surreal
from graph_examples.helpers.params import DatabaseParams, SurrealParams
import datetime
import re


db_params = DatabaseParams()
args_loader = ArgsLoader("Input Glove embeddings model",db_params)
FIELD_MAPPING = [
{"dataframe_field_name": "FilingID", "field_display_name": "Filing ID", "surql_field_name": "filing_id", "python_type": int},
{"dataframe_field_name": "1D", "field_display_name": "SEC#", "surql_field_name": "sec_number", "python_type": str},
{"dataframe_field_name": "Execution Type", "field_display_name": "Execution Type", "surql_field_name": "execution_type", "python_type": str},
{"dataframe_field_name": "Execution Date", "field_display_name": "Execution Date", "surql_field_name": "execution_date", "python_type": datetime},
{"dataframe_field_name": "Signatory", "field_display_name": "Signatory", "surql_field_name": "signatory_name", "python_type": str},
{"dataframe_field_name": "Title", "field_display_name": "Signatory Title", "surql_field_name": "signitory_title", "python_type": str},
]


def insert_data_into_surrealdb(logger,connection:Surreal,data):
    """
    Inserts data into SurrealDB.

    Args:
        data: The data to be inserted.
    """
    insert_surql = """ 
    fn::filing_upsert(
        $filing_id,
        $sec_number,
        $execution_type,
        $execution_date,
        $signatory_name,
        $signitory_title)
    """


    params = {
        "filing_id": data["filing_id"],
        "sec_number": data["sec_number"],
        "execution_type": data["execution_type"],
        "execution_date": data["execution_date"],
        "signatory_name": data["signatory_name"],
        "signitory_title": data["signitory_title"],
        }

    try:
        SurrealParams.ParseResponseForErrors(connection.query_raw(
            insert_surql,params=params
        ))
    except Exception as e:
        logger.error(f"Error inserting data into SurrealDB: {data}")
        raise




def insert_dataframe_into_database(logger,connection:Surreal,df):
    """
    Extracts specified fields from a pandas DataFrame and returns an array of objects.

    Args:
        df: The pandas DataFrame.
        field_mapping: An array of objects, where each object has "field_display_name" and "dataframe_field_name".
    Returns:
        An array of objects, where each object contains the extracted field values.
    """
    if df is not None and not df.empty:
        for index, row in tqdm.tqdm(df.iterrows(), desc="Processing rows", total=len(df), unit="row",position=2):
            row_data = get_parsed_data_from_field_mapping(row, FIELD_MAPPING)
            insert_data_into_surrealdb(logger,connection,row_data)
            
def process_excel_file_and_extract(logger,connection:Surreal,filepath):
    """
    Processes an Excel file, extracts specified fields, and returns an array of objects.

    Args:
        filepath: The path to the Excel file.
        field_mapping: An array of objects, where each object has "field_display_name" and "dataframe_field_name".

    Returns:
        An array of objects, or None if an error occurs.
    """
    encoding_hint = get_file_encoding(filepath)  # Get the encoding hint
    # Prioritize latin1/ISO-8859-1
    encodings_to_try = ['iso-8859-1', encoding_hint]  # Try iso-8859-1 first

    df = None
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(filepath, encoding=enc, encoding_errors='replace')  # Use errors='replace'
            #if enc != encoding_hint:
            #    logger.warning(f"Successfully read {filepath} using {enc} instead of {encoding_hint}.")
            break  # If successful, stop trying other encodings
        except UnicodeDecodeError:
            logger.warning(f"UnicodeDecodeError for {filepath} with {enc}.")
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing {filepath}: {e}")
            break  # Stop trying if a different error occurs

    if df is not None:
        df = df.replace([np.nan], [None])
        insert_dataframe_into_database(logger,connection,df)
    

def process_filings():

    logger = loggers.setup_logger("SurrealProcessFilings")
    args_loader.LoadArgs() # Parse command-line arguments
    logger.info(args_loader.string_to_print())

    with Surreal(db_params.DB_PARAMS.url) as connection:
        logger.info("Connected to SurrealDB")
        connection.signin({"username": db_params.DB_PARAMS.username, "password": db_params.DB_PARAMS.password})
        connection.use(db_params.DB_PARAMS.namespace, db_params.DB_PARAMS.database)

        logger.info(f"Processing part 1 adv base a firms data in directory {PART1_DIR}")

        file_pattern = re.compile(r"^IA_ADV_Base_A_.*\.csv$")

        matching_files = [
            filename
            for filename in os.listdir(PART1_DIR)
            if file_pattern.match(filename)
        ]

        for filename in tqdm.tqdm(matching_files, desc="Processing files", unit="file",position=1):
            filepath = os.path.join(PART1_DIR, filename)
            process_excel_file_and_extract(logger,connection,filepath)
            
            

# --- Main execution block ---
if __name__ == "__main__":
    process_filings()
# --- End main execution block ---