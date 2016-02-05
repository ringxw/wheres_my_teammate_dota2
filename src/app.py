# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, url_for, abort, redirect
from pymongo import MongoClient

app = Flask(__name__)
#This connects to the client that runs on localhost port 27017, which is the default
client = MongoClient()

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
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    #should return results html here
    positions = ', '.join(_parse_check_box(POSITIONS))
    regions = ', '.join(_parse_check_box(REGIONS))
    languages = ', '.join(_parse_check_box(LANGUAGES))
    my_results = 'Player {0}, mmr {1}, plays positions {2}, plays on regions {3}, speaks {4}, looking for a teammate!!'.format(request.form['username'], request.form['mmr'], positions, regions, languages)

    return _get_player_name()

def _get_player_name():
    #try talk to the sample database, and return the player name
    conn = connect_db()
    players = conn.players.find()
    for player in players:
        print player
        ret = player['name']
    return ret

def _parse_check_box(input_list):
    results = []
    for item in input_list:
        if request.form.get(item):
            results.append(item)
    return results

if __name__ == '__main__':
    app.run(debug=True)
