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
        f"<strong>Welcome to the Zack's Hawaii Climate API!</strong> <br/> <br/>"
        f"<em>Available Static Routes:</em> <br/>"
        f"<strong>/api/v1.0/precipitation</strong> <br/>"
        f"<strong>/api/v1.0/stations</strong> <br/>"
        f"<strong>/api/v1.0/tobs</strong> <br/> <br/>"
        f"<em>Available Dynamic Routes:</em> <br/>"
        f"<strong>/api/v1.0/start_date</strong> <br/>"
        f"<ul> Accepts the start date as a parameter in the URL, using this format: YYYY-MM-DD <br/>"
        f"For example: /api/v1.0/start_date/2015-8-16 <br/>"
        f"Min input date: 2010-01-01 - Max input date: 2017-08-23 <br/>"
        f"Returns the min, max, and average temperatures calculated from the given start date to the end of the dataset </ul> <br/>"
        f"<strong>/api/v1.0/start_end_date</strong> <br/>"
        f"<ul> Accepts the start date and end dates as parameters in the URL, using this format: YYYY-MM-DD <br/>"
        f"For example: /api/v1.0/start_end_date/2015-8-16/2017-1-1 <br/>"
        f"Returns the min, max, and average temperatures calculated from the given start date to the given end date from the dataset </ul> "
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

@app.route("/api/v1.0//start_date/<start>")
def tobs_by_startDate(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range. For a specified start, calculate min, max, and avg for all the dates greater than or equal to the start date."""
    # Def a func to convert the string date to datetime:
    def toDate(dateString): 
        return dt.datetime.strptime(dateString, "%Y-%m-%d").date()
    start_date = toDate(start)
    min_date = toDate("2010-1-1")
    max_date = toDate("2017-8-23")

    # If/else to return an error if start date is outside of data range:
    if start_date < min_date or start_date > max_date:
        
        return jsonify({"error": f"Date {start_date} is outside data, input date between 2010-01-01 and 2017-08-23 ."}), 404

    else:   
        # Query the data for the specified start date, calculate min, max, and avg for all the dates greater than or equal to the start date.
        start_date_qry = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date >= start_date).all()
 
        session.close()

        # Convert list of tuples into normal list
        start_date_qry_list = list(np.ravel(start_date_qry))
    
        return jsonify(start_date_qry_list)


@app.route("/api/v1.0//start_end_date/<start>/<end>")
def tobs_by_start_endDate(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range. For a specified start date and end date, calculate min, max, and avg for the dates from the start date to the end date, inclusive."""
    # Def a func to convert the string date to datetime:
    def toDate(dateString): 
        return dt.datetime.strptime(dateString, "%Y-%m-%d").date()
    start_date = toDate(start)
    end_date = toDate(end)
    min_date = toDate("2010-1-1")
    max_date = toDate("2017-8-23")

    # If/else to return an error if start or end dates are outside of data range:
    if start_date < min_date or start_date > max_date:
        
        return jsonify({"error": f"Date {start_date} is outside data, input date between 2010-01-01 and 2017-08-23 ."}), 404
    
    elif end_date < min_date or end_date > max_date:
        
        return jsonify({"error": f"Date {end_date} is outside data, input date between 2010-01-01 and 2017-08-23 ."}), 404

    else:   
        # Query the data for the specified start and end dates, calculate min, max, and avg for all the dates greater than or equal to the start date.
        start_end_date_qry = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
            filter(measurement.date >= start_date).\
            filter(measurement.date <= end_date).all()
 
        session.close()

        # Convert list of tuples into normal list
        start_end_date_qry_list = list(np.ravel(start_end_date_qry))
    
        return jsonify(start_end_date_qry_list)

if __name__ == "__main__":
    app.run(debug=True)