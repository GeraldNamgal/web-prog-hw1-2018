import os

import requests, json
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
    # Retrieve user info if a user is signed in
    userInfo=[]
    if engine.dialect.has_table(engine, "users"):
        userInfo = db.execute("SELECT * FROM users WHERE id = :id", {"id": session["userId"]}).fetchone()
    # Return index/main page
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
    # if request method was GET or anything else besides POST
    else:
        return render_template("search.html")

@app.route("/book/<int:bookId>", methods=["POST", "GET"])
def book(bookId):
    if request.method == "POST":
        # Retrieve the session "userId" to see who is signed in
        if session.get("userId") is None:
            session["userId"] = 0
        # If a user isn't signed in, return a must-sign-in error page
        if session["userId"] == 0:
            return render_template("reviewAlert.html", message="Please sign in to review this book.",
                                    alert="Error", bookId=bookId)
        # If user already reviewed this book, return an error page
        if engine.dialect.has_table(engine, "reviews"):
            if db.execute("SELECT * FROM reviews WHERE bookId = :bookId AND reviewer = :reviewer",
                            {"bookId": bookId, "reviewer": session["userId"]}).rowcount != 0:
                return render_template("reviewAlert.html", message="You already reviewed this book.",
                                        alert="Error", bookId=bookId)
        # Insert new review into database; create a reviews table first if it doesn't exist already
        if not engine.dialect.has_table(engine, "reviews"):
            metadata = MetaData(engine)
            Table("reviews", metadata,
                Column("id", Integer, primary_key=True),
                Column("reviewer", Integer),
                Column("username", String(30)),
                Column("rating", Integer),
                Column("comment", String(500)),
                Column("bookid", Integer))
            metadata.create_all()
        # Retrieve rating and comment from form, stripping away leading and trailing spaces
        rating = request.form.get("rating")
        comment = request.form.get("comment").strip()
        # If user neither entered a comment or rating, return an error page
        if rating is None and comment == "":
            return render_template("reviewAlert.html", message="Please enter a rating and/or comment.",
                                    alert="Error", bookId=bookId)
        # Retrieve user's username
        username = ""
        if engine.dialect.has_table(engine, "users"):
            username = db.execute("SELECT * FROM users WHERE id = :reviewerId",
                                    {"reviewerId": session["userId"]}).fetchone().username
        # Inserting review; check if rating is not None as to not return a NoneType insert error
        if rating is not None:
            db.execute("INSERT INTO reviews (reviewer, rating, comment, username, bookid) VALUES (:reviewer, :rating, :comment, :username, :bookid)",
                        {"reviewer": session["userId"], "rating": int(rating), "comment": comment, "username": username, "bookid": bookId})
        else:
            db.execute("INSERT INTO reviews (reviewer, comment, username, bookid) VALUES (:reviewer, :comment, :username, :bookid)",
                        {"reviewer": session["userId"], "comment": comment, "username": username, "bookid": bookId})
        db.commit()
        # Return an alert page that review was successfully submitted
        return render_template("reviewAlert.html", message="Your review has been submitted.",
                                alert="Success", bookId=bookId)
    # If request method was GET or anything else besides POST
    else:
        # Retrieve book information
        bookInfo = db.execute("SELECT * FROM books WHERE id = :bookId", {"bookId": bookId}).fetchone()
        # If book is not in database, return a book-unavailable error
        if bookInfo is None:
            return render_template("error.html", message="That book is unavailable.")
        # Retrieve reviews for the book
        reviews = []
        if engine.dialect.has_table(engine, "reviews"):
            reviews = db.execute("SELECT * FROM reviews WHERE bookid = :bookId", {"bookId": bookId}).fetchall()
        # Get Goodreads ratings and reviews info
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "vH8L4fXjVtQkhdNVCeRQ", "isbns": bookInfo.isbn})
        # Return the book page for the book
        if res.status_code != 404:
            goodReadsData = json.loads(res.text)
            # Return Goodreads data with book page if api request was found (no 404 error)
            return render_template("book.html", book=bookInfo, reviews=reviews, res=res, goodReadsData=goodReadsData)
        else:
            # Don't return Goodreads data with book page if api request was not found (404 error)
            return render_template("book.html", book=bookInfo, reviews=reviews, res=res)
