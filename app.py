from datetime import datetime

from flask import Flask, render_template, request
import os
from data_models import db, Author, Book

app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data/library.sqlite')

# connect the Flask app to the flask-sqlalchemy code.
db.init_app(app)
#with app.app_context():
#    db.create_all()


@app.route('/')
def home():
    sort_by = request.args.get('sort','title')
    statement = db.select(Book)
    if sort_by == 'author':
        statement = statement.join(Author).order_by(Author.name)
    elif sort_by == 'publication_year':
        statement = statement.order_by(Book.publication_year)
    else:
        statement = statement.order_by(Book.title)

    books = db.session.scalars(statement).all()

    return render_template("home.html", books=books)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    success_message = None
    if request.method == 'POST':
        name = request.form['name']
        birthdate_str = request.form['birthdate']
        date_of_death_str=request.form['date_of_death']
        birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d')
        date_of_death = None
        if date_of_death_str:
            date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d')

        author = Author(
            name=name,
            birth_date=birthdate,
            date_of_death=date_of_death
        )

        db.session.add(author)
        db.session.commit()
        success_message = f"Author '{name}' was successfully added!"

    return render_template('add_author.html', success_message=success_message)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    success_message = None
    if request.method == 'POST':
        title = request.form['title']
        isbn = request.form['isbn']
        publication_year= datetime.strptime(request.form['publication_year'], '%Y-%m-%d')
        author_id=int(request.form['author_id'])

        book = Book(
            title=title,
            isbn=isbn,
            publication_year=publication_year,
            author_id=author_id
        )

        db.session.add(book)
        db.session.commit()
        success_message = f"Book '{title}' was successfully added!"

    authors = db.session.scalars(db.select(Author)).all()
    return render_template('add_book.html', authors=authors, success_message=success_message)


if __name__ == '__main__':
    app.run()

