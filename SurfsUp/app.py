# Import dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes for Zack's Hawaii Climate App."""
    return (
        f"Welcome to the Zack's Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value. Return the JSON representation of your dictionary."""
    # Query the last 12 months of precipitation data
    prcp_date_qry = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= dt.date(2016, 8, 23)).\
        filter(measurement.date <= dt.date(2017, 8, 23)).order_by(measurement.date).all()
        
    session.close()

    # Convert list of tuples into normal list
    prcp_list = list(np.ravel(prcp_date_qry))

    # Convert list of tuples into dict using a function:
    def Conv(x):
        it_x = iter(x)
        dict_result = dict(zip(it_x, it_x))
        return dict_result

    prcp_dict = Conv(prcp_list) 
    
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a JSON list of stations from the dataset."""
    # Query all stations
    stations = session.query(station.station).all()
        
    session.close()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(stations))
    
    return jsonify(stations_list)
    
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Query the dates and temperature observations of the most-active station for the previous year of data. Return a JSON list of temperature observations for the previous year."""
    # Query the last 12 months of precipitation data
    most_active_year_qry = session.query(measurement.station, measurement.date, measurement.tobs).\
        filter(measurement.station == "USC00519281").\
        filter(measurement.date >= dt.date(2016, 8, 23)).\
        filter(measurement.date <= dt.date(2017, 8, 23)).order_by(measurement.date).all()
 
    session.close()

    # Convert list of tuples into normal list
    most_active_year_list = list(np.ravel(most_active_year_qry))
    
    return jsonify(most_active_year_list)

@app.route("/api/v1.0/<start>")
def tobs_by_startDate(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range. For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date."""
    # Query the last 12 months of precipitation data
    start_date_qry = session.query(measurement.date, func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date >= dt.date(start)).\
        filter(measurement.date <= dt.date(end)).all()
 
    session.close()

    # Convert list of tuples into normal list
    start_date_qry_list = list(np.ravel(start_date_qry))
    
    return jsonify(start_date_qry_list)

# @app.route("/api/v1.0/<start>/<end>")
# def tobs_by_startDate(start,end):
#     # Create our session (link) from Python to the DB
#     session = Session(engine)
#     """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range. For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive."""
#     # Query the last 12 months of precipitation data
#     start_end_date_qry = session.query(measurement.date, func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
#         filter(measurement.date >= dt.date(start)).\
#         filter(measurement.date <= dt.date(end)).all()
 
#     session.close()

#     # Convert list of tuples into normal list
#     start_end_date_qry_list = list(np.ravel(start_end_date_qry))
    
#     return jsonify(start_end_date_qry_list)

if __name__ == "__main__":
    app.run(debug=True)