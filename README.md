Purpose of Project:

    The purpose of this project is to establish a Flask Rest API to work in
    parallel with the CryptoPlatformFE (Front End). This rest API stores
    user information in a MongoDB database and gives the ability to not only
    store user information, but for that information to be retrieved for use
    on the front end. This rest API also makes calls to other API's such as
    Binance to retrieve real time market data for analysis in investment choices.
    Other libraries that have been added include PassLib which adds a layer of
    encryption for user passwords.

The Binance and NewsAPI keys needed to run the program are private, please contact
me and I can provide those for use in running the app.

How to Run (Windows):

1. Install requirements by runnining "npm i" in cmd.

2. Activate the virtual enviroment.
   In the cmd, run "venv\Scripts\activate.bat"

3. Set Flask App to app.py.
   In cmd, run "set FLASK_APP=app.py"

4. Run the Flask App.
   In cmd, run "flask run"

How to Run (Mac OS):
