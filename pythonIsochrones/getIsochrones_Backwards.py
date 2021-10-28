import requests
import json
import os
import sys
import re
import random
import subprocess
import math

key = "AttyqYk0OQNaMJY7MIDLF2nD1Fm3qCnyYMyO70qdPX8"
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
    coords = [[float(x.split(",")[1]), float(x.split(",")[0])] for x in coords]
    return coords


def makeGj(coords, ID, r):
    gj = {"type": "Feature", "properties": {"id": ID, "range": r},
          "geometry": {"type": "Polygon", "coordinates": [coords]}}
    return gj


def sendqueries_savedata(queries, data_dir):
    """

    """

    # lengths for printing super informative message
    len_origins = len(queries)
    len_times = len(queries[0])

    # for each origin
    for i, origin in enumerate(queries[::-1]):
        print(f"\nProcessing: {i} / {len_origins} origins")
        # sys.stdout.write(f"\nProcessing: {i} / {len_origins} origins\r")

        results_one_origin = []

        # for each time
        for i, t in enumerate(origin):
            # one file for each origin and time
            ID = t["id"]
            r = t["params"]["range"]

            sys.stdout.write(f"    Getting: {r} minutes \r")

            # check if file aready present
            f = f'{data_dir}/{ID}_{r}.json'
            if not os.path.isfile(f):
                print(f"{f} does not yet exist")
                try:
                    resp = requests.get(url, t["params"], timeout=None)
                    if resp.ok:
                        data = resp.json()
                        coords = getCoords(data)
                        gj = makeGj(coords, ID, r)
                        with open(f, "w") as file:
                            json.dump(gj, file)
                    else:
                        with open(f, "w") as file:
                            json.dump({"resp": "No way possible"}, file)
                except:
                    continue
            else:
                print(f"{f} does already exist")
                continue

    return


def buildMultipolygons(paths, data_dir):
    nr = r".*_(\d+)"
    unique_numbers = set([re.search(nr, x).group(1) for x in paths])

    # for each time, get all the matching sinlge polgons
    for i, t in enumerate(unique_numbers):

        # file for all polgons with one time duration
        f = f"{data_dir}/{t}_all.geojson"
        if not os.path.isfile(f):
            sys.stdout.write(
                f"Building Multipolyon: {i} / {len(unique_numbers)}")

            multiPoly = {"type": "FeatureCollection",
                         "features": []}
            # reg = r"_" + t + "$"
            pat = re.compile(".*_" + t + ".json$")
            files = [x for x in paths if pat.match(x)]

            for origin in files:
                try:
                    with open(origin, "r") as file:
                        singlePoly = json.load(file)
                        # print(type(singlePoly["geometry"]
                        #       ["coordinates"][0][0][0]))
                        multiPoly["features"].append(singlePoly)
                except:
                    continue

            with open(f, "w") as outFile:
                json.dump(multiPoly, outFile)


def rasterize(indir, outdir):
    mp = [os.path.join(indir, f)
          for f in os.listdir(indir) if f.endswith(".geojson")]

    for m in mp:
        filename, extenstion = os.path.splitext(m)
        outfile = os.path.join(outdir, filename.split("/")[-1]) + ".tif"

        # -a_nodata 0
        cmd = f"gdal_rasterize -burn 255 -burn 0 -burn 0 -burn 100 -at -tr .005 .005 -ot Byte {m} {outfile}"
        subprocess.run(cmd, shell=True)

    return mp


def main():

    # get the coordinates and the ids from the stations geojson
    stations = "./stations.geojson"
    # stations = "../../../../Desktop/missing.geojson"
    # data = readData(stations)
    # # data = random.sample(data, 10000)

    # # build the queries
    # # the structure is mulitple queries for one origin for all times
    times = [5, 10, 15, 20, 30, 45, 60, 90, 120]
    times = [x * 60 for x in times]

    # queries = buildQueries(data, times)

    # send queries and save data
    data_dir = "./data"
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)
    sendqueries_savedata(queries, data_dir)

    # Read results back in and process them
    gjs = [os.path.join(data_dir, x)
           for x in os.listdir(data_dir) if x.endswith(".json")]

    # build the multipolygons for each time step
    data_all = "./data/multipolygons"
    if not os.path.isdir(data_all):
        os.mkdir(data_all)
    multipolygons = buildMultipolygons(gjs, data_all)

    # rasterize the multipolygons
    raster_dir = os.path.join(data_all, "raster")
    if not os.path.isdir(raster_dir):
        os.mkdir(raster_dir)

    res = rasterize(data_all, raster_dir)
    print()
    print(res)


if __name__ == "__main__":
    main()
