from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)

def create_connection():
    conn = sqlite3.connect("gps_data.db")
    conn.row_factory = sqlite3.Row  # Umožní přístup ke sloupcům podle jména
    return conn

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/filters')
def get_filters():
    """
    Vrací unikátní kombinace:
    - Rok: extrahováno pomocí SUBSTR(datum, 7, 4)
    - Měsíc: extrahováno pomocí SUBSTR(datum, 4, 2)
    - Kategorie a symbol
    """
    conn = create_connection()
    cur = conn.cursor()
    query = """
        SELECT DISTINCT substr(datum, 7, 4) AS year,
                        substr(datum, 4, 2) AS month,
                        kategorie, symbol
        FROM gps_data
    """
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    data = [dict(row) for row in rows]
    return jsonify(data)

@app.route('/api/data')
def get_data():
    """
    Vrací data podle filtru. Přijímá parametry (možné vícenásobné, oddělené čárkami):
    - year: např. "2023" nebo "2022,2023"
    - month: např. "03" nebo "01,05"
    - kategorie: např. "KADAVER" nebo "KADAVER,NECO"
    """
    year = request.args.get('year')
    month = request.args.get('month')
    kategorie = request.args.get('kategorie')
    
    query = "SELECT * FROM gps_data WHERE 1=1"
    params = []
    
    if year:
        years = year.split(',')
        placeholders = ",".join("?" for _ in years)
        query += f" AND substr(datum, 7, 4) IN ({placeholders})"
        params.extend(years)
        
    if month:
        months = month.split(',')
        placeholders = ",".join("?" for _ in months)
        query += f" AND substr(datum, 4, 2) IN ({placeholders})"
        params.extend(months)
        
    if kategorie:
        categories = kategorie.split(',')
        placeholders = ",".join("?" for _ in categories)
        query += f" AND kategorie IN ({placeholders})"
        params.extend(categories)
        
    conn = create_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    data = [dict(row) for row in rows]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)

