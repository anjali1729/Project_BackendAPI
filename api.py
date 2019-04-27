from flask import Flask
from flask import request, jsonify
import json
import sqlite3

json_dict = {'company_country': 'country', 
            'company_id':'id',
            'contact_id':'id',
            'contact_email':'email',
            'company_name':'name',
            'company_revenue':'revenue',
            'contact_name':'name'}

app = Flask(__name__)
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    comp_d ={}
    for idx, col in enumerate(cursor.description):
        if "company" in col[0]:
            comp_d[json_dict[col[0]]] = row[idx]
        else:
            d[json_dict[col[0]]] = row[idx]
        d["company"]=comp_d
    return d

@app.route('/contacts', methods=['GET'])
def api_filter():
    query_parameters = request.args

    company_id = query_parameters.get('company_id')
    revenue_gte = query_parameters.get('revenue_gte')
    name = query_parameters.get('name')

    query = "SELECT contact_id, contact_name, contact_email, company_id, company_name, company_country, company_revenue from (SELECT contact.id AS contact_id, contact.name AS contact_name, contact.email AS contact_email, contact.company_id AS contact_company_id, company.id AS company_id, company.name AS company_name, company.country as company_country, CAST(company.revenue AS real) AS company_revenue from contact left join company on company.id=contact.company_id"
    to_filter = []

    if company_id:
        query += " WHERE company.id=? "
        to_filter.append(company_id)
    elif revenue_gte:
        query += " WHERE company.revenue>=? "
        to_filter.append(revenue_gte)
    elif name:
        query += " WHERE contact.name=? "
        to_filter.append(name)

    query = query + ");"

    print("query >> ", query)
    print("to_filter >> ", to_filter)
    conn = sqlite3.connect('leadbook.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query,to_filter).fetchall()

    return jsonify({"status_code": 200,"message": "successful","data":results})

@app.route("/contacts/<name>", methods = ['GET'])
def get_all_company(name=None):
    query = "SELECT contact_id, contact_name, contact_email, company_id, company_name, company_country, company_revenue from (SELECT contact.id AS contact_id, contact.name AS contact_name, contact.email AS contact_email, contact.company_id AS contact_company_id, company.id AS company_id, company.name AS company_name, company.country as company_country, CAST(company.revenue AS real) AS company_revenue from contact left join company on company.id=contact.company_id WHERE contact_id="+name+");"
    print("query >> ", query)
    #print("to_filter >> ", to_filter)
    conn = sqlite3.connect('lb.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query).fetchall()
    #print(results)
    return jsonify({"status_code": 200,"message": "successful","data":results})

app.run()
