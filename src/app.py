# -*- coding: utf-8 -*-

import os
import urllib2
import urllib
import re
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, json
from pymongo import MongoClient
from player import Player
from flask.ext.openid import OpenID


app = Flask(__name__)
#This connects to the client that runs on localhost port 27017, which is the default
client = MongoClient()

app.config.update(dict(
    DEBUG=True,
    SECRET_KEY="development key",
    USERNAME='admin',
    PASSWORD='default',
    STEAM_API_KEY = 'C960FA8C55EB2DBCE4B7B1EDA4637E42'
                  ))

oid = OpenID(app)

_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')
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
    my_results = '';
    count = 0
    for steam_id_loop in matching_player_list:
        if count > 0:
            my_results = my_results+', '
        count+=1
        my_results = my_results + get_steam_userinfo(steam_id_loop)
    #my_results = ', '.join(matching_player_list)

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
    count = 0
    for steam_id_loop in matching_player_list:
        if count > 0:
            my_results = my_results+', '
        count+=1
        my_results = my_results + get_steam_userinfo(steam_id_loop)
    #my_results = ', '.join(matching_player_list)
    session['redo_search'] = True
    #flash new player infos
    #concat player data into flash info
    flash(my_results)
    return render_template('index.html')

#OPENID LOGIN PART
#http://stackoverflow.com/questions/353880/how-does-openid-authentication-work
#http://tinisles.blogspot.ca/2008/02/how-does-openid-work.html
@app.route('/login')
@oid.loginhandler
def login():
    if g.player is not None:
        set_login_session_values(g.player)
        return render_template('index.html')
    return oid.try_login('http://steamcommunity.com/openid')

@oid.after_login
def create_or_login(resp):
    match = _steam_id_re.search(resp.identity_url)
    #g.player = Player.get_or_create(match.group(1))
    #steamdata = get_steam_userinfo(g.user.steam_id)
    #g.player.nickname = steamdata['personaname']
    #db.session.commit()

    set_login_session_values(match.group(1))
#return render_template(oid.get_next_url)
    return render_template('index.html')

def set_login_session_values(steam_id):
    session['logged_name'] = steam_id
    session['steam_name'] = get_steam_userinfo(session['logged_name'])
    session['logged_in'] = True
    session['redo_search'] = False
    g.player = session['logged_name']
    flash('You are logged in as %s' % session['steam_name'])
    return 1

@app.before_request
def before_request():
    g.player = None
    if 'logged_name' in session:
        g.player = session['logged_name']

@app.route('/logout')
def logout():

    flash('You were logged out')
    init_session()
    return render_template('index.html')

def init_session():
    session['logged_in'] = False
    session.pop('logged_name', None)
    session.pop('redo_search', None)
    session.pop('steam_name', None)

    return 1

def _parse_check_box(input_list):
    results = []
    for item in input_list:
        if request.form.get(item):
            results.append(item)
    return results

def get_steam_userinfo(steam_id):
    options = {
        'key': app.config['STEAM_API_KEY'],
        'steamids': steam_id
    }
    url = 'http://api.steampowered.com/ISteamUser/' \
        'GetPlayerSummaries/v0001/?%s' % urllib.urlencode(options)
    rv = json.load(urllib2.urlopen(url))
    print rv['response']['players']['player'][0]
    return rv['response']['players']['player'][0]['personaname'] or {}
#return rv or {}
if __name__ == '__main__':
    app.debug = True
    app.run()
