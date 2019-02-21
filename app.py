import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#define engine
#engine = create_engine("sqlite:///Instructions/Resources/hawaii.sqlite")
engine = create_engine("sqlite:///Instructions/Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# create the base with automap
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
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
        f"Available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"- Precipitation Stats From All Stations<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"- Station Deets<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"- Temp Observations<br/>"
        f"<br/>"
        f"/api/v1.0/start<br/>"
        f"- Min, Max and Avg temps based on dates greater than or equal to start date<br/>"
        f"<br/>"
        f"/api/v1.0/start/end<br/>"
        f"- Min, Max and Avg temps for dates between the start and end date inclusive<br/>"

    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    results = session.query(Measurement).all()

    all_Measurement = []
    for meas in results:
        measurement_dict = {}
        measurement_dict["date"] = meas.date
        measurement_dict["prcp"] = meas.prcp
        all_Measurement.append(measurement_dict)

    return jsonify(all_Measurement)


@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)


@app.route("/api/v1.0/tobs")
def tobs():
    twelve_months_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    station_observation = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date > twelve_months_ago).\
    order_by(Measurement.date).all()

    #all_tobs = list(np.ravel(station_observation))
    return jsonify(station_observation)

@app.route("/api/v1.0/<start>")
def given_date(start):
    """Return the average temp, max temp, and min temp for the date"""
    results = session.query(Measurement.date, func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date == start).all()

    data_list = []
    for result in results:
        row = {}
        row['Date'] = result[0]
        row['Average Temperature'] = float(result[1])
        row['Highest Temperature'] = float(result[2])
        row['Lowest Temperature'] = float(result[3])
        data_list.append(row)

    return jsonify(data_list)

@app.route("/api/v1.0/<start>/<end>")
def query_dates(start, end):
    results = session.query(func.avg(Measurement.tobs), func.max(Measurement.tobs), func.min(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()

    data_list = []
    for result in results:
        row = {}
        row["Start Date"] = start
        row["End Date"] = end
        row["Average Temperature"] = float(result[0])
        row["Highest Temperature"] = float(result[1])
        row["Lowest Temperature"] = float(result[2])
        data_list.append(row)
    return jsonify(data_list)
    
#____________________________
if __name__ == "__main__":
    app.run(debug=True)
