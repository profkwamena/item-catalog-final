# udacity_fullstack_project3
udacity Full Stack Web Developer Nanodegree Project 3 - Item Catalog. This project was inspired by Allan Breyes's fullstack project on GitHub  https://github.com/allanbreyes/udacity-full-stack

The libraries flask-seasurf and GitHub-Flask are needed
#Files
* application.py -- python script with flask main application
* catalog.db -- sqlite database for item catalog
* database_setup.py -- pathon script for sqlalchemy database schema
* addData.py -- python script to polulate database with sample data
* static/styles.css -- css style for all views
* templates/additem.html -- template for item add view
* templates/catalog.html -- template for catalog and category overview
* templates/deleteitem.html -- template for item delete view
* templates/edititem.html -- template for item edit view
* templates/item.html -- template for item view
* templates/header.html -- header for all views
* templates/footer.html -- footer for all views

# The following programs are needed to run

* python 2.7.1
* [flask](http://flask.pocoo.org) 
* [sqlalchemy](http://www.sqlalchemy.org)
* [SeaSurf](https://flask-seasurf.readthedocs.org)
* [GitHub-Flask](https://github-flask.readthedocs.org/en/latest/)

#Setup
for GitHub OAuth the Client ID and Client Secret have to be changed in application.py: 

```python
app.config['GITHUB_CLIENT_ID'] = 'XXX'
app.config['GITHUB_CLIENT_SECRET'] = 'YYY'
```

for session managment you should change the secret key of the app:
```python
app_secret = 'ZZZ'
```

the callback url should be something like  https://dev.kwamena.de/github-callback and can be configured in the beginning of application.py:

```python
github_callback_url = "https://dev.kwamena.de/github-callback"
```

 To reset database:
```bash
[kwamena@discodia:catalog] rm catalog.db
[kwamena@discodia:catalog] python addData.py
```

##To use
start application
```bash
[kwamena@discodia:catalog] python application.py
```

##Example
https://dev.kwamena.de (login needed)

