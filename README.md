__to activate virtual environment__
- source <path>/bin/activate in linux/mac
- __to create a project__
- python3 manage.py startproject  <name of the project>
- __to create a app__
- python3 manage.py startapp  <name of the app>
- __to see more command options__
- python3 manage.py --help
`__init__.py` helps interpretor regognize folder as python module
__to make migrations__
- python3 manage.py makemigrations
 __to commit migrations to database__
- python3 manage.py migrate
__to run application server__
- python3 manage.py runserver <port number: default: 8000>

__to create superuser__
-`python3 manage.py createsuperuser`