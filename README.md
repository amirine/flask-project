# flask-project

Getting Started
-------------------------

To start the project some environment variables are needed.

Secret key variable:

```sh
SECRET_KEY=
```

<code>SECRET_KEY</code> may not be filled in as it has a default value in project's code, still that's not a good
practice for the production, so please enter this value.

Database variables:

```sh
DATABASE_URL=
```

Variable for Elasticsearch:

```sh
ELASTICSEARCH_URL=
```

Usually <code>ELASTICSEARCH_URL=http://localhost:9200 </code> is taken.

Variable for Redis:

```sh
REDIS_URL=
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

Please copy .env.example content into .env file and fill the required credentials.

Now you can run <code>flask run</code> command and open up your app running on localhost.

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

How to use API
-------------------------

Most of API requests are available only for authorized users, so please in order to use project's API properly create a
user account.

Generally project's REST API functionality includes:

1. Getting list of users (available for authorized users only).
2. Getting information of a specific user (available for authorized users only).
3. Getting followers of a specific user (available for authorized users only).
4. Getting followed of a specific user (available for authorized users only).
5. Creating a user account (available for all the users).
6. Updating a user account (available for authorized user: users have access to their own info only).

As it was mentioned, most of the requests require authorization, actually authorization token. So to use all the API
functionality generate a token first: just run the command below:

```sh
curl -X POST http://localhost:5000/api/tokens -u "username:password" 
```

To retrieve users stored in database make <code>GET</code> request to http://localhost:5000/api/users:

```sh
curl http://localhost:5000/api/users -H "Authorization: Bearer <token>"
```

To get information for a specific user run:

```sh
curl http://localhost:5000/api/users/1 -H "Authorization: Bearer <token>"
```

To get followers and followed for a specific user run:

```sh
curl http://localhost:5000/api/users/1/followers -H "Authorization: Bearer <token>"
curl http://localhost:5000/api/users/1/followed -H "Authorization: Bearer <token>"
```

To register a new user account use a <code>POST</code> request:

```sh
curl -X POST http://localhost:5000/api/users -H "Content-Type: application/json" -H "Authorization: Bearer <token>" -d '{"username": "alice", "password": "dog", "email": "alice@example.com"}'
```

To modify an existing user info run a <code>PUT</code> request:

```sh
curl -X PUT http://localhost:5000/api/users/2 -H "Content-Type: application/json" -H "Authorization: Bearer <token>" -d '{"about_me": "about alice"}'
```

Clients can also invalidate the token by running:

```sh
curl -X DELETE http://localhost:5000/api/tokens -H "Authorization: Bearer <token>"
```
