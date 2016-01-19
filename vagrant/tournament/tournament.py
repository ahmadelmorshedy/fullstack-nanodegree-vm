#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import psycopg2.extras


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM match_results")
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT count(*) FROM players")
    results = cursor.fetchone()[0]
    conn.close()
    return results


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO players (name) VALUES (%s)", (name,))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    # player standings are implemented as a View in the sql file
    conn = connect()
    cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM player_standings")
    results = cursor.fetchall()
    conn.close()
    return results


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO match_results (winner, loser) VALUES (%s, %s)", (winner, loser,))
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    # initialize Variables
    paired_players = [] #used to save the ids for the players that are already registered to a pair
    players_matrix = {} #each row contains player id and a list of previous opponents

    # connect to the Database
    conn = connect()
    cursor = conn.cursor(cursor_factory = psycopg2.extras.DictCursor)

    '''
    since players are paired based on number of matches they won, we need to
    select players ordered by their wins, that's why we select player_standings
    view, but w need only the id and name
    '''
    cursor.execute("SELECT id, name from player_standings")
    player_standings = cursor.fetchall()

    ''' players played width view gets a couples of player, opponent, we use it
    to build players matrix '''
    cursor.execute("SELECT * from players_played_with")
    players_played_with = cursor.fetchall()

    # No further need for the connection. close it
    conn.close()

    # Build the matrix
    ''' loop on plyers in player_standings so that we guarantee that they are
    sorted per wins in player matrix '''
    for player in player_standings:
        if not player['id'] in players_matrix:
            players_matrix[player['id']] = [] #create entry for this player
            players_matrix[player['id']].append(player['name'])
        #get player's opponent
        for opponent in players_played_with:
            if opponent['player_id'] == player['id']:
                players_matrix[player['id']].append(opponent['opponent'])

    ''' Pairing the corresponding players together:
    each player has its nearest player(s) after him in players matrix since
    it is ordered based on wins
    only required to check that
        1. the candidate player is not already paired
        2. the canidate player and the current player did not meet before'''
    players_ids = players_matrix.keys()
    for i in range(0,len(players_ids)-1):
        if not players_ids[i] in paired_players:
            for j in range (i+1, len(players_ids)):
                if not players_ids[j] in paired_players:
                    if not players_ids[j] in players_matrix[players_ids[i]]:
                        paired_players.append(players_ids[i])
                        paired_players.append(players_ids[j])
                        break
    #build pairings
    ''' Now we have the players in paired_players ordered consecutively, all we
    need is reforrmatting them in the form (id1, name1, id2, name2)'''
    i = 0
    pairings = []
    while i < len(paired_players):
        pairing_row = []
        pairing_row.append(paired_players[i])
        pairing_row.append(players_matrix[paired_players[i]][0])
        pairing_row.append(paired_players[i+1])
        pairing_row.append(players_matrix[paired_players[i+1]][0])
        pairings.append(pairing_row)
        i = i + 2
    return pairings
