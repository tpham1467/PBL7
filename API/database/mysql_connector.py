from datetime import datetime
import mysql.connector
import os
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


def initialTable():
    print("-------Begin create tables-------")
    execute_mysql = mysqldb.cursor(buffered=True)
    # file_data
    execute_mysql.execute("CREATE TABLE IF NOT EXISTS file_data (id INT AUTO_INCREMENT PRIMARY KEY,name VARCHAR(255),dir VARCHAR(255),size VARCHAR(255), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);")
    # logs
    execute_mysql.execute("CREATE TABLE IF NOT EXISTS logs (id INT AUTO_INCREMENT PRIMARY KEY, created_at DATETIME, log TEXT)")
    # jobs
    execute_mysql.execute("CREATE TABLE IF NOT EXISTS jobs (id INT AUTO_INCREMENT PRIMARY KEY, type VARCHAR(255), step INT, status VARCHAR(255),created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    # job_results
    execute_mysql.execute("CREATE TABLE IF NOT EXISTS job_results (id INT AUTO_INCREMENT PRIMARY KEY, job_id INT, total_record INT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    print("-------Done created tables-------")

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