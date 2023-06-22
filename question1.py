try:
    from contextlib import nullcontext
    import requests
    import zipfile
    import io
    import json
    import sqlite3
except:
    print('library not found')

# connection to the database
conn = sqlite3.connect('ODI.db')

cursor = conn.cursor()



#create the tables:

try:
    cursor.execute('''CREATE TABLE IF NOT EXISTS MATCH_DETAILS_ODI (
                        id INTEGER PRIMARY KEY ,
                        Venue TEXT,
                        city TEXT,
                        date DATE,
                        event_name TEXT,
                        match_type_number INTEGER,
                        team1 TEXT,
                        team2 TEXT,
                        result TEXT,
                        by_wickets INTEGER,
                        by_runs INTEGER,
                        t_win TEXT,
                        t_decision TEXT,
                        player_of_match TEXT,
                        season TEXT,
                        target INTEGER,
                        overs INTEGER,
                        gender TEXT
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS META_ODI (
                        data_version TEXT,
                        created TEXT,
                        revision INTEGER,
                        id INTEGER,
                        FOREIGN KEY (id) REFERENCES MATCH_DETAILS_ODI(id)
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS PLAYER_ODI (
                        player_name TEXT,
                        id INTEGER,
                        team TEXT,
                        register_id INTEGER,
                        FOREIGN KEY (id) REFERENCES MATCH_DETAILS_ODI(id)
                    )''')
    

    cursor.execute('''CREATE TABLE IF NOT EXISTS INNINGS_ODI (
                        batting_team TEXT,
                        bowling_team TEXT,
                        over INTEGER,
                        delievery INTEGER,
                        batter_name TEXT,
                        bowler_name TEXT,
                        non_striker_name TEXT,
                        batter_runs INTEGER,
                        extras INTEGER,
                        total INTEGERS,
                        id INTEGER,
                        FOREIGN KEY (id) REFERENCES MATCH_DETAILS_ODI(id)
                    )''')
    
    
except sqlite3.Error as e:
    print("Error:", e)



id=0
# URL of the zipped file
zip_file_url = "https://cricsheet.org/downloads/odis_json.zip"

# Send a GET request to the URL to retrieve the zipped file
response = requests.get(zip_file_url)

if response.status_code == 200:
    # Read the zipped content into memory
    zip_content = io.BytesIO(response.content)

    # Open the zip file
    with zipfile.ZipFile(zip_content, "r") as zip_file:
        # Iterate over the files in the zip archive
        for file_name in zip_file.namelist():
            # Check if the file is of interest
            if file_name.endswith(".json"):
                # Extract the file from the zip archive
                extracted_data = zip_file.read(file_name)
                
                json_data = json.loads(extracted_data)
                # Process the extracted data as per your requirement
                #print(json_data['meta']['created'],json_data['info']['season'],json_data['info']['bowl_out'], i)
                #print(json_data['info']['gender'])
                #print(json_data['info']['outcome'])
                
                id = cursor.lastrowid  # Get the auto-incremented id
                venue = json_data['info']['venue']
                city = None
                pom = 'not mentioned'
                eventname = 'not mentioned'

                for info,n in json_data['info'].items():
                    if info == 'city':
                        city = n 
                    if info == 'player_of_match':
                        pom = n[0]
                    if info == 'event':
                        eventname =  n['name']
                date = json_data['info']['dates'][0]

                match_type_number = json_data['info']['match_type_number']
                team1 = json_data['info']['teams'][0]
                team2 = json_data['info']['teams'][1]

                result = None # solved in if loop below
                by_wickets = None # assinged values below
                by_runs = None # assigned values below

                t_win = json_data['info']['toss']['winner']
                t_decision = json_data['info']['toss']['decision']

                

                
                season = json_data['info']['season']
                target = None # assigned below
                overs = None # assigned below
                gender = json_data['info']['gender']

                data_version = json_data['meta']['data_version']
                created =  json_data['meta']['created']
                revision =  json_data['meta']['revision']

                player_name = None

                register_id = None

                people_name = None

                

                

                if 'winner' in json_data['info']['outcome']:
                    result = json_data['info']['outcome']['winner']
                    if 'by' in json_data['info']['outcome']:
                        if 'runs' in json_data['info']['outcome']['by']:
                            by_runs = json_data['info']['outcome']['by']['runs']
                        elif 'wickets' in json_data['info']['outcome']['by']:
                            by_wickets = json_data['info']['outcome']['by']['wickets']
                else:
                    result = 'no result'
                    by_runs = 0
                    by_wickets = 0

                
                for over in json_data['innings']:
                        for w,q in over.items():
                            if w == 'target':
                               target = q['overs']
                               overs = q['runs']

                #inserting into Match details odi table
                
                try:
                    cursor.execute('''INSERT INTO MATCH_DETAILS_ODI (
                            id, Venue, city, date, event_name, match_type_number, team1, team2, result,
                            by_wickets, by_runs, t_win, t_decision, player_of_match, season, target, overs, gender
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (id, venue, city, date, eventname, match_type_number, team1, team2, result,
                        by_wickets, by_runs, t_win, t_decision, pom, season, overs, target, gender))
                    
                except sqlite3.Error as e:
                    print("Error in detailsodi:", e)
                


                #inserting into meta odi table
                
                try:

                    cursor.execute('''INSERT INTO META_ODI (
                        data_version, created, revision, id
                        ) VALUES (?, ?, ?, ?)''',
                        (data_version, created, revision, id))
                except sqlite3.Error as e:
                    print(" error in Meta_odi", e)


                for info in json_data['info']['players'][team1]:
                    player_name = info
                    rid = json_data['info']['registry']['people'].get(info)

                    #inserting into Player odi table
                    
                    try:
                        cursor.execute('''INSERT INTO PLAYER_ODI (
                            player_name, id, team, register_id
                        ) VALUES (?, ?, ?, ?)''',
                        (player_name, id, team1, rid))
                    except sqlite3.Error as e:
                        print("error in team1 palyer_odi ", e)


                for info in json_data['info']['players'][team2]:
                    player_name = info
                    rid = json_data['info']['registry']['people'].get(info)

                    #inserting into Player odi table

                    try:
                        cursor.execute('''INSERT INTO PLAYER_ODI (
                            player_name, id, team, register_id
                        ) VALUES (?, ?, ?, ?)''',
                        (player_name, id, team2, rid))
                    except sqlite3.Error as e:
                        print("error in team2 palyer_odi ", e)

                
                
                    
                for over in json_data['innings']:
                    batting_team = over['team']
                    if batting_team == team1:
                        bowling_team = team2
                    else:
                        bowling_team = team1
                    ov = over['overs']
                    for o in ov:
                            deliveries = o['deliveries']
                            om = o['over']
                            d = 0
                            for delivery in deliveries:
                                d = d+1
                                batter_name = delivery['batter']
                                bowler_name = delivery['bowler']
                                non_striker_name = delivery['non_striker']
                                runs = delivery['runs']
                                batter_runs = runs['batter']
                                extras = runs['extras']
                                total = runs['total']


                                # inserting into innings_odi table
                                try:
                                    cursor.execute('''INSERT INTO INNINGS_ODI (
                                        batting_team, bowling_team, over, delievery, batter_name, bowler_name,
                                        non_striker_name, batter_runs, extras, total, id
                                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                        (batting_team, bowling_team, om, d,batter_name,bowler_name,non_striker_name,batter_runs,extras,total,id))
                                except sqlite3.Error as e:
                                    print("error in innings_odi ",e)

                                #print(batting_team, bowling_team, om, d,batter_name,bowler_name,non_striker_name,batter_runs,extras,total,id)


    # Close the response to free up resources
    response.close()
conn.commit()
print("Data ingested successfully")

conn.close()


