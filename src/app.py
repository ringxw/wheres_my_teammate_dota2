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

@app.route('/login')
@oid.loginhandler
def login():
    if g.player is not None:
        return redirect(oid.get_next_url())
    return oid.try_login('http://steamcommunity.com/openid')

@oid.after_login
def create_or_login(resp):
    match = _steam_id_re.search(resp.identity_url)
    #g.player = Player.get_or_create(match.group(1))
    #steamdata = get_steam_userinfo(g.user.steam_id)
    #g.player.nickname = steamdata['personaname']
    #db.session.commit()
    session['logged_name'] = match.group(1)
    session['steam_name'] = get_steam_userinfo(session['logged_name'])
    session['logged_in'] = True
    session['redo_search'] = False
    flash('You are logged in as %s' % session['steam_name'])
    return redirect(oid.get_next_url())

@app.before_request
def before_request():
    g.player = None
        #if 'user_id' in session:
#g.player = Player.query.get(session['username'])

@app.route('/logout')
def logout():
    init_session()
    flash('You were logged out')
    session.pop('logged_name', None)
    session.pop('steam_name', None)
    return redirect(oid.get_next_url())

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

def get_steam_userinfo(steam_id):
    options = {
        'key': app.config['STEAM_API_KEY'],
        'steamids': steam_id
    }
    url = 'http://api.steampowered.com/ISteamUser/' \
        'GetPlayerSummaries/v0001/?%s' % urllib.urlencode(options)
    rv = json.load(urllib2.urlopen(url))
    return rv['response']['players']['player'][0]['personaname'] or {}
#return rv or {}
if __name__ == '__main__':
    app.debug = True
    app.run()
