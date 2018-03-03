import csv
import os

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    # Create tables (referenced from: https://www.pythonsheets.com/notes/python-sqlalchemy.html,
    #                https://stackoverflow.com/questions/33053241/sqlalchemy-if-table-does-not-exist,
    #                and http://docs.sqlalchemy.org/en/latest/core/metadata.html)
    # Create books table if it doesn't already exist
    if not engine.dialect.has_table(engine, "books"):
        metadata = MetaData(engine)
        Table("books", metadata,
            Column("id", Integer, primary_key=True),
            Column("isbn", String(13)),
            Column("title", String(4805)),
            Column("author", String(50)),
            Column("year", Integer))
        metadata.create_all()
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
            Column("name", String(30)),
            Column("username", String(30)),
            Column("password", String(20)))
        metadata.create_all()
    # Create a reviews table if it doesn't exist already
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

if __name__ == '__main__':
    main()
