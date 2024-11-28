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

# mongodb for mac, remote access
TEMP PASSWORD FOR TESTING: mongoPASSWORD

We will be using Atlas for our service. Provided over AWS. 
1. execute the command first
python -m pip install "pymongo[srv]"==3.12. This driver will be used for Atlas 
2. Following will be an example of how to connection
mongodb+srv://kc0000:PASSWORD@cluster0.q7jza.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
I will not be sharing the username/password here. 
replace kc0000 and PASSWORD accordingly
3. You can need to set these variables. One way is to add this to the bash file of the enviroment. 
export CLOUD_MONGO="CLOUD"
export GAME_MONGO_PW="PASSWORD"  # Replace with your actual password
4. You will probably need to update your CA certificate to verify the ssl connection. You can also manually set ssl=False in the connection URL, which I do not recommend.
pip install --upgrade certifi
/Applications/Python\ 3.12/Install\ Certificates.command 
5.
./local.sh
You should be good to go