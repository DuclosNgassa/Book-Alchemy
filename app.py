from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, flash
import os
from data_models import db, Author, Book

app = Flask(__name__)

app.secret_key = 'my_flash_secret_key_for_book_alchemy'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data/library.sqlite')

# connect the Flask app to the flask-sqlalchemy code.
db.init_app(app)


# with app.app_context():
#    db.create_all()


@app.route('/')
def home():
    sort_by = request.args.get('sort', 'title')
    search_query = request.args.get('search', '').strip()

    statement = db.select(Book)

    # Apply search
    if search_query:
        search_term = f"%{search_query}%"
        statement = statement.where(Book.title.ilike(search_term))

    # Apply sorting
    if sort_by == 'author':
        statement = statement.join(Author).order_by(Author.name)
    elif sort_by == 'publication_year':
        statement = statement.order_by(Book.publication_year)
    else:
        statement = statement.order_by(Book.title)

    books = db.session.scalars(statement).all()

    no_results_message = None
    if search_query and not books:
        no_results_message = f"No books matched your search for '{search_query}'."

    return render_template(
        "home.html",
        books=books,
        current_sort=sort_by,
        search_query=search_query,
        no_results_message=no_results_message
    )


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    success_message = None

    if request.method == 'POST':
        name = request.form.get('name')
        birth_date_str = request.form.get('birth_date')
        date_of_death_str = request.form.get('date_of_death')

        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()

        date_of_death = None
        if date_of_death_str and date_of_death_str.strip():
            date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date()

        author = Author(
            name=name,
            birth_date=birth_date,
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
        publication_year = datetime.strptime(request.form['publication_year'], '%Y-%m-%d')
        author_id = int(request.form['author_id'])
        rating_str = request.form.get('rating')
        rating = int(rating_str) if rating_str else None

        book = Book(
            title=title,
            isbn=isbn,
            publication_year=publication_year,
            author_id=author_id,
            rating=rating,
        )

        db.session.add(book)
        db.session.commit()
        success_message = f"Book '{title}' was successfully added!"

    authors = db.session.scalars(db.select(Author)).all()
    return render_template('add_book.html', authors=authors, success_message=success_message)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id: int):
    book = db.session.get(Book, book_id)

    if book:
        author = book.author
        title = book.title

        db.session.delete(book)
        db.session.commit()

        remaining_books_count = db.session.scalar(
            db.select(db.func.count(Book.id)).where(Book.author_id == author.id)
        )

        if remaining_books_count == 0:
            author_name = author.name
            db.session.delete(author)
            db.session.commit()
            flash(
                f"Book '{title}' and author '{author_name}' were successfully deleted because they had no remaining books.",
                "success")
        else:
            flash(f"Book '{title}' was successfully deleted!", "success")

    else:
        flash("Book not found.", "danger")

    return redirect(url_for('home'))


@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = db.session.get(Book, book_id)
    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for('home'))
    return render_template('book_detail.html', book=book)


@app.route('/author/<int:author_id>')
def author_detail(author_id):
    author = db.session.get(Author, author_id)
    if not author:
        flash("Author not found.", "danger")
        return redirect(url_for('home'))
    return render_template('author_detail.html', author=author)


@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    author = db.session.get(Author, author_id)

    if author:
        author_name = author.name
        db.session.delete(author)
        db.session.commit()

        flash(f"Author '{author_name}' and all associated books were successfully deleted!", "success")
    else:
        flash("Author not found.", "danger")

    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run()
