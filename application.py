import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if session.get("userId") is None:
        session["userId"] = 0
    userInfo = db.execute("SELECT * FROM users WHERE id = :id", {"id": session["userId"]}).fetchone()
    return render_template("index.html", userInfo=userInfo)

@app.route("/api/<string:isbn>")
def isbnApi(isbn):
    return render_template("isbnApi.html", isbn=isbn)

@app.route("/registration", methods=["POST"])
def registration():
    # Get username from registration form; strip leading and trailing spaces
    username = request.form.get("username").strip()
    # If username is blank, return error page
    if username == "":
        return render_template("error.html", message="Please enter a username.")
    # If username contains spaces, return error page
    if (" " in username) == True:
        return render_template("error.html", message="Please choose a username without spaces.")
    # If username already exists, return error page; first check if there is a users table
    if engine.dialect.has_table(engine, "users"):
        if db.execute("SELECT username FROM users WHERE lower(username) = :username",
                {"username": username.lower()}).fetchone() is not None:
            return render_template("error.html", message="Username already exists.")

    # TODO: Anything else constitute an invalid username?

    # If username passes validation, add new user's information to database
    # Create a users table if one doesn't already exist
    if not engine.dialect.has_table(engine, "users"):
        metadata = MetaData(engine)
        Table("users", metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(30)),
            Column("username", String(30)),
            Column("password", String(20)))
        metadata.create_all()
    # Insert new user's information into table
    name = request.form.get("name")
    password = request.form.get("password")
    db.execute("INSERT INTO users (name, username, password) VALUES (:name, :username, :password)",
            {"name": name, "username": username, "password": password})
    db.commit()
    # Return registered page after user is registered successfully
    return render_template("registered.html")

@app.route("/login", methods=["POST"])
def login():
    # Get username from registration form; strip leading and trailing spaces
    username = request.form.get("username").strip()
    # If username is blank, return error page
    if username == "":
        return render_template("error.html", message="Please enter a username.")
    # Check if username exists; first check if a users table exists
    if engine.dialect.has_table(engine, "users"):
        # Retrieve the user's data if there is any via username; use lower() for string comparing
        userInfo = db.execute("SELECT * FROM users WHERE lower(username) = :username",
                {"username": username.lower()}).fetchone()
        # If username exists in database
        if userInfo is not None:
            # Check that password matches database's
            password = request.form.get("password")
            if userInfo.password == password:
                # Set the session for the user
                if session.get("userId") is None:
                    session["userId"] = 0
                session["userId"] = userInfo.id
                # Return search page
                return redirect(url_for("search"))
            else:
                return render_template("error.html", message="Password is incorrect.")
        else:
            return render_template("error.html", message="Username does not exist.")
    else:
        return render_template("error.html", message="Username does not exist.")

@app.route("/logout", methods=["POST"])
def logout():
    # Unset the user's session
    if session.get("userId") is None:
        session["userId"] = 0
    else:
        session["userId"] = 0
    return render_template("loggedOut.html")

@app.route("/search", methods=["POST", "GET"])
def search():
    if request.method == "POST":
        # Get search criteria from form, stripping leading and trailing spaces
        isbn = request.form.get("isbn").strip()
        title = request.form.get("title").strip()
        author = request.form.get("author").strip()
        # If user entered no criteria, return a message
        if isbn is "" and title is "" and author is "":
            return render_template("search.html", message="Please enter a search criteria.")
        # Query for criteria
        isbnQuery = []
        titleQuery = []
        authorQuery = []
        # Check if a books table exists
        if engine.dialect.has_table(engine, "books"):
            # For each query, check that criteria is not empty as to not return everything
            if isbn is not "":
                isbnQuery = db.execute("SELECT * FROM books WHERE lower(isbn) LIKE :isbn",
                        {"isbn": "%"+isbn.lower()+"%"}).fetchall()
            if title is not "":
                titleQuery = db.execute("SELECT * FROM books WHERE lower(title) LIKE :title",
                        {"title": "%"+title.lower()+"%"}).fetchall()
            if author is not "":
                authorQuery = db.execute("SELECT * FROM books WHERE lower(author) LIKE :author",
                        {"author": "%"+author.lower()+"%"}).fetchall()
        # If the searching returned empty, return a message
        if not isbnQuery and not titleQuery and not authorQuery:
            return render_template("search.html", message="Your search returned no results.")
        else:
            return render_template("search.html", isbnQuery=isbnQuery, titleQuery=titleQuery, authorQuery=authorQuery)
    else:
        return render_template("search.html")

@app.route("/book/<int:bookId>", methods=["POST", "GET"])
def book(bookId):
    if request.method == "POST":

        # TODO: Check that user didn't already comment on this book

        # Insert new review into database; create a reviews table if doesn't exist already
        if not engine.dialect.has_table(engine, "reviews"):
            metadata = MetaData(engine)
            Table("reviews", metadata,
                Column("id", Integer, primary_key=True),
                Column("userId", Integer),
                Column("review", String(500)),
                Column("bookId", Integer))
            metadata.create_all()
        # Retrieve review from form, stripping away leading and trailing spaces
        review = request.form.get("review").strip()
        db.execute("INSERT INTO reviews (userId, review, bookId) VALUES (:userId, :review, :bookId)",
                {"userId": session["userId"], "review": review, "bookId": bookId})
        db.commit()
        return render_template("book.html")
    else:
        bookInfo = db.execute("SELECT * FROM books WHERE id = :bookId", {"bookId": bookId}).fetchone()
        return render_template("book.html", book=bookInfo)
