# -*- coding: utf-8 -*-
import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash


app = Flask(__name__)

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY="development key",
    USERNAME='admin',
    PASSWORD='default'
                  ))
#Global Vars
POSITIONS = ['carry', 'mid', 'off', 'support', 'hard_support']
REGIONS = ['usw', 'use', 'china']
LANGUAGES = ['English','Russian','Chinese']

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    #should return results html here
    positions = ', '.join(_parse_check_box(POSITIONS))
    regions = ', '.join(_parse_check_box(REGIONS))
    languages = ', '.join(_parse_check_box(LANGUAGES))
    my_results = 'Player {0}, mmr {1}, plays positions {2}, plays on regions {3}, speaks {4}, looking for a teammate!!'.format(request.form['username'], request.form['mmr'], positions, regions, languages)
    return my_results

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #if request.form['username'] != app.config['USERNAME']:
        if request.form['username'] != 'OSfrog':
            error = 'Invalid username'
        #elif request.form['password'] != app.config['PASSWORD']:
        elif request.form['password'] != 'bruno':
            error = 'Invalid password'
        else:
            session['logged_in'] = True #seems important, that's how the page knows you are logged in.
            flash('You were logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('home'))

def _parse_check_box(input_list):
    results = []
    for item in input_list:
        if request.form.get(item):
            results.append(item)
    return results

if __name__ == '__main__':
    app.debug = True
    app.run()
