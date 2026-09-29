from datetime import datetime
import sqlite3
from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_flash'


def get_db_connection():
  conn = sqlite3.connect('database.db')
  conn.row_factory = sqlite3.Row
  return conn


def init_db():
  conn = get_db_connection()
  conn.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            description TEXT,
            year INTEGER,
            image_url TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
  conn.commit()
  conn.close()


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/author')
def author():
  return render_template('author.html')


@app.route('/cars')
def cars():
  search_query = request.args.get('q', '').strip()
  conn = get_db_connection()

  if search_query:
    query = (
        'SELECT * FROM cars WHERE brand LIKE ? OR model LIKE ? ORDER BY'
        ' created_at DESC'
    )
    like_param = f'%{search_query}%'
    cars_list = conn.execute(query, (like_param, like_param)).fetchall()
  else:
    cars_list = conn.execute(
        'SELECT * FROM cars ORDER BY created_at DESC'
    ).fetchall()

  conn.close()
  return render_template('cars.html', cars=cars_list, search_query=search_query)


@app.route('/add_car', methods=['POST'])
def add_car():
  brand = request.form['brand']
  model = request.form['model']
  description = request.form['description']
  year = request.form['year']
  image_url = request.form['image_url']

  if not brand or not model:
    flash('Марка та модель є обовʼязковими!', 'danger')
    return redirect(url_for('cars'))

  conn = get_db_connection()
  conn.execute(
    'INSERT INTO cars (brand, model, description, year, image_url) VALUES (?, ?, ?, ?, ?)',
    (brand, model, description, year, image_url),
  )
  conn.commit()
  conn.close()
  return redirect(url_for('cars'))



@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_car(id):
  conn = get_db_connection()

  if request.method == 'POST':
    brand = request.form['brand']
    model = request.form['model']
    description = request.form['description']
    year = request.form['year']
    image_url = request.form['image_url']

    conn.execute(
        'UPDATE cars SET brand = ?, model = ?, description = ?, year = ?, '
        'image_url = ? WHERE id = ?',
        (brand, model, description, year, image_url, id),
    )
    conn.commit()
    conn.close()
    return redirect(url_for('cars'))

  car = conn.execute('SELECT * FROM cars WHERE id = ?', (id,)).fetchone()
  conn.close()

  if car is None:
    return 'Автомобіль не знайдено', 404

  return render_template('edit_car.html', car=car)


@app.route('/car/<int:id>')
def car_detail(id):
  conn = get_db_connection()
  car = conn.execute('SELECT * FROM cars WHERE id = ?', (id,)).fetchone()
  conn.close()

  if car is None:
    return 'Автомобіль не знайдено', 404

  return render_template('car_detail.html', car=car)


@app.route('/delete/<int:id>', methods=['POST'])
def delete_car(id):
  conn = get_db_connection()
  conn.execute('DELETE FROM cars WHERE id = ?', (id,))
  conn.commit()
  conn.close()
  return redirect(url_for('cars'))


if __name__ == '__main__':
  init_db()
  app.run(debug=True)