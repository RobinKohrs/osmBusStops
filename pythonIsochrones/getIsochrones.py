import requests
import json
import os
import sys

key = "r7q-nvV9wqOzMKfEQpcE0d-yfzrnamM-dh-7PPN3yCM"
url = "https://isoline.route.ls.hereapi.com/routing/7.2/calculateisoline.json"


def readData(path):

    with open(path, "r") as path:
        data = json.load(path)

    
    stations = []
    for s in data["features"]:
        id = s["properties"]["id"]
        coords = s["geometry"]["coordinates"]
        data = {"id": id, "coords": coords}
        stations.append(data)
    
    return stations


def buildQueries(data, times):

    queries_all_origins = []

    for origin in data:
        queries_one_origin = []
        for t in times:
            coords = origin["coords"]
            rp = {
                "apiKey": key,
                "mode": "shortest;pedestrian;traffic:disabled",
                "start": f'geo!{coords[1]},{coords[0]}',
                "range": t,
                "rangetype": "time"
            }

            query = {"id": origin["id"], "params": rp}
            queries_one_origin.append(query)

        # after going through all the times for one origin, append this list to the list of all origins
        queries_all_origins.append(queries_one_origin)

    return queries_all_origins

def getCoords(data):

    coords = data["response"]["isoline"][0]["component"][0]["shape"]
    coords = [[x.split(",")[1],x.split(",")[0]] for x in coords]

    return coords


def makeGj(coords, ID, r):
    gj = {"type": "Feature", "properties": {"id": ID, "range": r}, "geometry": {"type": "Polygon", "coordinates": [coords]}}
    return gj

def sendqueries_savedata(queries, data_dir):

    for origin in queries:
        results_one_origin = []
        for t in origin:
            # one file for each origin and time
            ID = t["id"]
            r =  t["params"]["range"]
            f = f'{data_dir}/{ID}_{r}.json'
            if not os.path.isfile(f):
                resp = requests.get(url, t["params"])
                data = resp.json()
                coords = getCoords(data)
                gj = makeGj(coords, ID, r)
                print(gj)
                with open(f, "w") as file:
                    json.dump(gj, file)
                    exit()

def main():

    # get the coordinates and the ids from the stations geojson
    stations = "../osmBusStops/data/stations.geojson"
    data = readData(stations)

    # build the queries
    # the structure is mulitple queries for one origin for all times
    times = [x * 60 for x in range(5)]
    queries = buildQueries(data, times)

    ## send queries and save data
    data_dir = "./data"
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)

    sendqueries_savedata(queries, data_dir)


if __name__ == "__main__":
    main()