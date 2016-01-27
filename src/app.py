# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, url_for, abort, redirect

app = Flask(__name__)

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

def _parse_check_box(input_list):
    results = []
    for item in input_list:
        if request.form.getlist(item):
            results.append(item)
    return results

if __name__ == '__main__':
    app.run(debug=True)
