import datetime
import time

from django.contrib.gis.db import models
from django.contrib.gis.geos import Point, LineString
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField


class Stop(models.Model):
    """
    A single bus stop (e.g. ROCKVILLE STATION & BAY F - WEST).  One or more routes (e.g. 44 Rockville)
    go through a single stop.
    Example api: http://rideonrealtime.net/stops/25662
    api docs: http://kb.g-and-o.com/wiki/index.php/Live_Transit_API/API/stops/:code
    """
    created_at = CreationDateTimeField()
    modified_at = ModificationDateTimeField()

    id = models.IntegerField(primary_key=True)  # stop_id from API values
    stop_code = models.IntegerField()
    stop_name = models.CharField(max_length=300)
    geom = models.PointField()

    def set_from_api(self, api_data):
        """
        Sets the object's attributes from json API data.

        @api_data: dict of json API data for the stop. See example at bottom of
                   this source file for what the data looks like.
        """
        if self.id is not None and int(api_data['stop_id']) != self.id:
            raise ValueError("Stop #%s in database can't be set with stop #%s from api." %
                             (self.id, api_data['stop_id']))
        self.stop_code = int(api_data['stop_code'])
        self.stop_name = api_data['stop_name'][:300]  # todo: add logging if value greater than 300
        self.geom = Point(api_data['stop_lon'], api_data['stop_lat'])


class Route(models.Model):
    """
    A single route, i.e. what the destination sign will say on the top of a bus (e.g. 44 Rockville).
    Example: http://www.montgomerycountymd.gov/DOT-Transit/routesandschedules/allroutes/route044.html
    Example api: http://rideonrealtime.net/routes/2777
    api docs: http://kb.g-and-o.com/wiki/index.php/Live_Transit_API/API/routes/:id
    """
    created_at = CreationDateTimeField()
    modified_at = ModificationDateTimeField()

    id = models.IntegerField(primary_key=True)  # route_id from API values
    route_short_name = models.CharField(max_length=300, null=True)
    route_long_name = models.CharField(max_length=300, null=True)
    route_desc = models.TextField(null=True)
    route_color = models.CharField(max_length=6, default="000000")
    route_text_color = models.CharField(max_length=6, default="000000")

    def set_from_api(self, api_data):
        """
        Sets the object's attributes from json API data.

        @api_data: dict of json API data for the route. See example at bottom of
                   this source file for what the data looks like.
        """
        if self.id is not None and int(api_data['route_id']) != self.id:
            raise ValueError("Route` #%s in database can't be set with route #%s from api." %
                             (self.id, api_data['route_id']))
        self.route_short_name = api_data['route_short_name'][:300]
        self.route_long_name = api_data['route_long_name'][:300]
        self.route_desc = api_data['route_desc'] or None
        self.route_color = api_data['route_color'] or None
        self.route_text_color = api_data['route_text_color'] or None


class Trip(models.Model):
    """
    A scheduled trip for a route, (e.g. The 44 Rockville bus that stops at X, Y, and Z at 6:15am, 6:25am, and 6:53am).
    A trip has multiple stops.
    Example: http://www6.montgomerycountymd.gov/apps/dot-transit/routesandschedules/allroutes/route_schedules/route44.asp?sched=weekday&routename=44&routecode=1
    Example api: http://rideonrealtime.net/trips/425677
    api docs: http://kb.g-and-o.com/wiki/index.php/Live_Transit_API/API/trips/:id
    """
    created_at = CreationDateTimeField()
    modified_at = ModificationDateTimeField()

    id = models.IntegerField(primary_key=True)  # trip_id from API values
    trip_headsign = models.CharField(max_length=300)
    geom = models.LineStringField()

    def set_from_api(self, api_data):
        """
        Sets the object's attributes from json API data.

        @api_data: dict of json API data for the trip. See example at bottom of
                   this source file for what the data looks like.
        """
        if self.id is not None and int(api_data['route_id']) != self.id:
            raise ValueError("Trip` #%s in database can't be set with trip #%s from api." %
                             (self.id, api_data['route_id']))
        self.trip_headsign = api_data['trip_headsign'][:300]
        self.geom = LineString(*[coord for coord in api_data['geometry']['coordinates']])


class TripStop(models.Model):
    """
    A stop on a scheduled trip (e.g. The 44 Rockville stopping at ROCKVILLE STATION & BAY F - WEST).
    Example api: http://rideonrealtime.net/trips/425677
    api docs: http://kb.g-and-o.com/wiki/index.php/Live_Transit_API/API/trips/:id
    """
    created_at = CreationDateTimeField()
    modified_at = ModificationDateTimeField()

    trip = models.ForeignKey(Trip)
    stop = models.ForeignKey(Stop)
    arrival_time = models.TimeField()
    departure_time = models.TimeField()
    stop_sequence = models.IntegerField()

    def set_from_api(self, api_data, trip):
        """
        Sets the object's attributes from json API data.

        @api_data: dict of json API data for the stop on a trip. See example at bottom of
                   this source file for what the data looks like.
        """
        self.trip = trip
        self.stop = Stop.objects.get(id=int(api_data['stop']['stop_id']))
        arrtime = time.gmtime(int(api_data['arrival_time']))
        self.arrival_time = datetime.time(arrtime.tm_hour, arrtime.tm_min, arrtime.tm_sec)
        deptime = time.gmtime(int(api_data['departure_time']))
        self.departure_time = datetime.time(deptime.tm_hour, deptime.tm_min, deptime.tm_sec)
        self.stop_sequence = int(api_data['stop_sequence'])


"""
API Examples:

Data for Stop model
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
}

Data for Route model
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

Data for Trip model
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
}

Data for TripStop model
{
  "arrival_time" : 67504,
  "departure_time" : 67504,
  "stop_sequence" : 2,
  "stop" : {
    "stop_name" : "MONROE ST & MONROE PL",
    "stop_code" : "24150",
    "stop_id" : "4150",
    "uri" : "/stops/4150"
  }
}
"""