import csv
import os

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Global variables
isbnLen = 14
titleLen = 1000
authorLen = 50
nameLen = 30
usernameLen = 30
passwordLen = 500
commentLen = 1000

def main():
    # Create tables (referenced from: https://www.pythonsheets.com/notes/python-sqlalchemy.html,
    #                https://stackoverflow.com/questions/33053241/sqlalchemy-if-table-does-not-exist,
    #                and http://docs.sqlalchemy.org/en/latest/core/metadata.html)
    # Create books table if it doesn't already exist
    if not engine.dialect.has_table(engine, "books"):
        metadata = MetaData(engine)
        Table("books", metadata,
            Column("id", Integer, primary_key=True),
            Column("isbn", String(isbnLen)),
            Column("title", String(titleLen)),
            Column("author", String(authorLen)),
            Column("year", Integer))
        metadata.create_all()
        # Check that table was created
        if not engine.dialect.has_table(engine, "books"):
            print("Database error occurred: could not create table.")
        # Insert books.csv data into books table
        with open("books.csv") as f:
            reader = csv.reader(f)
            # Skip the field names
            next(reader)
            for isbn, title, author, year in reader:
                db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                            {"isbn": isbn, "title": title, "author": author, "year": year})
            db.commit()
    # Create a users table if one doesn't exist yet
    if not engine.dialect.has_table(engine, "users"):
        metadata = MetaData(engine)
        Table("users", metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(nameLen)),
            Column("username", String(usernameLen), nullable=False),
            Column("password", String(passwordLen)))
        metadata.create_all()
        # Check that table was created
        if not engine.dialect.has_table(engine, "users"):
            print("Database error occurred: could not create table.")
    # Create a reviews table if it doesn't exist already
    if not engine.dialect.has_table(engine, "reviews"):
        metadata = MetaData(engine)
        Table("reviews", metadata,
            Column("id", Integer, primary_key=True),
            Column("reviewer", Integer, nullable=False),
            Column("username", String(usernameLen)),
            Column("rating", Integer),
            Column("comment", String(commentLen)),
            Column("bookid", Integer, nullable=False))
        metadata.create_all()
        # Check that table was created
        if not engine.dialect.has_table(engine, "reviews"):
            print("Database error occurred: could not create table.")

if __name__ == '__main__':
    main()
