
from graph_examples.helpers.constants import * 
from graph_examples.helpers import loggers   
import pandas as pd
import os
from graph_examples.helpers.params import DatabaseParams
import re
import fasttext

FILING_FIELD_MAPPING = [
    {"dataframe_field_name": "FilingID", "field_display_name": "Filing ID", "surql_field_name": "filing_id", "python_type": int},
    {"dataframe_field_name": "1D", "field_display_name": "SEC#", "surql_field_name": "sec_number", "python_type": str},
    {"dataframe_field_name": "1A", "field_display_name": "Name", "surql_field_name": "name", "python_type": str},
    {"dataframe_field_name": "1B1", "field_display_name": "Legal Name", "surql_field_name": "legal_name", "python_type": str},
]

B_R_FIELD_MAPPING = [
    {
        "dataframe_field_name": "FilingID",
        "field_display_name": "Filing ID",
        "surql_field_name": "filing_id",
        "python_type": int,  # Assuming Filing ID is an integer
        "description": "Unique identifier for the filing.",
    },
    {
        "dataframe_field_name": "Name",
        "field_display_name": "Name",
        "surql_field_name": "name",
        "python_type": str,
        "description": "Name of the custodian holding books or records.",
    },
    {
        "dataframe_field_name": "Type",
        "field_display_name": "Type of Custodian",
        "surql_field_name": "type",
        "python_type": str,
        "description": "Nature of the custodian's relationship to the books or records.",
    },
    {
        "dataframe_field_name": "Description",
        "field_display_name": "Description",
        "surql_field_name": "description",
        "python_type": str,
        "description": "Description of the custodian's relationship to the books or records.",
    },
]


FILING_71b_FIELD_MAPPING = [
    {
        "dataframe_field_name": "FilingID",
        "field_display_name": "Filing ID",
        "surql_field_name": "filing_id",
        "python_type": int,  # Assuming FilingID is an integer
        "description": "Unique identifier for the filing.",
    },
    {
        "dataframe_field_name": "Fund Type",
        "field_display_name": "Fund Type",
        "surql_field_name": "fund_type",
        "python_type": str,
        "description": "Type of the fund (e.g., Hedge Fund).",
    },
    {
        "dataframe_field_name": "Fund Name",
        "field_display_name": "Fund Name",
        "surql_field_name": "fund_name",
        "python_type": str,
        "description": "Name of the fund.",
    },
    {
        "dataframe_field_name": "Master Fund Name",
        "field_display_name": "Master Fund Name",
        "surql_field_name": "master_fund_name",
        "python_type": str,
        "description": "Name of the master fund (if applicable).",
    },
]
FILING_53k_FIELD_MAPPING = [
    {
        "dataframe_field_name": "Filing ID",
        "field_display_name": "Filing ID",
        "surql_field_name": "filing_id",
        "python_type": int,  # Assuming Filing ID is an integer
        "description": "Unique identifier for the filing.",
    },
    {
        "dataframe_field_name": "5K(3)(a)",
        "field_display_name": "Legal name of custodian",
        "surql_field_name": "legal_name",
        "python_type": str,
        "description": "Legal name of the custodian holding separately managed account assets.",
    },
    {
        "dataframe_field_name": "5K(3)(b)",
        "field_display_name": "Primary business name of custodian",
        "surql_field_name": "primary_business_name",
        "python_type": str,
        "description": "Primary business name of the custodian holding separately managed account assets.",
    },
]


db_params = DatabaseParams()
args_loader = ArgsLoader("Generate fast text firm model",db_params)



def get_filing_5k3_df(logger):
    """
    Processes and returns a Pandas DataFrame from 5K3 filing data.

    Args:
        logger:  A logger object.

    Returns:
        A Pandas DataFrame.
    """
    logger.info(f"Processing 5k3_df {PART1_DIR}")

    
    file_pattern = re.compile(r"^IA_Schedule_D_5K3_.*\.csv$")

    matching_files = [
        filename
        for filename in os.listdir(PART1_DIR)
        if file_pattern.match(filename)
    ]
    
    filing_df = extract_csv_data(logger,matching_files)

    filing_df = filing_df.rename(
        columns={
            "5K(3)(b)": "name",
            "Filing ID": "filing_id",
            "5K(3)(a)": "legal_name",
        }
    )
    filing_df["fund_type"] = None  # Add fund_type column with None
    filing_df["master_fund_name"] = None 


    return filing_df





def filter_vc_hedge(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters a DataFrame to include only rows that meet the following criteria:
    - 'Fund Type' is 'Hedge Fund' or 'VC Fund' (case-insensitive)

    Args:
        df: The input pandas DataFrame.

    Returns:
        A new pandas DataFrame containing only the filtered rows.
    """

    # Ensure case-insensitive comparison and handle missing columns
    if 'Fund Type' in df.columns:
        fund_type_condition = df['Fund Type'].str.lower().isin(['venture capital fund', 'hedge fund'])
    else:
        fund_type_condition = pd.Series([False] * len(df))

    # Combine conditions using the OR operator
    combined_condition = fund_type_condition

    return df[combined_condition]
 

def get_filing_7b1_df(logger):
    """
    Processes and returns a Pandas DataFrame from 7B1 filing data.

     Args:
        logger:  A logger object.

    Returns:
        A Pandas DataFrame.
    """
    logger.info(f"Processing 7b1_df {PART1_DIR}")

    # Define regular expression patterns to identify relevant CSV files.
    
    file_pattern1 = re.compile(r"^IA_Schedule_D_7B1_.*\.csv$")
    file_pattern2 = re.compile(r"^ERA_Schedule_D_7B1_.*\.csv$")

    # Find all files in the directory that match either pattern.
    matching_files = [
        filename
        for filename in os.listdir(PART1_DIR)
        if file_pattern1.match(filename) or file_pattern2.match(filename)
    ]
    filing_df = extract_csv_data(logger,matching_files,filter_func=filter_vc_hedge)


    filing_df = filing_df.rename(
        columns={
            "Fund Name": "name",
            "FilingID": "filing_id",
            "Fund Type": "fund_type",
            "Master Fund Name": "master_fund_name",
        }
    )
    filing_df["legal_name"] = None
    return filing_df
        


def get_filing_b_r_df(logger):
    """
    Processes and returns a Pandas DataFrame from books and records filing data.

     Args:
        logger:  A logger object.

    Returns:
        A Pandas DataFrame.
    """
    logger.info(f"Processing b_r_df {PART1_DIR}")

    # Define regular expression patterns to identify relevant CSV files.
    
    
    # Define regular expression pattern to identify relevant CSV files.
    file_pattern = re.compile(r".*_Schedule_D_Books_and_Records_.*\.csv$")

    matching_files = [
        filename
        for filename in os.listdir(PART1_DIR)
        if file_pattern.match(filename)
    ]


    filing_df = extract_csv_data(logger,matching_files)


    filing_df = filing_df.rename(
        columns={
            "Name": "name",
            "FilingID": "filing_id",
            "Type": "fund_type"
        }
    )
    filing_df["legal_name"] = None
    filing_df["master_fund_name"] = None 
    return filing_df
        

def get_filing_firm_df(logger):
    """
    Processes and returns a Pandas DataFrame of firm filing data.

     Args:
        logger:  A logger object.

    Returns:
        A Pandas DataFrame.
    """
    logger.info("Getting filing firm dictionary")

    # Define regular expression patterns to identify relevant CSV files.
    file_pattern1 = re.compile(r"^IA_ADV_Base_A_.*\.csv$")
    file_pattern2 = re.compile(r"^ERA_ADV_Base_.*\.csv$")

    # Find all files in the directory that match either pattern.
    matching_files = [
        filename
        for filename in os.listdir(PART1_DIR)
        if file_pattern1.match(filename) or file_pattern2.match(filename)
    ]
    filing_df = extract_csv_data(logger,matching_files)

    filing_df = filing_df.rename(
        columns={
            "1A": "name",
            "FilingID": "filing_id",
            "1B1": "legal_name"
        }
    )
    filing_df["fund_type"] = "Registered"
    filing_df["master_fund_name"] = None 


    return filing_df 


def get_adv_firms_df(logger):
    """
    Processes and returns a concatenated Pandas DataFrame of investment advisor firms from Excel files.

     Args:
        logger:  A logger object.

    Returns:
        A Pandas DataFrame.
    """


    dfs: list[pd.DataFrame] = []  # List to store individual dataframes

    file_tqdm = tqdm.tqdm(os.listdir(INVESTMENT_ADVISER_FIRMS_DIR), desc="Processing Files", position=1)
    for filename in file_tqdm:
        file_tqdm.set_description(f"Processing {filename}")
        if filename.endswith(".xlsx"):
            filepath = os.path.join(INVESTMENT_ADVISER_FIRMS_DIR, filename)                
            logger.info(f"Getting firms  from {filepath}")
            df = pd.read_excel(filepath)
            df = df.replace([np.nan], [None])
            dfs.append(df)

    if dfs:
        filing_df = pd.concat(dfs, ignore_index=True)  # Concatenate all dataframes

        filing_df = filing_df.rename(
            columns={
                "Primary Business Name": "name",
                "Legal Name": "legal_name",
                "Firm Type":"fund_type"
            }
        )
        filing_df["master_fund_name"] = None 
        filing_df["filing_id"] = None 

        return filing_df


def train_model(logger,traning_data_file, model_bin_file):

    """
    Trains a FastText unsupervised model on the given training data.

    If the model already exists, it loads the existing model. Otherwise, it trains a new
    skipgram model and saves it. The training data file is then removed.

    Args:
        logger (logging.Logger): Logger for logging information and errors.
        traning_data_file (str): Path to the training data file.
        model_bin_file (str): Path to save the trained model (.bin file).

    Returns:
        fasttext.FastText._FastText: The trained FastText model.
    """
   
    logger.info("Training model")
    model = fasttext.train_unsupervised(
        traning_data_file,  # Path to the training data file containing firm names.
        model='skipgram',  # Use the skip-gram model architecture, which predicts context words from a target word.
        minn=2,          # Minimum length of character n-grams (2).  
                         # Crucial for capturing short tokens like 'DE', 'JP'.
        maxn=10,         # Maximum length of character n-grams (10).  Captures longer sub-word units.
        dim=100,         # Dimensionality of the word vectors (100).  Output embedding vector size.
        epoch=5,         # Number of training epochs (5).
        lr=0.05,        # Learning rate (0.05).
        loss='ns',       # Use negative sampling for loss function (efficient for large vocabularies).
        wordNgrams=2,    # Use word n-grams (2) in addition to sub-word n-grams.
        minCount=1       # Include all words, even those with frequency 1.  Ensures all firm names are represented.
    )
    
    model.save_model(model_bin_file) 
    return model
        

def write_model_to_text_file(logger,model,model_txt_file):

    """
    Writes the trained FastText model vectors to a text file.

    This function extracts word vectors from the FastText model and saves them in a text
    format, suitable for use with other embedding libraries.

    Args:
        logger (logging.Logger): Logger for logging information.
        model (fasttext.FastText._FastText): The trained FastText model.
        model_txt_file (str): Path to save the model in text format.
    """


    logger.info(f"Writing model to {model_txt_file}")
    model_dim = model.get_dimension()
    with open(model_txt_file, "w") as f:
        words = model.words
        for word in tqdm.tqdm(words, desc=f"Writing model to {model_txt_file}"):
            vector = model.get_word_vector(word)
            # Clean the token
            if word=="FORTRESS JAPAN OPPORTUNITY FUND IV YEN":
                word = escape_token_text_for_txt_file(word)
            #ensure its not an empty string
            if word and len(vector) == model_dim:
                vector_str = " ".join([str(v) for v in vector]) # More robust conversion to string
                f.write(f"{word} {vector_str}\n") 


    
def train_firm_fast_text():
    """
    Orchestrates the training of a FastText model on firm names from various sources.

    This function retrieves firm names from 5K3, 7B1, Books and Records filings,
    ADV filings, and Investment Advisor Firms data, concatenates them, preprocesses
    the names, trains a FastText model, and saves the model to a text file.
    """
    logger = loggers.setup_logger("TrainFastTextModel")
    args_loader.LoadArgs() # Parse command-line arguments
    logger.info(args_loader.string_to_print())
    filing_5k3_df = get_filing_5k3_df(logger)
    filing_7b1_df = get_filing_7b1_df(logger)
    filing_filing_firm_df = get_filing_firm_df(logger)
    filing_b_r_firm_df = get_filing_b_r_df(logger)
    filing_adv_firms_df = get_adv_firms_df(logger)

    union_df = pd.concat(
        [
            filing_5k3_df[
                [ "name", "legal_name", "master_fund_name"]
            ],
            filing_7b1_df[
                [ "name", "legal_name", "master_fund_name"]
            ],
            filing_b_r_firm_df[
                [ "name", "legal_name", "master_fund_name"]
            ],
            filing_filing_firm_df[
                [ "name", "legal_name", "master_fund_name"]
            ],
            filing_adv_firms_df[
                [ "name", "legal_name", "master_fund_name"]
            ]
        ],
        ignore_index=True,
    )

    union_df["name"] = union_df["name"].apply(clean_initials_and_punctuation_for_company_string)
    union_df["legal_name"] = union_df["legal_name"].apply(clean_initials_and_punctuation_for_company_string)
    union_df["master_fund_name"] = union_df["master_fund_name"].apply(clean_initials_and_punctuation_for_company_string)
    
    all_company_names_combined = pd.concat([union_df['name'], union_df['legal_name'], union_df['master_fund_name']])
    cleaned_names = all_company_names_combined.dropna()
    unique_sorted_names = sorted(cleaned_names.unique())
    
    ensure_dir(FAST_TEXT_DIR)
    training_file =  os.path.join(FAST_TEXT_DIR, 'corpus.txt')
    bin_file =  os.path.join(FAST_TEXT_DIR, 'model.bin')
    raw_file =  os.path.join(FAST_TEXT_DIR, 'model.txt')


    with open(training_file,"w") as f:
       logger.info(f"Writing training data to {training_file}")
       for name in tqdm.tqdm(unique_sorted_names, desc="Writing corpus", total=len(union_df), unit="row"):
            f.write(f"{(name)}\n")

    model = train_model(logger,training_file,bin_file)
    write_model_to_text_file(logger,model,raw_file)
                    
            


    
# --- Main execution block ---
if __name__ == "__main__":
    train_firm_fast_text()
# --- End main execution block ---