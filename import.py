import csv
import os

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    # Creating a table (referenced from: https://www.pythonsheets.com/notes/python-sqlalchemy.html,
    #                   https://stackoverflow.com/questions/33053241/sqlalchemy-if-table-does-not-exist,
    #                   and http://docs.sqlalchemy.org/en/latest/core/metadata.html)
    # If table doesn't already exist then create it
    if not engine.dialect.has_table(engine, "books"):
        metadata = MetaData(engine)
        Table("books", metadata,
            Column("id", Integer, primary_key=True),
            Column("isbn", String(13)),
            Column("title", String(4805)),
            Column("author", String(50)),
            Column("year", Integer))
        metadata.create_all()
        # Inserting into table
        with open("books.csv") as f:
            reader = csv.reader(f)
            # Skip the field names
            next(reader)
            for isbn, title, author, year in reader:
                db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                        {"isbn": isbn, "title": title, "author": author, "year": year})
            db.commit()
    # If table already exists then "books.csv" was already loaded
    else:
        print("A \"books.csv\" table already exists.")

if __name__ == '__main__':
    main()
