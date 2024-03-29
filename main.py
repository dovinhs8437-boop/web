from flask import Flask, render_template, request
import sqlite3
from datetime import datetime, timedelta
import csv
import requests
import random

season_id = '2024'
teams  = {1:"Nick",2:"Phillip",3:"Andrew",4:"Josh",5:"Wesley",6:"Becky",8:"Nate",10:"Paul",7:"Lonnie",9:"Caleb"}
app = Flask(__name__,template_folder='templates')

def yesterday(frmt='%Y-%m-%d', string=True):
    yesterday = datetime.now() - timedelta(1)
    if string:
        return yesterday.strftime(frmt)
    return yesterday
date = yesterday()

def get_highlight_url(game_id, event_id):
    headers = {
        'Host': 'stats.nba.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'x-nba-stats-origin': 'stats',
        'x-nba-stats-token': 'true',
        'Connection': 'keep-alive',
        'Referer': 'https://stats.nba.com/',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

    url = 'https://stats.nba.com/stats/videoeventsasset?GameEventID={}&GameID={}'.format(
                event_id, game_id)
    r = requests.get(url, headers=headers)
    json = r.json()
    video_urls = json['resultSets']['Meta']['videoUrls']
    playlist = json['resultSets']['playlist']
    video_event = {'video': video_urls[0]['lurl'], 'desc': playlist[0]['dsc']}
    return (video_event['video'],video_event['desc'])

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

@app.route('/players/')
def return_players():
    players= request.args.get('players','')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')    

    if not start_date:
        start_date = yesterday()
    if not end_date:
        end_date = yesterday()

    print("start date:", type(start_date))
    print("end date:", type(end_date))
    print(yesterday())
    highlights= []
    players_list = players.split(',')
    # Connect to the SQLite database
    conn = sqlite3.connect('MLB_Highlights.db')
    cursor = conn.cursor()
    # Execute SQL query
    for p in players_list:
        p = p.strip()
        cursor.execute(f"""
                        SELECT player_name,date,headline,description,mp4_url,yahoo_team_name,mlb_team_name
                        FROM yahoo_highlights_{season_id}
                        Where player_name LIKE '%{p}%' and date >= '{start_date}' and date <='{end_date}'
                        ORDER BY player_name, date
                        """
                        )
        
        player = cursor.fetchall()
        for i in player:
            highlights.append(i)
    # Close the database connection
    conn.close()

    # Render the template with the query results
    return render_template('return_players.html', highlights=highlights, start_date=start_date,end_date=end_date,players=players)

@app.route('/search_players/')
def search_players():
    players = request.args.get('players', '')  # If 'players' parameter is not provided, default to an empty string
    end_date = request.args.get('end_date', yesterday())
    start_date = request.args.get('start_date', yesterday())
    return render_template('search_players.html', players=players, end_date=end_date, start_date=start_date)

@app.route('/keyword/')
def return_keyword():
    keywords= request.args.get('keywords','')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')    

    if not start_date:
        start_date = yesterday()
    if not end_date:
        end_date = yesterday()

    print("start date:", type(start_date))
    print("end date:", type(end_date))
    print(yesterday())
    highlights= []
    keywords_list = keywords.split(',')
    # Connect to the SQLite database
    conn = sqlite3.connect('MLB_Highlights.db')
    cursor = conn.cursor()
    # Execute SQL query
    for k in keywords_list:
        k = k.strip()
        cursor.execute(f"""
                        SELECT player_name,date,headline,description,mp4_url,yahoo_team_name,mlb_team_name
                        FROM yahoo_highlights_{season_id}
                        Where description LIKE '%{k}%' and date >= '{start_date}' and date <='{end_date}'
                        ORDER BY player_name, date
                        """
                        )
        
        keyword = cursor.fetchall()
        for i in keyword:
            highlights.append(i)
    # Close the database connection
    conn.close()

    # Render the template with the query results
    return render_template('return_keyword.html', highlights=highlights, start_date=start_date,end_date=end_date,keywords=keywords)

@app.route('/search_keyword/')
def search_keyword():
    keywords = request.args.get('keywords', '')  # If 'players' parameter is not provided, default to an empty string
    end_date = request.args.get('end_date', yesterday())
    start_date = request.args.get('start_date', yesterday())
    return render_template('search_keyword.html', keywords=keywords, end_date=end_date, start_date=start_date)

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
