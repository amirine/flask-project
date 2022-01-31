# flask-project

Getting Started
-------------------------

To start the project some environment variables are needed.

Flask project setup variables:

```sh
FLASK_APP=blog.py
FLASK_DEBUG=
FLASK_ENV=
SECRET_KEY=
```

Note that the variable <code>FLASK_APP=blog.py</code> has a constant value based on project's file name, <code>
FLASK_DEBUG</code> variable, that indicates whether debug mode is available, can be set to 0 or 1. <code>
SECRET_KEY</code> may not be filled in as it has a default value in project's code, still that's not a good practice for
the production, so please enter this value.

Database variables:

```sh
DATABASE_URL=
```

Variables for email support:

```sh
MAIL_SERVER=
MAIL_PORT=
MAIL_USE_TLS=
MAIL_USERNAME=
MAIL_PASSWORD=
```

Project's functionality includes password reset and errors sending to the admin email, so all these values are also
required.

Dynamic translation for posts is also provided, therefore one more environmental variable required:

```sh
MS_TRANSLATOR_KEY=
```

To set translator key specified above visit [Azure](https://portal.azure.com/) website. Before you can use the Microsoft
Translator API, you will need to get an account there. Once you have the Azure account, click on *Create a resource*
link and select Translator resource. Fill out the form and create a resource. Now you can find 2 keys in the *Keys and
Endpoint* section, just copy either of them.

Please copy .flaskenv.example content into .flaskenv file and fill the required credentials.

Now you can run <code>flask run</code> command and open up your app running on <code>http://localhost:5000/ </code>.

Database setup
-------------------------

To create the migration repository for the project just run:

```sh
flask db init
```

and to generate an automatic migration run:

```sh
flask db migrate -m "<some migration info>"
```

To apply the changes to the database, the following flask command must be used:

```sh
flask db upgrade
```

You also have a <code>flask db downgrade</code> command, which undoes the last migration, don't forget about it and use
where needed.

Testing
-------------------------

Project provides developers with some custom tests listed in <code>tests.py</code> file, so to run them enter:

```sh
python3 tests.py
```

You can always add some extra tests to the project and check needed functionality.

Languages setup
-------------------------

This Flask Blog project supports 2 languages: English and Russian. All the needed translations are displayed in <code>
messages.po</code> file. But one common situation when working with translations is that you may want to make some
changes in templates, then comes a need of translations update.

Current project supports 3 actions: initializing new language

```sh
flask translate init <LANG>
```

updating all language repositories

```sh
flask translate update
```

and compiling all language repositories

```sh
flask translate compile
```

Just run the required command and get the result.
