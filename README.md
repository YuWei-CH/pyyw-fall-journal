# flask-api
An example flask rest API server.

To build production, type `make prod`.

To create the env for a new developer, run `make dev_env`.


# mongodb for mac, brew installation
brew update
brew tap mongodb/brew
brew install mongodb-community@6.0

start: brew services start mongodb/brew/mongodb-community@6.0
stop:  brew services stop mongodb/brew/mongodb-community@6.0

to use mongoDB, you connect to the client via  connect_db() from data/db_connect: client= connect_db()
Then, replace the existing functions in people.py...roles.py....text.py...etc...to CRUD data from corresponding collection in the client (of selected parameter.)
