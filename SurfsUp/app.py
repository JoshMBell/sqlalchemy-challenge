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
            f"api/v1.0/precipitation<br/>"
            f"api/v1.0/stations<br/>"
            f"api/v1.0/tobs"
        
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

if __name__ == '__main__':
    app.run(debug=True)