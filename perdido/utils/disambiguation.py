from typing import Dict
from sklearn.cluster import DBSCAN
import pandas as pd


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