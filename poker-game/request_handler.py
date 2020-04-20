import sqlite3
import datetime
players_db = '__HOME__/team079/'

locations={
    "Student Center":[(-71.095863,42.357307),(-71.097730,42.359075),(-71.095102,42.360295),(-71.093900,42.359340),(-71.093289,42.358306)],
    "Dorm Row":[(-71.093117,42.358147),(-71.092559,42.357069),(-71.102987,42.353866),(-71.106292,42.353517)],
    "Simmons/Briggs":[(-71.097859,42.359035),(-71.095928,42.357243),(-71.106356,42.353580),(-71.108159,42.354468)],
    "Boston FSILG (West)":[(-71.124664,42.353342),(-71.125737,42.344906),(-71.092478,42.348014),(-71.092607,42.350266)],
    "Boston FSILG (East)":[(-71.092409,42.351392),(-71.090842,42.343589),(-71.080478,42.350900),(-71.081766,42.353771)],
    "Stata/North Court":[(-71.091636,42.361802),(-71.090950,42.360811),(-71.088353,42.361112),(-71.088267,42.362476),(-71.089769,42.362618)],
    "East Campus":[(-71.089426,42.358306),(-71.090885,42.360716),(-71.088310,42.361017),(-71.087130,42.359162)],
    "Vassar Academic Buildings":[(-71.094973,42.360359),(-71.091776,42.361770),(-71.090928,42.360636),(-71.094040,42.359574)],
    "Infinite Corridor/Killian":[(-71.093932,42.359542),(-71.092259,42.357180),(-71.089619,42.358274),(-71.090928,42.360541)],
    "Kendall Square":[(-71.088117,42.364188),(-71.088225,42.361112),(-71.082774,42.362032)],
    "Sloan/Media Lab":[(-71.088203,42.361017),(-71.087044,42.359178),(-71.080071,42.361619),(-71.082796,42.361905)],
    "North Campus":[(-71.11022,42.355325),(-71.101280,42.363934),(-71.089950,42.362666),(-71.108361,42.354484)],
    "Technology Square":[(-71.093610,42.363157),(-71.092130,42.365837),(-71.088182,42.364188),(-71.088267,42.362650)]
}

def request_handler(request):
    # Request Dictionary: {'method': 'GET', 'values': {}, 'args': []}
    lat = float(request['values']['lat'])
    lon = float(request['values']['lon'])
    mitArea = get_area([lat, lon], locations)

    if request['method'] == 'GET':
        return mitArea
    elif request['method'] == 'POST':
        conn = sqlite3.connect(visits_db)  # connect to that database (will create if it doesn't already exist)
        c = conn.cursor()  # move cursor into database (allows us to execute commands)
        outs = ""
        c.execute('''CREATE TABLE IF NOT EXISTS gps_table (user text, lat float, lon float, location text, timing timestamp);''') # run a CREATE TABLE command
        thirty_seconds_ago = datetime.datetime.now()- datetime.timedelta(seconds = 30) # create time for fifteen minutes ago!
        user = request['values']['user']
        c.execute('''INSERT into gps_table VALUES (?,?,?,?,?);''', (user, lat, lon, mitArea, datetime.datetime.now()))
        things = c.execute('''SELECT * FROM dated_table WHERE timing > ? AND location = ? ORDER BY timing ASC;''',(thirty_seconds_ago, mitArea)).fetchall()
        outs = "Users with same location in past 30 seconds:\n"
        for x in things:
            outs+=str(x)+"\n"
        conn.commit() # commit commands
        conn.close() # close connection to database
        return outs

def bounding_box(point_coord, box):
    minX = min([box[x][0] for x in range(len(box))])
    maxX = max([box[x][0] for x in range(len(box))])
    minY = min([box[y][1] for y in range(len(box))])
    maxY = max([box[y][1] for y in range(len(box))])
    return (minX <= point_coord[0] <= maxX) and (minY <= point_coord[1] <= maxY)

def within_area(point_coord, area):
    translatedArea = [(p[0]-point_coord[0], p[1]-point_coord[1]) for p in area]
    translatedArea.append((area[0][0]-point_coord[0], area[0][1]-point_coord[1]))
    crossingEdges = []
    numCrossed = 0
    for i in range(len(translatedArea)-1):
        if sign(translatedArea[i][1]) != sign(translatedArea[i+1][1]):
            crossingEdges.append((translatedArea[i], translatedArea[i+1]))
    for edge in crossingEdges:
        if sign(edge[0][0]) == 1 and sign(edge[1][0]) == 1:
            numCrossed += 1
        elif sign(edge[0][0]) == -1 and sign(edge[1][0]) == -1:
            continue
        else:
            intersection = (edge[0][0]*edge[1][1] - edge[0][1]*edge[1][0])/(edge[1][1] - edge[0][1])
            if intersection > 0:
                numCrossed += 1
    return numCrossed % 2 == 1

def get_area(point_coord,locations):
    for region in locations:
        if within_area(point_coord, locations[region]):
            return region
    return "Outside MIT"

def sign(x):
    if x > 0:
        return 1.
    elif x < 0:
        return -1.
    elif x == 0:
        return 0.
    else:
        return x
