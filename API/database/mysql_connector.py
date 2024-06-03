from datetime import datetime
import mysql.connector
import uuid
from config.task_key import __TASK_KEY__
from services import file_management
from config import CONFIG_DATABASE


mysqldb = mysql.connector.connect(
  host="host.docker.internal",
  user="root",
  password="root",
  database=CONFIG_DATABASE['DATABASE_NAME']
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
        status = 'pending'
        values.append(f"('{job_id}', '{type_value}', {step}, '{status}')")

    # Join the value tuples into a single string
    values_str = ", ".join(values)

    # Final SQL query
    sql += values_str
    print(sql)
    execute_mysql = mysqldb.cursor(buffered=True)
    execute_mysql.execute(sql)

def initialTable():
    print("-------Begin create tables-------")
    execute_mysql = mysqldb.cursor(buffered=True)
    # file_data
    execute_mysql.execute("CREATE TABLE IF NOT EXISTS file_data (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255),dir VARCHAR(255),size VARCHAR(255), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
    # logs
    execute_mysql.execute("CREATE TABLE IF NOT EXISTS logs (id INT AUTO_INCREMENT PRIMARY KEY, created_at DATETIME, log TEXT)")
    # jobs
    execute_mysql.execute("CREATE TABLE IF NOT EXISTS jobs (id VARCHAR(255) PRIMARY KEY, type VARCHAR(255), step INT, status VARCHAR(255),created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    # job_results
    execute_mysql.execute("CREATE TABLE IF NOT EXISTS job_results (id INT AUTO_INCREMENT PRIMARY KEY, job_id VARCHAR(255), total_record INT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    print("__________Done created tables__________")
    print("__________Begin create file and directory__________")
    insert_file_data(file_management.__file_name__['tgdd_end_page_link'], file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_end_page_link'] + '.csv', '100KB' )
    insert_file_data(file_management.__file_name__['tgdd_end_page_link'], file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_end_page_link'] + '.csv', '100KB' )
    insert_file_data(file_management.__file_name__['tgdd_end_page_link'], file_management.__path__['crawl_data'] + '/' + file_management.__file_name__['tgdd_end_page_link'] + '.csv', '100KB' )
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
    mysqldb.commit()

def update_jobs(task_key, status):
    cursor = mysqldb.cursor()
    query = "UPDATE jobs SET status = %s where type = %s"
    cursor.execute(query, (status, task_key))
    mysqldb.commit()

