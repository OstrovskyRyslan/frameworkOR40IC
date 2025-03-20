import pyodbc
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Налаштування підключення до MSSQL Server
DB_CONFIG = {
    'server': 'DESKTOP-QQAOEK4',
    'database': 'Game',
    'username': '',  # Для Windows Authentication не указываем пользователя
    'password': '',  # Для Windows Authentication не указываем пароль
}

def get_db_connection():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"Trusted_Connection=yes;"  # Для Windows Authentication
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
    )
    return conn

@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Обробка пошуку
    search_query = request.form.get("search", "")
    if search_query:
        cursor.execute("SELECT name, level, score, play_time FROM Players WHERE name LIKE ? ORDER BY score DESC", ('%' + search_query + '%',))
    else:
        cursor.execute("SELECT name, level, score, play_time FROM Players ORDER BY score DESC")
    players = cursor.fetchall()
    
    # Отримання загальної кількості гравців і середнього рейтингу
    cursor.execute("SELECT COUNT(*), AVG(score) FROM Players")
    total_players, avg_score = cursor.fetchone()
    
    conn.close()
    return render_template("index.html", players=players, total_players=total_players, avg_score=avg_score)

@app.route("/delete/<string:name>", methods=["POST"])
def delete_player(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Players WHERE name = ?", (name,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
