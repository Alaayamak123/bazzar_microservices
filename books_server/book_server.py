from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Float, Integer, String, ForeignKey, or_
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

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


class Catalog(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)


class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    count: Mapped[int] = mapped_column(Integer, default=1)
    price: Mapped[float] = mapped_column(Float, default=0)
    catalog_id: Mapped[int] = mapped_column(ForeignKey(Catalog.id))
    catalog: Mapped[Catalog] = relationship(Catalog)

with app.app_context():
    db.create_all()
    
    
def log(message):
    with open('./catalog_log.txt', 'a') as logger:
        logger.write(f'{message}\n')

@app.get('/catalogs')
def get_all_catalogs():
    try:
        catalogs = db.session.execute(db.select(Catalog).order_by(Catalog.id)).scalars()
        catalogs_list = [{ 'id': catalog.id,'name': catalog.name } for catalog in catalogs]
        
        log(f'make GET request on /catalogs > get all catalogs {datetime.now()}')
        return jsonify({
            'catalogs': catalogs_list
        })

    except Exception as e:
        json_response = jsonify({
            'error': e.__str__()
        })
        return make_response(json_response,500)

@app.post('/catalogs')
def create_catalog():
    try:
        name = request.form['name']
    except:
        json_response = jsonify({
            'error': 'no name was provided'
        })
        return make_response(json_response, 400)

    catalog = Catalog(
        name=name
    )

    db.session.add(catalog)
    db.session.commit()

    log(f'make POST request on /catalogs > add new catalog {datetime.now()}')
    return jsonify({
        'success': True,
        'catalog': catalog.name,
        'catalog_id': catalog.id,
    })


@app.get('/books')
def get_all_books():
    try:
        books = db.session.execute(db.select(Book).order_by(Book.id)).scalars()
        books_list = [{'id': book.id, 'name': book.name, 'count': book.count, 'price': book.price} for book in books]
        return jsonify({
            'books': books_list
        })

    except Exception as e:
        json_response = jsonify({
            'error': e.__str__()
        })
        return make_response(json_response, 500)



@app.post('/books')
def create_book():
    try:
        name = request.form['name']
        catalog = request.form['catalog']
        count = int(request.form['count'])
        price = int(request.form['price'])
    except Exception as exc:
        json_response = jsonify({
            'error': exc.__str__()
        })
        return make_response(json_response, 400)

    book = Book(
        name=name,
        catalog_id=catalog,
        count=count,
        price=price,
    )

    db.session.add(book)
    db.session.commit()

    return jsonify({
        'success': True,
        'book': book.name,
        'book_id': book.id,
    })

@app.get('/books/search/<string:name>')
def search_books(name):
    books = db.session.execute(db.select(Book).filter_by(name=name)).scalars()
    books_list = [{'name': book.name,'proce': book.price, 'id': book.id} for book in books]
    return jsonify({
        'books': books_list
    })

@app.get('/books/find')
def get_book_by_name():
    search_string = request.args.get('name','')
    books = db.session.query(Book).filter(or_(Book.name.like(f"%{search_string}%"))).all()

    book_info = [{
        'id': book.id,
        'name': book.name,
        'count': book.count
    } for book in books]
    return jsonify({
        'books': book_info
    })


@app.get('/books/<int:id>')
def get_book(id):
    try:
        book = Book.query.filter_by(id=id).first()
        book_info = dict({
            'id': book.id,
            'name': book.name,
            'count': book.count
        })
        return jsonify({
            'books': book_info
        })
    except Exception as exc:
        json_response = jsonify({
            'error': exc.__str__()
        })

        return make_response(json_response,404)
    
@app.put('/books/<int:id>/count/increase')
def increase_book_stock(id):   
    try:
        book = Book.query.filter_by(id=id).first()
        book.count = book.count + 1
        db.session.commit()
        
        return jsonify({
            'count': book.count,
        })
    except Exception as e:
        json_response = jsonify({
            'error': e.__str__()
        })

        return make_response(json_response,404)
    
@app.put('/books/<int:id>/count/decrease')
def decrease_book_stock(id):   
    try:
        book = Book.query.filter_by(id=id).first()
        book.count = book.count - 1
        db.session.commit()
        
        return jsonify({
            'count': book.count,
        })
    except Exception as e:
        json_response = jsonify({
            'error': e.__str__()
        })

        return make_response(json_response,404)
    
@app.put('/books/<int:id>/price')
def update_book_price(id):   
    try:
        price = float(request.form['price'])
        
        book = Book.query.filter_by(id=id).first()
        book.price = price
        db.session.commit()
        
        return jsonify({
            'price': book.price,
        })
    except Exception as e:
        json_response = jsonify({
            'error': e.__str__()
        })

        return make_response(json_response,404)
    
    
@app.get('/books/<int:id>/stock/availability')
def stock_availability(id):
    book = Book.query.filter_by(id=id).first()
    if book.count == 0:
        json_response = jsonify({
            'success': False,
            'message': 'Out of stock'
        })
        return make_response(json_response,403)

    return jsonify({
        'success': True,
        'left': book.count
    })
app.run('0.0.0.0', port=4000, debug=True)
