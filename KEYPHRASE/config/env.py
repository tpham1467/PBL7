import os
from dotenv import load_dotenv

def read_config_model():
    load_dotenv(dotenv_path='.env')
    env_variables = {}

    # Iterate over all environment variables
    for key, value in os.environ.items():
        print("ENV: ", key, value)
        # Filter out only the variables defined in the .env file (if desired)
        # This example assumes that you only want to collect variables starting with a certain prefix, e.g., "DB_"
        if key.startswith("MODEL_"):
            env_variables[key] = value

    return env_variables