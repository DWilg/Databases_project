CREATE TABLE Time (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP,
    hour INT,
    day INT,
    month INT,
    datetime TIMESTAMP,
    timezone VARCHAR(50)
);

CREATE TABLE Price (
    id SERIAL PRIMARY KEY,
    price DECIMAL,
    distance DECIMAL,
    surge_multiplier DECIMAL,
    latitude DECIMAL,
    longitude DECIMAL
);


CREATE TABLE Wind (
    id SERIAL PRIMARY KEY,
    windSpeed DECIMAL,
    windGust DECIMAL,
    windGustTime TIMESTAMP,
    windBearing INT
);

CREATE TABLE Temperature (
    id SERIAL PRIMARY KEY,
    temperatureHigh DECIMAL,
    temperatureHighTime TIMESTAMP,
    temperatureLow DECIMAL,
    temperatureLowTime TIMESTAMP,
    temperatureMin DECIMAL,
    temperatureMinTime TIMESTAMP,
    temperatureMax DECIMAL,
    temperatureMaxTime TIMESTAMP
);

CREATE TABLE ApparentTemperature (
    id SERIAL PRIMARY KEY,
    apparentTemperatureHigh DECIMAL,
    apparentTemperatureHighTime TIMESTAMP,
    apparentTemperatureLow DECIMAL,
    apparentTemperatureLowTime TIMESTAMP,
    apparentTemperatureMin DECIMAL,
    apparentTemperatureMinTime TIMESTAMP,
    apparentTemperatureMax DECIMAL,
    apparentTemperatureMaxTime TIMESTAMP
);

CREATE TABLE Conditions (
    id SERIAL PRIMARY KEY,
    icon VARCHAR(50),
    dewPoint DECIMAL,
    pressure DECIMAL,
    windBearing INT,
    cloudCover DECIMAL,
    uvIndex DECIMAL,
    visibility DECIMAL,
    ozone DECIMAL,
    sunriseTime TIMESTAMP,
    sunsetTime TIMESTAMP,
    moonPhase DECIMAL
);

CREATE TABLE Weather (
    id SERIAL PRIMARY KEY,
    short_summary VARCHAR(255),
    long_summary TEXT,
    precipIntensity DECIMAL,
    precipProbability DECIMAL,
    humidity DECIMAL,
    visibility DECIMAL,
    temperature_id INT REFERENCES Temperature(id),
    apparent_temperature_id INT REFERENCES ApparentTemperature(id),
    wind_id INT REFERENCES Wind(id),
    conditions_id INT REFERENCES Conditions(id)
);

CREATE TABLE Ride (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100),
    destination VARCHAR(100),
    cab_type VARCHAR(50),
    product_id VARCHAR(50),
    name VARCHAR(100),
    price_id INT REFERENCES Price(id),
    time_id INT REFERENCES Time(id),
    weather_id INT REFERENCES Weather(id)
);