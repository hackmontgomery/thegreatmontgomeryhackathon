import unittest
import datetime
import json

from django.contrib.gis.geos import Point, LineString

from stops.models import Stop, Route, Trip, TripStop


class SetFromAPITests(unittest.TestCase):

    def test_stop(self):
        json_data = """
        {
            "stop_id" : "1884",
            "stop_code" : "21884",
            "stop_name" : "EAST WEST HWY & CONNECTICUT AVE",
            "stop_lat" : 38.987993,
            "stop_lon" : -77.076255,
            "zone_id" : null,
            "stop_url" : null,
            "location_type" : null,
            "parent_station" : null,
            "uri" : "/stops/21884",
            "geometry" : {"type":"Point","coordinates":[-77.076255,38.987993]}
        }"""
        api_data = json.loads(json_data)
        stop = Stop()
        stop.set_from_api(api_data)
        self.assertEquals(1884, stop.id)
        self.assertEquals(21884, stop.stop_code)
        self.assertEquals("EAST WEST HWY & CONNECTICUT AVE", stop.stop_name)
        self.assertEquals(Point(-77.076255, 38.987993), stop.geom)

    def test_route(self):
        json_data = """
        {
            "route_id" : "2777",
            "agency_id" : "MCRO",
            "route_short_name" : " 44",
            "route_long_name" : "Twinbrook-Rockville",
            "route_desc" : null,
            "route_type" : 3,
            "route_url" : null,
            "route_color" : "0000FF",
            "route_text_color" : "FFFFFF",
            "uri" : "/routes/2777"
        }
        """
        api_data = json.loads(json_data)
        route = Route()
        route.set_from_api(api_data)
        self.assertEquals(route.id, 2777)
        self.assertEquals(route.route_short_name, " 44")
        self.assertEquals(route.route_long_name, "Twinbrook-Rockville")
        self.assertEquals(route.route_desc, None)
        self.assertEquals(route.route_color, "0000FF")
        self.assertEquals(route.route_text_color, "FFFFFF")

    def test_trip(self):
        json_data = """
        {
            "trip_id" : "425677",
            "trip_headsign" : "Twinbrook",
            "trip_short_name" : "425677",
            "shape_id" : "425677",
            "service_id" : "425677",
            "direction_id" : "425677",
            "start_time" : "425677",
            "end_time" : "425677",
            "first_stop_name" : "425677",
            "last_stop_name" : "425677",
            "uri": "/trips/425677",
            "geometry" : {
                "type": "LineString",
                "coordinates": [[-77.147223,39.084786],[-77.1473,39.084788],[-77.14736,39.084778],[-77.147406,39.084755]]
            }
        }
        """
        api_data = json.loads(json_data)
        route = Route(id=1)
        trip = Trip()
        trip.set_from_api(api_data, route)
        self.assertEquals(425677, trip.id)
        self.assertEquals(route, trip.route)
        self.assertEquals("Twinbrook", trip.trip_headsign)
        self.assertEquals(LineString(*[[-77.147223,39.084786],[-77.1473,39.084788],[-77.14736,39.084778],[-77.147406,39.084755]]),
                          trip.geom)

    def test_trip_stop(self):
        json_data = """
        {
            "arrival_time" : 67504,
            "departure_time" : 67707,
            "stop_sequence" : 2
        }
        """
        api_data = json.loads(json_data)
        stop = Stop(id=1)
        trip = Trip(id=2)
        tripstop = TripStop()
        tripstop.set_from_api(api_data, stop, trip)
        self.assertEquals(stop, tripstop.stop)
        self.assertEquals(trip, tripstop.trip)
        self.assertEquals(datetime.time(18, 45, 04), tripstop.arrival_time)
        self.assertEquals(datetime.time(18, 48, 27), tripstop.departure_time)
        self.assertEquals(2, tripstop.stop_sequence)
