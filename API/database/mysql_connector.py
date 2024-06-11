import uuid
from datetime import datetime

import config
import mysql.connector
from config import read_config_api
from config.task_key import __TASK_KEY__
from entities import Job, JobResult
from services import file_management

config = read_config_api("DB_")
print(config)


def get_db_connection():
    return mysql.connector.connect(
        # host="host.docker.internal",
        host=config["DB_HOST"],
        user=config["DB_USERNAME"],,
        password=config["DB_PASSWORD"],,
        database=config["DB_DATABASE_NAME"],
    )


def checkMysqlConnect():
    # print(os.environ['DB_CONNECTION'])
    # print(os.environ['DB_HOST'])
    # print(os.environ['DB_PORT'])
    # print(os.environ['DB_DATABASE'])
    mysqldb = get_db_connection()
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

    mysqldb = get_db_connection()
    execute_mysql = mysqldb.cursor(buffered=True)
    try:
        execute_mysql.execute(sql)
        write_log(sql)
        mysqldb.commit()
    finally:
        execute_mysql.close()
        print("closed cursor connection!!!")
        mysqldb.close()
        print("closed mysqldb connection!!!")
    print("DONE INSERT JOBS")


def insert_preprocess():
    # print("INSERT JOBS RESULT")
    job_results = getAll("job_results")
    # print(f"job_results: {job_results}")
    if not job_results:
        table_name = "job_results"
        initial_record = 0
        preprocess_tasks = [
            "tokenize",
            "lowercase",
            "remove_stopwords",
            "remove_punctuation",
        ]

        job_id = get_job_id("preprocess")
        # print(f"job_id: {job_id}")

        for preprocess_task in preprocess_tasks:
            insert(
                table_name,
                job_type=preprocess_task,
                job_id=job_id,
                total_record=initial_record,
            )
    else:
        print("job_results table has value")


def initialTable():
    print("-------Begin create tables-------")
    mysqldb = get_db_connection()
    execute_mysql = mysqldb.cursor(buffered=True)
    try:
        # file_data
        execute_mysql.execute(
            """
            CREATE TABLE IF NOT EXISTS file_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255),
                dir VARCHAR(255),
                size VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        # logs
        execute_mysql.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                created_at DATETIME,
                log TEXT
            );
            """
        )
        # jobs
        execute_mysql.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id VARCHAR(255) PRIMARY KEY, type VARCHAR(255),
                step INT,
                status VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                begin_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        # job_results
        execute_mysql.execute(
            """
            CREATE TABLE IF NOT EXISTS job_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                job_type VARCHAR(255),
                job_id VARCHAR(255), 
                total_record INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                begin_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
        )
    finally:
        execute_mysql.close()
        mysqldb.close()

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
    insert_preprocess()
    print("__________Inserted successfully__________")


def getAll(table: str):
    mysqldb = get_db_connection()
    execute_mysql = mysqldb.cursor(buffered=True)
    query = "SELECT * FROM " + table + " ORDER BY created_at DESC"
    try:
        execute_mysql.execute(query)
        write_log(query)
    finally:
        execute_mysql.close()
        mysqldb.close()
    return execute_mysql.fetchall()


def insert(table: str, **kwargs):
    mysqldb = get_db_connection()
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
    finally:
        execute_mysql.close()
        mysqldb.close()


def delete(table: str, id: str):
    mysqldb = get_db_connection()
    execute_mysql = mysqldb.cursor(buffered=True)
    try:
        query = f"DELETE FROM {table} WHERE id = {id}"
        execute_mysql.execute(query)
        write_log(query)
        mysqldb.commit()
    finally:
        execute_mysql.close()
        mysqldb.close()


def write_log(log: str):
    mysqldb = get_db_connection()
    execute_mysql = mysqldb.cursor(buffered=True)
    current_time = datetime.now()
    insert_query = "INSERT INTO logs (created_at, log) VALUES (%s, %s)"
    values = (current_time, log)
    try:
        execute_mysql.execute(insert_query, values)
        mysqldb.commit()
    finally:
        execute_mysql.close()
        mysqldb.close()


def insert_file_data(name, dir, size):
    mysqldb = get_db_connection()
    cursor = mysqldb.cursor()
    query = "INSERT INTO file_data (name, dir, size) VALUES (%s, %s, %s)"
    values = (name, dir, size)
    try:
        cursor.execute(query, values)
        write_log(query)
        mysqldb.commit()
    finally:
        cursor.close()
        mysqldb.close()
    write_log(query)


def get_all_by_conditional(table: str, conditions: str, selected_columns=["*"]):
    mysqldb = get_db_connection()
    cursor = mysqldb.cursor()

    columns = ", ".join(selected_columns)
    query = f"SELECT {columns} FROM {table} WHERE {conditions}"
    print(query)
    try:
        cursor.execute(query)
        write_log(query)
        results = cursor.fetchall()
    finally:
        cursor.close()
        mysqldb.close()
    return results


def update_jobs(task_key, status, begin_at=None, end_at=None):
    mysqldb = get_db_connection()
    cursor = mysqldb.cursor()

    # Construct the base SQL query
    query = "UPDATE jobs SET status = %s"

    # Append 'begin_at' to the query if provided
    if begin_at is not None:
        query += ", begin_at = %s"

    # Append 'end_at' to the query if provided
    if end_at is not None:
        query += ", end_at = %s"
    # Add the WHERE clause
    query += " WHERE type = %s"

    try:
        # Construct the parameter tuple for the execute method
        params = (status,)

        # Add 'begin_at' parameter if provided
        if begin_at is not None:
            params += (begin_at,)

        # Add 'end_at' parameter if provided
        if end_at is not None:
            params += (end_at,)

        # Add 'task_key' parameter for the WHERE clause
        params += (task_key,)

        # Execute the query with parameters
        cursor.execute(query, params)
        write_log(query)
        mysqldb.commit()
    finally:
        cursor.close()
        mysqldb.close()


def update_jobs_by_task_id(task_key, task_id):
    mysqldb = get_db_connection()
    cursor = mysqldb.cursor()
    query = "UPDATE jobs SET id = %s where type = %s"
    try:
        cursor.execute(query, (task_id, task_key))
        mysqldb.commit()
    finally:
        cursor.close()
        mysqldb.close()


def update_preprocess_tasks(job_id, total_record, end_at=None):
    print(f"____UPDATE PREPROCESS TASK____: {job_id}, {total_record}")
    if end_at is None:
        end_at = datetime.now()
    prev_total_record = get_total_record(job_id)
    print(f"prev total record: {prev_total_record}")
    if prev_total_record != total_record:
        mysqldb = get_db_connection()
        try:
            with mysqldb.cursor() as cursor:
                query = "UPDATE job_results SET total_record=%s, end_at=%s WHERE job_type=%s"
                write_log(query)
                cursor.execute(query, (total_record, end_at, job_id))
            mysqldb.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            mysqldb.rollback()
        finally:
            cursor.close()
            mysqldb.close()
    print(f"____UPDATE PREPROCESS TASK DONE____: {job_id}, {total_record}")


def get_all_jobs():
    try:
        results = getAll("jobs")
        jobs = []
        for row in results:
            job_id, job_type, step, status, created_at, begin_at, end_at = row
            # Convert MySQL timestamp to datetime object if necessary
            if isinstance(created_at, datetime):
                created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
            job = Job(job_id, job_type, step, status, created_at, begin_at, end_at)
            jobs.append(job)
        return jobs

    except Exception as e:
        print("Error fetching jobs:", e)
        return []


def get_all_jobs_result():
    try:
        results = getAll("job_results")
        print(results)
        job_results = []
        for row in results:
            id, job_type, job_id, total_record, created_at, begin_at, end_at = row
            # print(f"{id},{job_type}, {job_id}, {total_record},....")
            # Convert MySQL timestamp to datetime object if necessary
            if isinstance(created_at, datetime):
                created_at = created_at.strftime("%Y-%m-%d %H:%M:%S")
            # print("OK")
            job_result = JobResult(
                job_type, job_id, total_record, created_at, begin_at, end_at
            )
            # print(job_result.job_type)
            job_results.append(job_result)
        return job_results
    except Exception as e:
        print("Error fetching job_results:", e)
        return []


def is_any_task_in_progress() -> bool:
    mysqldb = get_db_connection()
    cursor = mysqldb.cursor(dictionary=True)
    query = "SELECT 1 FROM jobs WHERE status = 'IN_PROGRESS' LIMIT 1"
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        write_log(query)
        # print(f"is_any_task_in_progress:{result is not None}")
    finally:
        cursor.close()
        mysqldb.close()
    return result is not None


def get_tasks_status() -> list:
    mysqldb = get_db_connection()
    cursor = mysqldb.cursor(dictionary=True)
    query = "SELECT type, status FROM jobs"
    try:
        cursor.execute(query)
        write_log(query)
    finally:
        cursor.close()
        mysqldb.close()
    return cursor.fetchall()


# get task status from jobs
def get_task_status(type: str) -> str:
    mysqldb = get_db_connection()
    cursor = mysqldb.cursor(dictionary=True)
    query = "SELECT status FROM jobs WHERE type= %s"
    try:
        cursor.execute(query)
        write_log(query)
    finally:
        cursor.close()
        mysqldb.close()
    return cursor.fetchone()


# get job id in jobs table
def get_job_id(job_type):
    mysqldb = get_db_connection()
    cursor = mysqldb.cursor(buffered=True)
    query = f"SELECT id FROM jobs WHERE type='{job_type}'"
    try:
        cursor.execute(query)
        write_log(query)
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    finally:
        cursor.close()
        mysqldb.close()


def get_total_record(job_id: str):
    return get_all_by_conditional(
        "job_results", f"job_type='{job_id}'", ["total_record"]
    )


def get_job_data():
    try:
        mysqldb = get_db_connection()
        if mysqldb.is_connected():
            cursor = mysqldb.cursor(dictionary=True)

            # SQL query to join the two tables
            query = """
                SELECT jobs.*, job_results.total_record
                FROM jobs
                JOIN job_results ON jobs.id = job_results.job_id;
            """

            cursor.execute(query)
            write_log(query)
            # Fetch all rows from the result
            rows = cursor.fetchall()
            # Close the cursor and connection
            cursor.close()
            mysqldb.close()

            # Format the data into the desired JSON structure
            job_data = []
            for row in rows:
                job = {
                    "job_id": row["id"],
                    "job_type": row["type"],
                    "step": row["step"],
                    "status": row["status"],
                    "created_at": str(row["created_at"]),
                    "total_record": row["total_record"],
                }
                job_data.append(job)

            return job_data

    except mysql.connector.Error as e:
        print("Error connecting to MySQL:", e)
        return None
