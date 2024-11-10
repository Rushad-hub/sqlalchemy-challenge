# Import the dependencies.
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


#################################################
# Database Setup
#################################################
# Set up the Flask app
app = Flask(__name__)

# Set up the database URI
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///hawaii.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# Create the database object
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(db.engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(db.engine)

#################################################
# Flask Setup
#################################################
@app.route('/')
def index():
    return (
        f"Welcome to the Climate Data API!<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date for 12 months ago
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    # Query for precipitation data for the last 12 months
    precip_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).\
        all()

    # Convert the query results to a dictionary
    precip_dict = {date: prcp for date, prcp in precip_data}

    return jsonify(precip_dict)

@app.route('/api/v1.0/stations')
def stations():
    # Query for all station names
    stations = session.query(Station.station).all()

    # Convert list of tuples into a flat list
    station_list = [station[0] for station in stations]

    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    # Query the most active station (station with the most observations)
    most_active_station = session.query(Measurement.station, func.count(Measurement.id)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.id).desc()).first()[0]

    # Calculate the date for 12 months ago
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    # Query temperature observations for the most active station in the last year
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).\
        all()

    # Convert to a list of temperature observations
    temperature_list = [{"date": date, "tobs": tobs} for date, tobs in tobs_data]

    return jsonify(temperature_list)

@app.route('/api/v1.0/<start>')
def start_stats(start):
    # Query temperature statistics for dates >= start
    stats = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).all()

    # Convert query results into a dictionary
    temp_stats = {
        "TMIN": stats[0][0],
        "TAVG": stats[0][1],
        "TMAX": stats[0][2]
    }

    return jsonify(temp_stats)

@app.route('/api/v1.0/<start>/<end>')
def start_end_stats(start, end):
    # Query temperature statistics for dates in the range [start, end]
    stats = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Convert query results into a dictionary
    temp_stats = {
        "TMIN": stats[0][0],
        "TAVG": stats[0][1],
        "TMAX": stats[0][2]
    }

    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)
