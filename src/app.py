# -*- coding: utf-8 -*-

import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from pymongo import MongoClient


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
    player = _build_player_info(request.form['username'], request.form['mmr'], positions, regions, languages)
    db = connect_db()
    _insert_user_to_db(player, db)
    user_list = _search_players(player, 200, db)
    my_results = ', '.join(user_list)
    #my_results = 'Player {0}, mmr {1}, plays positions {2}, plays on regions {3}, speaks {4}, looking for a teammate!!'.format(request.form['username'], request.form['mmr'], positions, regions, languages)
    if session['logged_in']:
        session['redo_search'] = True
    #flash new player infos
    #concat player data into flash info
    flash(my_results)
    return render_template('index.html')

@app.route('/redo_search', methods=['POST'])
def redo_search():
    #should return results html here
    positions = ', '.join(_parse_check_box(POSITIONS))
    regions = ', '.join(_parse_check_box(REGIONS))
    languages = ', '.join(_parse_check_box(LANGUAGES))
	
    player = _build_player_info(request.form['username'], request.form['mmr'], positions, regions, languages)
    db = connect_db()
    _insert_user_to_db(player, db)
    user_list = _search_players(player, 200, db)
    my_results = ', '.join(user_list)
    #my_results = 'REDO_SEARCH Player {0}, mmr {1}, plays positions {2}, plays on regions {3}, speaks {4}, looking for a teammate!!'.format(request.form['username'], request.form['mmr'], positions, regions, languages)
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

def _insert_user_to_db(player, db):
    result = db.players.insert_one(player)
 
# searches the db for user within mmr range, return list of players, if empty, return msg string
def _search_players(current_player, mmr_range, db):
    mmr_value = int(current_player['mmr'])
    upper_range = mmr_value+mmr_range
    lower_range = mmr_value-mmr_range
    ret = []
    for player in search_users_mmr(db, upper_range, lower_range):
        if player['username'] != current_player['username'] and _has_matching_region_and_language(player,current_player):
            ret.append(player['username'])
    if not ret:
        ret = ['No Matching MMR for you']
    return ret

def search_users_mmr(db, upper_range, lower_range):
    return db.players.find( { "$and" : [ { "mmr": { "$lt": upper_range } }, { "mmr": { "$gt": lower_range } } ] } )
def _parse_check_box(input_list):
    results = []
    for item in input_list:
        if request.form.get(item):
            results.append(item)
    return results

#returns true if player1 and player2 have matching region AND matching language
def _has_matching_region_and_language(player1, player2):
    '''
    we call isdisjoint to find if common element exists, example:
    {0, 1, 2}.isdisjoint([1])
    False
    '''
    region_mismatch = set(player1['regions']).isdisjoint(player2['regions'])
    language_mismatch = set(player1['languages']).isdisjoint(player2['languages'])
    print (region_mismatch)
    print (language_mismatch)
    if region_mismatch is True or language_mismatch is True:
        return False
    return True

def _build_player_info(username, mmr, positions, regions, languages):
    player_info = {}
    player_info['username'] = username
    player_info['mmr'] = int(mmr)
    player_info['positions'] = positions
    player_info['regions'] = regions
    player_info['languages'] = languages
    #player_info['build_date'] = 
    return player_info

if __name__ == '__main__':
    app.debug = True
    app.run()
