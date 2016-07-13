# -*- coding: utf-8 -*-

import os
import urllib2
import urllib
import re
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, json
from pymongo import MongoClient
import player
from player import Player
from flask.ext.openid import OpenID
import logging
from logging import Formatter
from logging.handlers import TimedRotatingFileHandler
import requests

app = Flask(__name__)
FORMATTER = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")

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
    app.logger.info('Initialize connection to DB')
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
    if not _parse_check_box(POSITIONS):
        flash('Please make sure to select positions')
        return render_template('index.html')
    else:
        positions = ', '.join(_parse_check_box(POSITIONS))
    if not _parse_check_box(REGIONS):
        flash('Please make sure to select regions')
        return render_template('index.html')
    else:
        regions = ', '.join(_parse_check_box(REGIONS))
    if not _parse_check_box(LANGUAGES):
        flash('Please make sure to select Languages')
        return render_template('index.html')
    else:
        languages = ', '.join(_parse_check_box(LANGUAGES))
    app.logger.info('Player input positions: {0}, regions: {1}, languages: {2} mmr: {3}'.format(positions, regions, languages, request.form['amount']))

    player_info = Player.build_player_info(request.form['username'], request.form['amount'], positions, regions, languages)

    app.logger.info('User with playername {0} requests to search'.format(player_info['username']))
    current_player = Player(player_info)
    
    db = connect_db()
    current_player._update_user_to_db(db)
    # We are providing an mmr range of 200 as a search criteria
    matching_player_list = current_player.get_matching_players(200, db)
    my_results = []
    for matching_player_id in matching_player_list:
        my_results.append(get_steam_userinfo(matching_player_id))
    if my_results:
        results = ', '.join(my_results)
    else:
        results = 'Could not match MMR for your profile'

    if session['logged_in']:
        session['redo_search'] = True

    #flash new player infos
    #concat player data into flash info
    flash(results)
    return render_template('index.html')

#TODO: Remove? I dont think we need this,  one /search should be enough to handle redo if we want different results for users
@app.route('/redo_search', methods=['POST'])
def redo_search():
    #should return results html here
    positions = ', '.join(_parse_check_box(POSITIONS))
    regions = ', '.join(_parse_check_box(REGIONS))
    languages = ', '.join(_parse_check_box(LANGUAGES))

    player_info = Player.build_player_info(request.form['username'], request.form['amount'], positions, regions, languages)
    current_player = Player(player_info)
    
    db = connect_db()
    current_player._update_user_to_db(db)
    # We are providing an mmr range of 200 as a search criteria
    matching_player_list = current_player.get_matching_players(200, db)
    my_results = []
    for matching_player_id in matching_player_list:
        my_results.append(get_steam_userinfo(matching_player_id))
    if my_results:
        results = ', '.join(my_results)
    else:
        results = 'Could not match MMR for your profile'

    session['redo_search'] = True
    #flash new player infos
    #concat player data into flash info
    flash(results)
    return render_template('index.html')

'''OPENID LOGIN PART
http://stackoverflow.com/questions/353880/how-does-openid-authentication-work
http://tinisles.blogspot.ca/2008/02/how-does-openid-work.html'''
@app.route('/login')
@oid.loginhandler
def login():
    app.logger.info('Login request')
    if g.player is not None:
        set_login_session_values(g.player)
        return render_template('index.html')
    return oid.try_login('http://steamcommunity.com/openid')

@oid.after_login
def create_or_login(resp):
    app.logger.info('Login successful')
    match = _steam_id_re.search(resp.identity_url)
    set_login_session_values(match.group(1))

#return render_template(oid.get_next_url)
    return render_template('index.html')

def set_login_session_values(steam_id):
    session['logged_name'] = steam_id
    session['steam_name'] = get_steam_userinfo(session['logged_name'])
    session['logged_in'] = True
    session['redo_search'] = False
    g.player = session['logged_name']
    flash(u'You are logged in as {0}'.format(session['steam_name']))
    return 1

@app.before_request
def before_request():
    g.player = None
    if 'logged_name' in session:
        g.player = session['logged_name']

@app.route('/logout')
def logout():
    app.logger.info('Logging out')
    flash('You were logged out')
    init_session()
    return render_template('index.html')

def init_session():
    app.logger.info('Initialize session')
    session['logged_in'] = False
    session.pop('logged_name', None)
    session.pop('redo_search', None)
    session.pop('steam_name', None)

def _parse_check_box(input_list):
    results = []
    for item in input_list:
        if request.form.get(item):
            results.append(item)
    return results

def get_steam_userinfo(steam_id):
    app.logger.info('API Request GetPlayerSummaries for {0}'.format(steam_id))
    options = {
        'key': app.config['STEAM_API_KEY'],
        'steamids': steam_id
    }
    url = 'http://api.steampowered.com/ISteamUser/' \
        'GetPlayerSummaries/v0001/?%s' % urllib.urlencode(options)
    r = requests.get(url)
    #app.logger.info(u'Steam Requests Status Code {0}'.format(r.status_code))
    response_dict = json.loads(r.text)
    app.logger.info(u'Steam Requests GetPlayerSummaries {0}'.format(r.text))
    if response_dict['response']['players']['player'][0]:
        return response_dict['response']['players']['player'][0]['personaname']
    else:
        #Throw error instead of return empty
        return ''


if __name__ == '__main__':
    handler = TimedRotatingFileHandler('/var/dota2teamfinder/app.log', when='H', interval=1)
    handler.suffix = "%Y.%m.%d.%H"
    handler.setLevel(logging.INFO)
    handler.setFormatter(FORMATTER)
    #Add your file loggers here
    loggers = [app.logger, player._LOG]
    for logger in loggers:
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    app.debug = True
    app.run()
