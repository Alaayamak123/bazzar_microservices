from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Integer, String, ForeignKey, or_, JSON, DATETIME
from sqlalchemy.orm import Mapped, mapped_column
import requests

class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)

# Set the database URI to the path within the Docker volume
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////data/project.db"

# Other configurations
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# initialize the app with the extension
db.init_app(app)


class Order(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_data: Mapped[dict] = mapped_column(JSON)
    purchase_date: Mapped[datetime] = mapped_column(DATETIME)
    count: Mapped[int] = mapped_column(Integer)


with app.app_context():
    db.create_all()


@app.post('/purchase/<int:id>')
def purchase_book(id):
    av_response = requests.get(f'http://172.18.160.1:4000/books/{id}/stock/availability')
    if av_response.status_code == 200:
        decrease_response = requests.put(f'http://172.18.160.1:4000/books/{id}/count/decrease')
        if decrease_response.status_code == 404:
            return make_response(decrease_response.json(),404)
        book_info = requests.get(f'http://172.18.160.1:4000/books/{id}')
        print(book_info)
        book = book_info.json()
        
        order = Order(book_data=book,purchase_date=datetime.now(),count=1)
        db.session.add(order)
        db.session.commit()
        
        with open('./order_log.txt', 'a') as log:
            log.write(f'user purchased book {book["books"]["name"]} at {datetime.now()}, in stock left {decrease_response.json()["count"]}\n')
        
        json = jsonify({
            'order': dict({
                'book_info': book,
                'purchase_date': datetime.now(),
                'count': 1,
            })
        })
        return json
    else:
        json_response = av_response.json()
        make_response(json_response,403)


app.run('0.0.0.0', port=5000, debug=True)
