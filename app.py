# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.measurement
# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)
#################################################
# Flask Routes
#################################################
@app.route('/')
def home():
    return(
        """
        <h1>Weather Observation</h1>
        <h2>Routes</h2>

        <ul>
            <li>/api/precipitation</li>
            <li>/api/stations</li>
            <li>/api/tobs</li>
        </ul>
        """
    )


@app.route('/api/v1.0/precipitation')
def precipitation():
    query = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    most_recent = dt.datetime.strptime(query, '%Y-%m-%d')
    one_year_from_last = most_recent.replace(year=most_recent.year-1)
    data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_from_last).all()
    precipitation_dict = {date:prcp for date,prcp in data}
    return jsonify(precipitation_dict)

@app.route('/api/v1.0/stations')
def stations():
    data = session.query(Station.station).group_by(Station.station).all()
    station_list = [row[0] for row in data]
    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    active_stations = session.query(Measurement.station, func.count(Measurement.id)).group_by(Measurement.station).order_by(func.count(Measurement.id).desc())
    most_active_station = active_stations.first().station
    most_recent = session.query(func.max(Measurement.date)).scalar()
    most_recent = dt.datetime.strptime(most_recent, '%Y-%m-%d')
    one_year_from_last = most_recent.replace(year=most_recent.year-1)
    most_active_station_data = session.query(Measurement.tobs, func.count(Measurement.id)).filter(Measurement.station==most_active_station).group_by(Measurement.tobs).filter(Measurement.date >= one_year_from_last).all()
    tobs_list = [row[0] for row in most_active_station_data]
    return jsonify(tobs_list)

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def temp_range(start, end=None):
    if end:
        data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    else:
        data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    print(data)
    stats = [(row[0], row[1], row[2]) for row in data]
    print(stats)
    return jsonify({'TMIN': stats[0], 'TAVG': stats[1], 'TMAX': stats[2]})


if __name__ == '__main__':
    app.run(debug=True)