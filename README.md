# wheres_my_teammate_dota2
## To setup virtual environment for the flask application for the first time:

*sudo pip install virtualenv*

Then, run virtual env to create the python virtual environment so it doesn't mess up your computer's default environment 

*virtualenv venv*

You can then install flask after activates virtualenv, which is what will be used here

*source venv/bin/activate*

*pip install -r requirement.txt*

After this you should see your shell that looks like this

*(venv)* **nans-air:src njiang**

Try run python and see if flask is been imported, you should not get any error
```
(venv) nans-air:wheres_my_teammate_dota2 njiang$ python
Python 2.7.6 (default, Sep  9 2014, 15:04:36)
[GCC 4.2.1 Compatible Apple LLVM 6.0 (clang-600.0.39)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> import flask
>>>
```

After the enviornment is set up ,to run the application

**python app.py**
