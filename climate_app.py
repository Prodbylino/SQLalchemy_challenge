import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#data base setup
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect database
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# References to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session 
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Home page<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date 1 year ago from last date in database
    last_date = datetime.strptime(last12[0],'%Y-%m-%d')
    prev_years=last_date - timedelta(days=365)
    

    # Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()

    # Dict with date as the key and prcp as the value
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)


# @app.route("/api/v1.0/stations")
# def stations():
#     results = session.query(Station.station).all()

#     # Unravel results into a 1D array and convert to a list
#     stations = list(np.ravel(results))
#     return jsonify(stations)
@app.route("/api/v1.0/stations")
def stations():

    # Create session
    sql_driver_session = Session(engine)

    # Query for stations
    all_stations = sql_driver_session.query(Station.station, Station.name).all()
    
    # Close session
    sql_driver_session.close()

    # Convert the query results to a dictionary
    stations_list = []
    for station, name, latitude, longitude, elevation in all_stations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        stations_list.append(station_dict)

    # Return the JSON representation of dictionary
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    # Calculate the date 1 year ago from last date in database
    prev_years = dt.date(2016, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_years).all()

    # Unravel results into a 1D array and convert to a list
    tobs_list = []
    for date, temp in results:
        if temp != None:
           temp_dict = {}
           temp_dict["date"] = date
           temp_dict["temp"] = temp
           tobs_list.append(temp_dict)
    # Return the results
    return jsonify(tobs_list)


# @app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):

    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    # dict in a list
    temp_list = []
    for min, avg, max in results:
        temp_dict = {}
        temp_dict["Min"] = min
        temp_dict["Average"] = avg
        temp_dict["Max"] = max
        temp_list.append(temp_dict)

    return jsonify(temp_list)


if __name__ == '__main__':
    app.run()