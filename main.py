from flask import Flask, render_template, redirect, url_for, request
import sqlite3
from sqlite3 import Error

database = "election.db"

try:
    with open("bincom_test.sql", "r") as sql_file:
        sql = sql_file.read()
        db = sqlite3.connect("election.db", check_same_thread=False)
    cursor = db.cursor()
    cursor.executescript(sql)
    db.commit()


except Error as error:
    print(error)
    # pass

app = Flask(__name__)


def query_db(query, one=False):
    cursor.execute(query)
    r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    return r if r else None if one else r


def check_polling_units_query(local):
    query = f"""
            SELECT polling_unit_name, polling_unit_description, polling_unit_number, lat, long, lga_name, ward_name
            FROM lga
            INNER JOIN ward ON lga.lga_id = ward.lga_id
            INNER JOIN polling_unit ON ward.ward_id = polling_unit.ward_id
            WHERE lga.lga_name = '{local}'
            ORDER BY polling_unit_name DESC
            """
    return query



def check_result_query(area):
    query = f"""
            SELECT party_abbreviation, party_score
            FROM polling_unit
            INNER JOIN announced_pu_results ON polling_unit.uniqueid = announced_pu_results.polling_unit_uniqueid
            INNER JOIN lga ON polling_unit.lga_id = lga.lga_id
            WHERE announced_pu_results.polling_unit_uniqueid = polling_unit.uniqueid
            """
    return query


@app.route("/", methods=['POST', 'GET'])
def home():
    query = "SELECT lga_name FROM lga"

    LGA = query_db(query=query)
    if request.method == "POST":
        return redirect(url_for('polling'))
    return render_template("index.html", lga=LGA)


@app.route("/polling", methods=['POST', 'GET'])
def polling():
    area = request.form.get('local')
    query = check_polling_units_query(local=area)
    polling_units = query_db(query=query)
    return render_template("polling.html", row=polling_units)


@app.route("/result", methods=['POST', 'GET'])
def result():
    area = request.form.get('local')
    query = check_result_query(area)
    lga_result = query_db(query=query)
    return render_template("result.html", result=lga_result)


if __name__ == "__main__":
    app.run(debug=True)
