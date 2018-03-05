# Project 1

"import.py" uploads the "books" data to my Heroku database as specified in the spec.
It also creates tables for the "users" and "reviews" tables, the only other two
tables in my project. My "import.py" file does take a minute or two to load in the
books data so the command line may hang for a bit while it's loading. My Heroku URI
is contained in the same folder as "import.py" in a file called "herokuURI.txt" if it
is needed.

For the most part, my comments, error handling, and design in general are pretty
self-explanatory and contextual. "application.py" contains all of my routes and their
functions. The "templates" folder contains all of my templates or html files.
"index.html" contains all of the html code for my Home or main page. On my main page,
you'll see the login and registration forms. The navigation, including the logout
button are located at the top of each page. Some links will appear or disappear
depending on whether a user is logged in or not. For example, the "Log Out" button
only appears after a user logs in. "search.html" contains the html code for my search
page where users can search for a book by title, author, or isbn. A list based on
their query populates there and users can click on a link to a book page. "book.html"
contains all html code for displaying information on the book of their choosing
including reviews as per the spec. I used "alert.html" as the only template to display
when handling errors throughout the project. Finally, my styling can be found in the
html files themselves and in a css file called "styles.css" which is located in a
folder called "css" which itself is located in a folder called "static".
