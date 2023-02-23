from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
import datetime as dt


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(autoload_with = engine)
measurement = Base.classes.measurement
station = Base.classes.station


#setup app
app = Flask(__name__)

@app.route("/")
def home():
    return (f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/start date (yyyy-mm-dd)<start><br/>"
            f"/api/v1.0/start date (yyyy-mm-dd)<start>/end date (yyyy-mm-dd)<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation_scores = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= query_date).all()
    prcp_dict = {date: prcp for date, prcp in precipitation_scores}
    session.close()
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stations = session.query(measurement.station).\
    group_by(measurement.station).all()
    station_list = [station[0] for station in stations]
    station_dict = {"All_stations": station_list}
    session.close()
    return jsonify(station_dict)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    station_count = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    one_year_ago = dt.date(2017, 8, 18) - dt.timedelta(days=365)
    results = session.query(measurement.station, measurement.date, measurement.tobs).\
    filter(measurement.station == station_count[0][0], measurement.date >= one_year_ago).\
    order_by(measurement.date).all()
    station_dict = {}
    for station, date, temp in results:
        if station not in station_dict:
            station_dict[station] = []
        station_dict[station].append({"date": date, "temp": temp})

    session.close()
    return jsonify(station_dict)


@app.route("/api/v1.0/<start>")
def calc_temps_start(start):
    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    session = Session(engine)

    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).all()
    temp_data = {}
    temp_data['TMIN'] = results[0][0]
    temp_data['TAVG'] = results[0][1]
    temp_data['TMAX'] = results[0][2]

    session.close()
    return jsonify(temp_data)


@app.route("/api/v1.0/<start>/<end>")
def calc_temps_start_end(start, end):
    session = Session(engine)

    start_date = dt.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = dt.datetime.strptime(end, '%Y-%m-%d').date()
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()
    
    temp_data = {}
    temp_data['TMIN'] = results[0][0]
    temp_data['TAVG'] = results[0][1]
    temp_data['TMAX'] = results[0][2]
    session.close()
    return jsonify(temp_data)


if __name__ == '__main__':
    app.run(debug=True)