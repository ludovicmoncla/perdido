from typing import Dict
from sklearn.cluster import DBSCAN
import pandas as pd
from geopy.distance import great_circle


def geojson2df(resJson: Dict):

    lst = []
    for t in resJson['features']:
        id = t["properties"]["id"]
        name = t["properties"]["name"]
        source = t["properties"]["source"]
        source_name = t["properties"]["sourceName"]
        country = t["properties"]["country"]
        latitude = t["geometry"]["coordinates"][1]
        longitude = t["geometry"]["coordinates"][0]

        lst.append([id, name, source, source_name, country, latitude, longitude])
        
    return pd.DataFrame(lst, columns =['xmlID', 'name', 'source', 'sourceName', 'country', 'latitude', 'longitude'])


def df2geojson(df, properties, lat='latitude', lon='longitude'):
    geojson = {'type':'FeatureCollection', 'features':[]}

    # loop through each row in the dataframe and convert each row to geojson format
    for _, row in df.iterrows():
        # create a feature template to fill in
        feature = {'type':'Feature',
                'properties':{},
                'geometry':{'type':'Point',
                            'coordinates':[]}}

        # fill in the coordinates
        feature['geometry']['coordinates'] = [row[lon],row[lat]]

        # for each column, get the value and add it as a new feature property
        for prop in properties:
            feature['properties'][prop] = row[prop]
        
        # add this feature (aka, converted dataframe row) to the list of features inside our dict
        geojson['features'].append(feature)
    
    return geojson

def gdf2geojson(df, properties):
    geojson = {'type':'FeatureCollection', 'features':[]}

    # loop through each row in the dataframe and convert each row to geojson format
    for _, row in df.iterrows():
        # create a feature template to fill in
        feature = {'type':'Feature',
                'properties':{},
                'geometry':{'type':'Point',
                            'coordinates':[]}}

        # fill in the coordinates
        feature['geometry']['coordinates'] = [row['geometry'].x, row['geometry'].y]

        # for each column, get the value and add it as a new feature property
        for prop in properties:
            feature['properties'][prop] = row[prop]
        
        # add this feature (aka, converted dataframe row) to the list of features inside our dict
        geojson['features'].append(feature)
    
    return geojson

# e : Epsilon, the maximum distance between two samples for one to be considered as in the neighborhood of the other
def clustering_disambiguation(p, e = 0.1):

    df = geojson2df(p.geojson)
    data = df.loc[:,['latitude', 'longitude']]
    if len(data) >= 3:
        clusterer = DBSCAN(eps = e)

        df["cluster"] = clusterer.fit_predict(data)
        if len(df[df.cluster != -1]) > 0:   
            best_cluster = df[df.cluster != -1].cluster.value_counts().idxmax()
            #df['cluster'] = np.where(df['cluster'] == bestCluster, bestCluster, -1)
            df2 = df[df.cluster == best_cluster].reset_index(drop=True)
        
            return df2geojson(df2, df2.columns), df2geojson(df, df.columns), best_cluster
        
    return df2geojson(df, df.columns), None, None


def compute_distances(gdf):
    distances = {}

    for index1, row1 in gdf.iterrows():
        if gdf['name'].value_counts().get(row1['name'], 0) > 1:
            t1 = (index1, row1['name'])
            d = {}
            for index2, row2 in gdf.iterrows():
                if row1['name'] != row2['name']:
                    dist = great_circle((row1['geometry'].y, row1['geometry'].x), (row2['geometry'].y, row2['geometry'].x)).km
                    if row2['name'] not in d:
                        d[row2['name']] = dist
                    else:
                        if dist < d[row2['name']]:
                            d[row2['name']] = dist
            distances[t1] = d
    return distances


def get_sum_minimal_distances(gdf):
    distances = compute_distances(gdf)

    for index1, row1 in gdf.iterrows():
        d = 0
        if gdf['name'].value_counts().get(row1['name'], 0) > 1:
            for context_toponym, dist in distances[(index1, row1['name'])].items():
                d += dist
        gdf.loc[index1,'sum_minimal_distances'] = d
    return gdf


def minimal_distances_disambiguation(gdf):

    gdf = get_sum_minimal_distances(gdf)

    gdf_n = gdf.loc[gdf.groupby("name")["sum_minimal_distances"].idxmin()].reset_index(drop=True)

    return gdf2geojson(gdf_n, gdf_n.columns), gdf2geojson(gdf, gdf.columns)