# coding: utf-8
from flask import Flask, render_template, request, redirect
import psycopg2
import os

app = Flask(__name__)
BASE_URL = os.environ.get('BASE_URL')
DB_NAME = os.environ.get('DB_NAME')
USER_NAME = os.environ.get('USER_NAME')
USER_PASSWD = os.environ.get('USER_PASSWD')
DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')

def db_connect():
  connection = psycopg2.connect(
  database=DB_NAME, 
  user=USER_NAME, 
  password=USER_PASSWD, 
  host=DB_HOST, 
  port=DB_PORT)
  return connection

def db_close(connection): 
  connection.close()

def db_command_execute(connection, command):
  cursor = connection.cursor()
  cursor.execute(command)
  result = cursor.fetchall()
  cursor.close()
  return result

@app.route("/", methods=["GET"])
def note_list():
  connection = db_connect()
  command = 'SELECT title, shortid FROM "Notes" ORDER BY "lastchangeAt" DESC'
  result = db_command_execute(connection, command)
  db_close(connection)
  return render_template("result.html", result=result, base_url=BASE_URL)

@app.route("/result", methods=["POST", "GET"])
def search():
  if request.method == 'GET':
    return redirect('/')
  elif request.method == 'POST':
    keyword = request.form['keyword']
    if keyword == '':
      return redirect('/')  

    connection = db_connect()
    command = 'SELECT title, shortid FROM "Notes" WHERE title &@~ \'%s\' OR content &@~ \'%s\'' %(keyword, keyword)
    result = db_command_execute(connection, command)
    db_close(connection)
    return render_template("result.html", keyword = keyword, result=result, base_url=BASE_URL)

@app.route("/setup", methods=["GET"])
def setup():
  connection = db_connect()
  with connection.cursor() as cur:
    sql = '''
          CREATE EXTENSION pgroonga;
          '''
    cur.execute(sql)
    
    sql = '''
          CREATE INDEX pgroonga_content_index ON "Notes" USING pgroonga (content);
          '''
    cur.execute(sql)

    sql = '''
          CREATE INDEX pgroonga_title_index ON "Notes" USING pgroonga (title);
          '''
    cur.execute(sql)
    
    cur.close()  
    connection.commit()
  
  db_close(connection)
  return "OK"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)