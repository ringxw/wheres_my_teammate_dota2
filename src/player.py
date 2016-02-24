#!/usr/bin/env python

import os

#player object will have players basic info
class Player:
    #construct the player object
    def __init__(self, info):
        self.info = info
        #self.info['username'] = name
        #self.info['mmr'] = mmr
        #self.info['positions'] = positions
        #self.info['regions'] = regions
        #self.info['languages'] = languages

    def search_users_name(self, db):
        return db.players.find({"username": player.info['username']})

    # Find all players from the player collection that's has lower_range<mmr<upper_range
    @staticmethod
    def find_matching_mmr_users(db, upper_range, lower_range):
        return db.players.find( { "$and" : [ { "mmr": { "$lt": upper_range } }, { "mmr": { "$gt": lower_range } } ] } )

    def _insert_user_to_db(self, db):
        result = db.players.insert_one(self.info)

    def _update_user_to_db(self, db):
        result = db.players.update( {"username": self.info['username']}, \
                                   self.info, \
                                   upsert=True)
        return result

    # searches the db for user within mmr range, regions and language; return list of players, if empty, return msg string
    def get_matching_players(self, mmr_range, db):
        player_mmr = int(self.info['mmr'])
        upper_range = player_mmr+mmr_range
        lower_range = player_mmr-mmr_range
        ret = []
        for player in self.find_matching_mmr_users(db, upper_range, lower_range):
            # We have to make sure the search result doesn't have the current player him/herself
            if player['username'] != self.info['username'] and self.has_matching_region_and_language(player):
                ret.append(player['username'])
        if not ret:
            ret = ['No Matching MMR for you']
        return ret
  
    #searches the player collection and returns all the player info that has matching mmr
    @staticmethod
    def search_players_mmr(db, upper_range, lower_range):
        return db.players.find( { "$and" : [ { "mmr": { "$lt": upper_range } }, { "mmr": { "$gt": lower_range } } ] } )

    #returns true if current player and player2 have matching region AND matching language
    def has_matching_region_and_language(self, player2_info):
        '''
        we call isdisjoint to find if common element exists, example:
        {0, 1, 2}.isdisjoint([1])
        False
        '''
        region_mismatch = set(self.info['regions']).isdisjoint(player2_info['regions'])
        language_mismatch = set(self.info['languages']).isdisjoint(player2_info['languages'])
        print (region_mismatch)
        print (language_mismatch)
        if region_mismatch is True or language_mismatch is True:
            return False
        return True

    #Builds player information, returns a dictionary 
    @staticmethod
    def build_player_info(username, mmr, positions, regions, languages):
        player_info = {}
        player_info['username'] = username
        player_info['mmr'] = int(mmr)
        player_info['positions'] = positions
        player_info['regions'] = regions
        player_info['languages'] = languages
        #player_info['build_date'] =
        return player_info
