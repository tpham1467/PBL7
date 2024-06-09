import uuid
from datetime import datetime

import mysql.connector
from config import read_config_api
from config.task_key import __TASK_KEY__
from entities import Job
from services import file_management

config = read_config_api("DB_")
print(config)
mysqldb = mysql.connector.connect(
    # host="host.docker.internal",
    host=config["DB_HOST"],
    user="root",
    password="root",
    database=config["DB_DATABASE_NAME"],
)


def checkMysqlConnect():
    # print(os.environ['DB_CONNECTION'])
    # print(os.environ['DB_HOST'])
    # print(os.environ['DB_PORT'])
    # print(os.environ['DB_DATABASE'])
    print(mysqldb.cursor())


def insert_jobs():
    sql = "INSERT INTO jobs (id, type, step, status) VALUES "

    # List to store individual value tuples
    values = []

    # Iterate through __TASK_KEY__ and prepare the value tuples
    for key, type_value in __TASK_KEY__.items():
        print(__TASK_KEY__.items())
        job_id = str(uuid.uuid4())  # Generating a unique ID for each row
        step = 0  # Assuming initial step is 0
        status = "PENDING"
        values.append(f"('{job_id}', '{type_value}', {step}, '{status}')")

    # Join the value tuples into a single string
    values_str = ", ".join(values)

    # Final SQL query
    sql += values_str
    print(sql)
    execute_mysql = mysqldb.cursor(buffered=True)
    execute_mysql.execute(sql)
    mysqldb.commit()


def insert_preprocess():
    job_results = getAll("job_results")
    print(f"job_results: {job_results}")
    if not job_results:
        table_name = "job_results"
        initial_record = 0
        preprocess_tasks = [
            "tokenize",
            "lowercase",
            "remove_stopwords",
            "remove_punctuation",
        ]

        for preprocess_task in preprocess_tasks:
            insert(
                table_name,
                job_id=preprocess_task,
                total_record=initial_record,
                created_at=datetime.now(),
            )
    else:
        print("job_results table has value")


def initialTable():
    print("-------Begin create tables-------")
    execute_mysql = mysqldb.cursor(buffered=True)
    # file_data
    execute_mysql.execute(
        "CREATE TABLE IF NOT EXISTS file_data (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255),dir VARCHAR(255),size VARCHAR(255), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"
    )
    # logs
    execute_mysql.execute(
        "CREATE TABLE IF NOT EXISTS logs (id INT AUTO_INCREMENT PRIMARY KEY, created_at DATETIME, log TEXT)"
    )
    # jobs
    execute_mysql.execute(
        "CREATE TABLE IF NOT EXISTS jobs (id VARCHAR(255) PRIMARY KEY, type VARCHAR(255), step INT, status VARCHAR(255),created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    # job_results
    execute_mysql.execute(
        "CREATE TABLE IF NOT EXISTS job_results (id INT AUTO_INCREMENT PRIMARY KEY, job_id VARCHAR(255), total_record INT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    print("__________Done created tables__________")
    print("__________Begin create file and directory__________")
    insert_file_data(
        file_management.__file_name__["tgdd_crawl_category"],
        file_management.__path__["crawl_data"]
        + "/"
        + file_management.__file_name__["tgdd_crawl_category"]
        + ".csv",
        "100KB",
    )
    insert_file_data(
        file_management.__file_name__["tgdd_crawl_end_page_link"],
        file_management.__path__["crawl_data"]
        + "/"
        + file_management.__file_name__["tgdd_crawl_end_page_link"]
        + ".csv",
        "100KB",
    )
    insert_file_data(
        file_management.__file_name__["tgdd_crawl_product_link"],
        file_management.__path__["crawl_data"]
        + "/"
        + file_management.__file_name__["tgdd_crawl_product_link"]
        + ".csv",
        "100KB",
    )
    insert_file_data(
        file_management.__file_name__["tgdd_crawl_description"],
        file_management.__path__["crawl_data"]
        + "/"
        + file_management.__file_name__["tgdd_crawl_description"]
        + ".csv",
        "100KB",
    )
    insert_file_data(
        file_management.__file_name__["preprocess"],
        file_management.__path__["crawl_data"]
        + "/"
        + file_management.__file_name__["preprocess"]
        + ".csv",
        "100KB",
    )
    print("__________Inserted successfully__________")
    print("__________Begin create jobs__________")
    insert_jobs()
    print("__________Inserted successfully__________")


def getAll(table: str):
    execute_mysql = mysqldb.cursor(buffered=True)
    query = "SELECT * FROM " + table + " ORDER BY created_at DESC"
    execute_mysql.execute(query)
    write_log(query)
    return execute_mysql.fetchall()


def insert(table: str, **kwargs):
    execute_mysql = mysqldb.cursor(buffered=True)

    try:
        fields = ", ".join(kwargs.keys())
        placeholders = ", ".join(["%s" for _ in range(len(kwargs))])
        values = tuple(kwargs.values())

        query = f"INSERT INTO {table} ({fields}) VALUES ({placeholders})"
        print(query, values)
        # Thực thi truy vấn
        execute_mysql.execute(query, values)
        # Commit thay đổi
        mysqldb.commit()
        write_log(query)
        print("__________Inserted successfully__________")
    except Exception as e:
        print("Error:", e)
        # Rollback trong trường hợp có lỗi
        mysqldb.rollback()


def delete(table: str, id: str):
    execute_mysql = mysqldb.cursor(buffered=True)
    execute_mysql.execute(f"DELETE FROM {table} WHERE id = {id}")
    mysqldb.commit()


def write_log(log: str):
    execute_mysql = mysqldb.cursor(buffered=True)
    current_time = datetime.now()
    insert_query = "INSERT INTO logs (created_at, log) VALUES (%s, %s)"
    values = (current_time, log)
    execute_mysql.execute(insert_query, values)
    mysqldb.commit()


def insert_file_data(name, dir, size):
    cursor = mysqldb.cursor()
    query = "INSERT INTO file_data (name, dir, size) VALUES (%s, %s, %s)"
    values = (name, dir, size)
    cursor.execute(query, values)
    write_log(query)
    mysqldb.commit()


def get_all_by_conditional(table: str, conditions: str, selected_columns=["*"]):
    with mysqldb.cursor() as cursor:
        columns = ", ".join(selected_columns)
        query = f"SELECT {columns} FROM {table} WHERE {conditions}"
        print(query)
        cursor.execute(query)
        results = cursor.fetchall()
    return results


def update_jobs(task_key, status):
    cursor = mysqldb.cursor()
    query = "UPDATE jobs SET status = %s where type = %s"
    cursor.execute(query, (status, task_key))
    mysqldb.commit()


def update_jobs_by_task_id(task_key, task_id):
    cursor = mysqldb.cursor()
    query = "UPDATE jobs SET id = %s where type = %s"
    cursor.execute(query, (task_id, task_key))
    mysqldb.commit()


def update_preprocess_tasks(job_id, total_record, created_at=None):
    print(f"____UPDATE PREPROCESS TASK____: {job_id}, {total_record}")
    if created_at is None:
        created_at = datetime.now()
    prev_total_record = get_total_record(job_id)
    if prev_total_record != total_record:
        try:
            with mysqldb.cursor() as cursor:
                query = "UPDATE job_results SET total_record=%s, created_at=%s WHERE job_id=%s"
                cursor.execute(query, (total_record, created_at, job_id))
            mysqldb.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            mysqldb.rollback()
    print(f"____UPDATE PREPROCESS TASK DONE____: {job_id}, {total_record}")


def get_all_jobs():
    try:
        results = getAll("jobs")
        jobs = []
        for row in results:
            job_id, job_type, step, status, created_at = row
            # Convert MySQL timestamp to datetime object if necessary
            if isinstance(created_at, datetime):
                created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
            job = Job(job_id, job_type, step, status, created_at)
            jobs.append(job)
        return jobs

    except Exception as e:
        print("Error fetching jobs:", e)
        return []


def get_tasks_status() -> list:
    cursor = mysqldb.cursor(dictionary=True)
    query = "SELECT type, status FROM jobs"
    cursor.execute(query)
    return cursor.fetchall()


def get_task_status(type: str) -> str:
    cursor = mysqldb.cursor(dictionary=True)
    query = "SELECT status FROM jobs WHERE type= %s"
    cursor.execute(query)

    return cursor.fetchone()


def get_total_record(job_id: str):
    return get_all_by_conditional("job_results", f"job_id='{job_id}'", ["total_record"])
