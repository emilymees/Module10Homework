# Import the dependencies.

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()
# reflect the tables
base.prepare(autoload_with=engine)

# Save references to each table
station = base.classes.station
measurement = base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

# home 
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes for Hawaii Weather Data: <br/><br/><br/>"
        f"Precipitation for Previous 12 Months:  /api/v1.0/precipitation<br/><br/>"
        f"List of Active Weather Stations:  /api/v1.0/stations<br/><br/>"
        f"Temperature Data for Previous 12 Months:  /api/v1.0/tobs<br/><br/>"
        f"Minimum, Average, and Maximum Temperatures for A Specified Start Date:  /api/v1.0/StartDate<br/> (Replace StartDate in address with yyyy-mm-dd format)<br/><br/>"
        f"Minimum, Average, and Maximum Temperatures for A Specified Start and End Date:  /api/v1.0/StartDate/EndDate<br/> (Replace StartDate and EndDate in address with yyyy-mm-dd format)<br/>"
    )


# precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    session = Session(engine)

    prev_12_months = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date > "2016-08-22").\
        order_by(measurement.date.desc()).all()

    session.close()

    prcp_data = []
    for date, prcp in prev_12_months:
        date_dict = {}
        date_dict[date] = prcp
        prcp_data.append(date_dict)
    
    return jsonify(prcp_data)


# stations list
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    total_active_stations = session.query(measurement.station).\
        group_by(measurement.station).\
        order_by(func.count(measurement.station).desc()).all()

    session.close()

    station_list = list(np.ravel(total_active_stations))

    return jsonify(station_list)


# tobs data
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    active_12_months = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date > "2016-08-22").\
        filter(measurement.station == "USC00519281").all()

    session.close()

    tobs_data = []
    for date, tobs in active_12_months:
        tobs_date_dict = {}
        tobs_date_dict[date] = tobs
        tobs_data.append(tobs_date_dict)

    return jsonify(tobs_data)
    

# min, avg, max data based on user defined start date to end of dataset
@app.route("/api/v1.0/<start>")
def start_date(start):

    session = Session(engine)

    start_functions = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        group_by(measurement.date).all()
    
    session.close()

    start_data = []
    for date, min, avg, max in start_functions:
        start_dict = {}
        start_dict["Date"] = date
        start_dict["TMIN"] = min
        start_dict["TAVG"] = avg
        start_dict["TMAX"] = max
        start_data.append(start_dict)

    return jsonify(start_data)


# min, avg, max data based on user defined start and end date
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):

    session = Session(engine)

    start_end_functions = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).\
        filter(measurement.date <= end).\
        group_by(measurement.date).all()
    
    session.close()

    start_end_data = []
    for date, min, avg, max in start_end_functions:
        start_end_dict = {}
        start_end_dict["Date"] = date
        start_end_dict["TMIN"] = min
        start_end_dict["TAVG"] = avg
        start_end_dict["TMAX"] = max
        start_end_data.append(start_end_dict)

    return jsonify(start_end_data)


if __name__ == '__main__':
    app.run(debug=True)
 