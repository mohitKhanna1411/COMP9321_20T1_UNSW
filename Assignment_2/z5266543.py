# Author: Mohit Khanna
# Student ID: z5266543
# Platform: Mac

from flask import Flask
from flask_restplus import Resource, Api
import sqlite3
from sqlite3 import Error
import os
import json
import time
import re
import urllib.request as req

app = Flask(__name__)
api = Api(app, default="World Bank Data", title="Assignment 2: COMP9321",
          description="Made by Mohit Khanna z5266543")

db_name = "z5266543.db"


def database_controller(database, command):
    try:
        connection = sqlite3.connect(database)
        connection.set_trace_callback(print)
    except Error as e:
        print(e)
    cursor = connection.cursor()
    if len(re.findall(';', command)) > 1:
        cursor.executescript(command)
    else:
        cursor.execute(command)
    result = cursor.fetchall()
    connection.commit()
    connection.close()
    return result


def create_db(db_file):
    if os.path.exists(db_file):
        print("Database already exists.")
        return False

    print("Creating database ...")
    create_table_indicator = '''
        CREATE TABLE Collection(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        indicator_id VARCHAR(100),
        indicator_value VARCHAR(100),
        creation_time DATE
        );
        '''
    create_table_values = '''
        CREATE TABLE Entries(
        collection_id INTEGER NOT NULL,
        country VARCHAR(100),
        date INTEGER,
        value REAL,
        CONSTRAINT entry_fkey
        FOREIGN KEY (collection_id)
        REFERENCES Collection(id));
        '''
    database_controller(db_file, create_table_indicator)
    database_controller(db_file, create_table_values)

    return True


def remote_request(indicator, start="2012", end="2017", content_format="json", per_page="1000"):
    url = "http://api.worldbank.org/v2/countries/all/indicators/"+indicator + \
        "?date="+start+":"+end+"&format="+content_format+"&per_page="+per_page
    resource = req.Request(url)
    data = req.urlopen(resource).read()
    if re.findall("Invalid value", str(data), flags=re.I):
        return False
    return json.loads(data)[1]


def response_question1(query_result):
    return {"uri": "/collections/" + str(query_result[0]),
            "id": query_result[0],
            "creation_time": query_result[3],
            "indicator_id": query_result[1],
            }


def response_question3(query_result):
    result = []
    for res in query_result:
        result.append({"uri": "/collections/" + str(res[0]),
                       "id": res[0],
                       "creation_time": res[3],
                       "indicator": res[1],
                       })
    return result


def response_question4(query_result_collection, query_result_entries):
    result = {"id": query_result_collection[0],
              "indicator": query_result_collection[1],
              "indicator_value": query_result_collection[2],
              "creation_time": query_result_collection[3],
              "entries": []
              }
    for res in query_result_entries:
        result["entries"].append({"country": res[1],
                                  "date": res[2],
                                  "value": res[3]
                                  })
    return result


def response_question5(query_result):
    return {"id": query_result[0],
            "indicator": query_result[1],
            "country": query_result[2],
            "year": query_result[3],
            "value": query_result[4]
            }


def response_question6(query_result_collection, query_result_entries):
    result = {"indicator": query_result_collection[0],
              "indicator_value": query_result_collection[1],
              "entries": []
              }
    for res in query_result_entries:
        result["entries"].append({"country": res[0],
                                  "value": res[1]
                                  })
    return result


parser = api.parser()
parser_2 = api.parser()
parser_3 = api.parser()
parser.add_argument('indicator_id', type=str, location='args')
parser_2.add_argument('order_by', type=str, location='args', action='split')
parser_3.add_argument('q', type=str, location='args')


@api.route("/collections")
class Task1and3(Resource):
    @api.response(200, 'Success')
    @api.response(201, 'Created')
    @api.response(400, 'Bad Request')
    @api.response(404, 'Not Found')
    @api.param('indicator_id', 'The indicator identifier (e.g."NY.GDP.MKTP.CD")')
    @api.doc(parser=parser, description="Add a new world bank collection")
    def post(self):
        indicator_id = parser.parse_args()['indicator_id']

        if not indicator_id:
            return {"message": "Please provide indicator_id in query params"}, 400

        query = database_controller(
            db_name, "SELECT * FROM Collection WHERE indicator_id = '" + indicator_id + "';")

        if query:
            return response_question1(query[0]), 200
        else:
            world_bank_data = remote_request(indicator_id)
            if not world_bank_data:
                return {"message": "The indicator_id '" + indicator_id + "' not found in data source"}, 404

            curr_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            insert_query = "INSERT INTO Collection (indicator_id, indicator_value, creation_time) VALUES ('{}', '{}', '{}');"\
                .format(world_bank_data[0]['indicator']['id'], world_bank_data[0]['indicator']['value'], curr_time)
            database_controller(db_name, insert_query)

            get_query_result = database_controller(
                db_name, "SELECT * FROM Collection WHERE indicator_id = '" + indicator_id + "';")
            entry = ""
            for data in world_bank_data:
                if data['value'] is not None:
                    country_val = data['country']['value'].replace("'", "''")
                    entry += f" INSERT INTO Entries VALUES ({get_query_result[0][0]}, '{country_val}', '{data['date']}', {data['value']});"
            # entry = entry.rstrip(",") + ";"
            database_controller(db_name, entry)

            return response_question1(get_query_result[0]), 201

    @api.response(200, 'Success')
    @api.response(400, 'Bad Request')
    @api.param('order_by', 'Specific order (e.g."+id,-creation_time,+indicator")')
    @api.doc(parser=parser_2, description="Get all collection in a specific order")
    def get(self):
        order_by_list = parser_2.parse_args()['order_by']
        allowed_values = ["+id", "+creation_time", "+indicator_id",
                          "-id", "-creation_time", "-indicator_id"]
        if not order_by_list:
            return {"message": "Please provide order_by in query params"}, 400

        order_by_list = ",".join(order_by_list).replace(
            "indicator", "indicator_id").split(",")
        order_by = ""
        for o in order_by_list:
            if o[0] == '+' and o in allowed_values:
                order_by += o.split('+')[1] + ' ASC, '
            elif o[0] == '-' and o in allowed_values:
                order_by += o.split('-')[1] + ' DESC, '
            else:
                return {"message": "Please provide correct orderby criteria in the query params"}, 400
        get_query_result = database_controller(
            db_name, "SELECT * FROM Collection ORDER BY " + order_by[:-2] + ";")

        return response_question3(get_query_result), 200


@api.route("/collections/<int:id>")
class Task2and4(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Bad Request')
    @api.response(404, 'Not Found')
    @api.doc(description="Delete a collection by ID")
    def delete(self, id):
        if not id:
            return {
                "message": "Please provide id to delete a collection from database"
            }, 400

        query = database_controller(
            db_name, "SELECT * FROM Collection WHERE id = '" + str(id) + "';")
        if not query:
            return {"message": "collection '" + str(id) + "' not found in the database!"}, 404
        else:
            database_controller(
                db_name, "DELETE FROM Entries WHERE collection_id = '" + str(id) + "';")
            database_controller(
                db_name, "DELETE FROM Collection WHERE id = '" + str(id) + "';")
            return {"message": "The collection '" + str(id) + "' was removed from the database!"}, 200

    @api.response(200, 'Success')
    @api.response(400, 'Bad Request')
    @api.response(404, 'Not Found')
    @api.doc(description="Get a collection by ID")
    def get(self, id):
        if not id:
            return {"message": "Please provide id to get a collection from database"}, 400

        collection_result = database_controller(
            db_name, "SELECT * FROM Collection WHERE id = '" + str(id) + "';")
        if not collection_result:
            return {"message": "collection '" + str(id) + "' not found in the database!"}, 404
        else:
            entries_result = database_controller(
                db_name, "SELECT * FROM Entries WHERE collection_id = '" + str(id) + "';")
            return response_question4(collection_result[0], entries_result), 200


@api.route("/collections/<int:id>/<string:year>/<string:country>")
class Task5(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Bad Request')
    @api.response(404, 'Not Found')
    def get(self, id, year, country):
        if not id or not year or not country:
            return {
                "message": "Please provide valid params to get a collection from database"
            }, 400

        result_query = database_controller(
            db_name, "SELECT id, indicator_id, country, date, value FROM Collection JOIN Entries " +
            "ON (Collection.id = Entries.collection_id) WHERE " +
            "collection_id = '" + str(id) + "' AND date = '" + year + "' AND country = '" + country + "';")
        if not result_query:
            return {"message": "Data for '" + str(id) + "', '" + year + "' and '" + country + "' not found in the database!"}, 404
        else:
            return response_question5(result_query[0]), 200


@api.route("/collections/<int:id>/<string:year>")
class Task6(Resource):
    @api.response(200, 'Success')
    @api.response(400, 'Bad Request')
    @api.response(404, 'Not Found')
    @api.param('q', 'top/bottom N countires (e.g. +10, -50)')
    @api.doc(parser=parser_3, description="Get N countries by id and year")
    def get(self, id, year):

        if not id or not year:
            return {
                "message": "Please provide valid params to get a collection from database"
            }, 400

        collection_result = database_controller(
            db_name, "SELECT indicator_id, indicator_value FROM Collection WHERE id = '" + str(id) + "';")

        q = parser_3.parse_args()['q']
        if q:
            q = str(int(q))
            order = ""
            if q[0] == "-":
                order = "ASC"
                q = q[1:]
            else:
                order = "DESC"
                q = str(100) if int(q) >= 100 else q

            query = "SELECT country, value FROM Entries WHERE collection_id = '" + \
                str(id) + "' AND date = '" + year + \
                "' ORDER BY value " + order + " LIMIT " + q + ";"

        else:
            query = "SELECT country, value FROM Entries WHERE collection_id = '" + \
                str(id) + "' AND date = '" + year + "';"
        entries_result = database_controller(db_name, query)

        if not collection_result or not entries_result:
            return {"message": "Data for '" + str(id) + "' and '" + year + "' not found in the database!"}, 404

        return response_question6(collection_result[0], entries_result), 200


if __name__ == "__main__":
    create_db(db_name)

    app.run(host="127.0.0.1", port=8888, debug=True)
