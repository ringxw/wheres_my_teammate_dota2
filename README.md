# wheres_my_teammate_dota2
To setup virtual environment for the flask application
for the first time:
sudo pip install virtualenv
virtualenv venv

You can then install flask

source venv/bin/activate
pip install -r requirement.txt

After this you should see your shell under venv

(venv) nans-air:src njiang

Try run python and see if flask is been imported

You should not get any error

(venv) nans-air:wheres_my_teammate_dota2 njiang$ python

Python 2.7.6 (default, Sep  9 2014, 15:04:36)

[GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.39)] on darwin

Type "help", "copyright", "credits" or "license" for more information.

>>> import flask

>>>

To run the application
python app.py
