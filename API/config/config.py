import os
from dotenv import load_dotenv

def read_config_api(KEY: str):
    load_dotenv()
    env_variables = {}
    # del os.environ['DB_HOST'] 
    # del os.environ['DB_USERNAME']
    # del os.environ['DB_PASSWORD']
    # del os.environ['DB_DATABASE_NAME']
    for key, value in os.environ.items():
        if key.startswith(KEY):
            print(key, value)
            env_variables[key] = value

    return env_variables