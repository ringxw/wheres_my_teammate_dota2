# -*- coding: utf-8 -*-

import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from pymongo import MongoClient
from player import Player


app = Flask(__name__)
#This connects to the client that runs on localhost port 27017, which is the default
client = MongoClient()

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

#This will connect to the local mongodby
#This connects to the client that runs on localhost port 27017, which is the default
def connect_db():
    client = MongoClient()
    db = client.appdb
    return db

@app.route('/')
def home():
    init_session()
    flash('new session')
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    #should return results html here
    positions = ', '.join(_parse_check_box(POSITIONS))
    regions = ', '.join(_parse_check_box(REGIONS))
    languages = ', '.join(_parse_check_box(LANGUAGES))

    player_info = Player.build_player_info(request.form['username'], request.form['mmr'], positions, regions, languages)

    current_player = Player(player_info)
    
    db = connect_db()
    current_player._update_user_to_db(db)
    # We are providing an mmr range of 200 as a search criteria
    matching_player_list = current_player.get_matching_players(200, db)
    my_results = ', '.join(matching_player_list)

    if session['logged_in']:
        session['redo_search'] = True
    #flash new player infos
    #concat player data into flash info
    flash(my_results)
    return render_template('index.html')

#TODO: Remove? I dont think we need this,  one /search should be enough to handle redo if we want different results for users
@app.route('/redo_search', methods=['POST'])
def redo_search():
    #should return results html here
    positions = ', '.join(_parse_check_box(POSITIONS))
    regions = ', '.join(_parse_check_box(REGIONS))
    languages = ', '.join(_parse_check_box(LANGUAGES))

    player_info = Player.build_player_info(request.form['username'], request.form['mmr'], positions, regions, languages)
    current_player = Player(player_info)
    
    db = connect_db()
    current_player._update_user_to_db(db)
    # We are providing an mmr range of 200 as a search criteria
    matching_player_list = current_player.get_matching_players(200, db)

    session['redo_search'] = True
    #flash new player infos
    #concat player data into flash info
    flash(my_results)
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #if request.form['username'] != 'OSfrog':
        #    error = 'Invalid username'
        #elif request.form['password'] != 'bruno':
        #    error = 'Invalid password'
        #else:
            session['logged_in'] = True #seems important, that's how the page knows you are logged in.
            session['logged_name'] = request.form['username']
            session['redo_search'] = False
            flash('You were logged in')
            return render_template('index.html')
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    init_session()
    flash('You were logged out')
    return render_template('index.html')

def init_session():
    session['logged_in'] = False
    session['logged_name'] = '_no_user'
    session['redo_search'] = False

    return 1

def _parse_check_box(input_list):
    results = []
    for item in input_list:
        if request.form.get(item):
            results.append(item)
    return results

if __name__ == '__main__':
    app.debug = True
    app.run()
