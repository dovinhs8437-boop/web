from flask import Flask, render_template, request
import sqlite3
from datetime import datetime, timedelta

season_id = '2024'
teams  = {1:"Nick",2:"Phillip",3:"Andrew",4:"Josh",5:"Wesley",6:"Becky",8:"Nate",10:"Paul",7:"Lonnie",9:"Caleb"}
app = Flask(__name__,template_folder='templates')

def yesterday(frmt='%Y-%m-%d', string=True):
    yesterday = datetime.now() - timedelta(1)
    if string:
        return yesterday.strftime(frmt)
    return yesterday
date = yesterday()
@app.route('/')
def index():

    return render_template('index.html',date=date,yesterday=yesterday)

@app.route('/yahoo/')
def yahoo_list():
    return render_template('yahoo_list.html',date=date,yesterday=yesterday)

@app.route('/mlb_teams/')
def mlb_list():
    return render_template('mlb_list.html',date=date,yesterday=yesterday)


@app.route('/team/<team_id>/<date>')
def yahoo_team_page(team_id,date=None):
    if date is None:
        date = yesterday()

    # Connect to the SQLite database
    conn = sqlite3.connect('MLB_Highlights.db')
    cursor = conn.cursor()
    team_owner = teams[int(team_id)]
    # Execute SQL query
    cursor.execute(f"""
                    SELECT player_name,date,headline,description,mp4_url,yahoo_team_name,mlb_team_name
                    FROM yahoo_highlights_{season_id}
                    Where team_id = {team_id} and date = '{date}'
                    ORDER BY player_name, date
                    """
                    )
    highlights = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Render the template with the query results
    return render_template('yahoo_teams.html', highlights=highlights, date=date,team_owner=team_owner)

@app.route('/all/<date>')
def all_players_page(date=None):
    if date is None:
        date = yesterday()

    # Connect to the SQLite database
    conn = sqlite3.connect('MLB_Highlights.db')
    cursor = conn.cursor()
    # Execute SQL query
    cursor.execute(f"""
                    SELECT player_name,date,headline,description,mp4_url,yahoo_team_name,mlb_team_name
                    FROM yahoo_highlights_{season_id}
                    Where date = '{date}'
                    ORDER BY player_name, date
                    """
                    )
    highlights = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Render the template with the query results
    return render_template('all_players.html', highlights=highlights, date=date)

@app.route('/players/<date>')
def return_players(date=None):
    players= request.args.get('players','')
    if date is None:
        date = yesterday()

    highlights= []
    players_list = players.split(',')
    print(players)
    # Connect to the SQLite database
    conn = sqlite3.connect('MLB_Highlights.db')
    cursor = conn.cursor()
    # Execute SQL query
    for p in players_list:
        p = p.strip()
        cursor.execute(f"""
                        SELECT player_name,date,headline,description,mp4_url,yahoo_team_name,mlb_team_name
                        FROM yahoo_highlights_{season_id}
                        Where player_name LIKE '%{p}%' and date = '{date}'
                        ORDER BY player_name, date
                        """
                        )
        print(p)
        player = cursor.fetchall()
        for i in player:
            highlights.append(i)
    # Close the database connection
    conn.close()

    # Render the template with the query results
    return render_template('return_players.html', highlights=highlights, date=date)

@app.route('/search_players/')
def search_players():
    players = request.args.get('players', '')  # If 'players' parameter is not provided, default to an empty string
    return render_template('search_players.html', players=players, date=yesterday())


@app.route('/mlb/<mlb_id>/<date>')
def mlb_team_page(mlb_id,date=None):
    if date is None:
        date = yesterday()

    # Connect to the SQLite database
    conn = sqlite3.connect('MLB_Highlights.db')
    cursor = conn.cursor()
    
    # Execute SQL query
    cursor.execute(f"""
                    SELECT player_name,date,headline,description,mp4_url,yahoo_team_name,mlb_team_name
                    FROM yahoo_highlights_{season_id}
                    Where (away_name = '{mlb_id}' or home_name = '{mlb_id}') and date = '{date}'
                    ORDER BY player_name, date
                    """
                    )
    highlights = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Render the template with the query results
    return render_template('mlb_teams.html', highlights=highlights, date=date,mlb_id=mlb_id)

if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0')
