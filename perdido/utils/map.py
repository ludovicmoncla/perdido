from typing import List, Tuple
import folium
import gpxpy


''' function get_bounding_box() returns a list containing the bottom left and the top right 
    points in the sequence '''
def get_bounding_box(points: List[float]) -> List[Tuple[float, float]]:
    bot_left_x = min(point[1] for point in points)
    bot_left_y = min(point[0] for point in points)
    top_right_x = max(point[1] for point in points)
    top_right_y = max(point[0] for point in points)
    return [(bot_left_x, bot_left_y), (top_right_x, top_right_y)]


#https://www.kaggle.com/code/paultimothymooney/overlay-gpx-route-on-osm-map-using-folium/notebook
def overlay_gpx(map: folium.Map, gpx_data:str) -> None:
    '''
    overlay a gpx route on top of an OSM map using Folium
    some portions of this function were adapted
    from this post: https://stackoverflow.com/questions/54455657/
    how-can-i-plot-a-map-using-latitude-and-longitude-data-in-python-highlight-few
    '''
    gpx_file = open(gpx_data, 'r')
    gpx = gpxpy.parse(gpx_file)
    points = []
    for track in gpx.tracks:
        for segment in track.segments:        
            for point in segment.points:
                points.append(tuple([point.latitude, point.longitude]))
    #latitude = sum(p[0] for p in points)/len(points)
    #longitude = sum(p[1] for p in points)/len(points)
    #myMap = folium.Map(location=[latitude,longitude],zoom_start=zoom)
    folium.PolyLine(points, color="red", weight=2.5, opacity=1).add_to(map)
    
