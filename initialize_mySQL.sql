CREATE TABLE Time (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    hour INT,
    day INT,
    month INT,
    datetime DATETIME,
    timezone VARCHAR(50)
);

CREATE TABLE Price (
    id INT AUTO_INCREMENT PRIMARY KEY,
    price DECIMAL(10,2),
    distance DECIMAL(10,2),
    surge_multiplier DECIMAL(5,2),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6)
);

CREATE TABLE Wind (
    id INT AUTO_INCREMENT PRIMARY KEY,
    windSpeed DECIMAL(5,2),
    windGust DECIMAL(5,2),
    windGustTime TIMESTAMP DEFAULT NULL,
    windBearing INT
);

CREATE TABLE Temperature (
    id INT AUTO_INCREMENT PRIMARY KEY,
    temperatureHigh DECIMAL(5,2),
    temperatureHighTime TIMESTAMP DEFAULT NULL,
    temperatureLow DECIMAL(5,2),
    temperatureLowTime TIMESTAMP DEFAULT NULL,
    temperatureMin DECIMAL(5,2),
    temperatureMinTime TIMESTAMP DEFAULT NULL,
    temperatureMax DECIMAL(5,2),
    temperatureMaxTime TIMESTAMP DEFAULT NULL
);

CREATE TABLE ApparentTemperature (
    id INT AUTO_INCREMENT PRIMARY KEY,
    apparentTemperatureHigh DECIMAL(5,2),
    apparentTemperatureHighTime TIMESTAMP DEFAULT NULL,
    apparentTemperatureLow DECIMAL(5,2),
    apparentTemperatureLowTime TIMESTAMP DEFAULT NULL,
    apparentTemperatureMin DECIMAL(5,2),
    apparentTemperatureMinTime TIMESTAMP DEFAULT NULL,
    apparentTemperatureMax DECIMAL(5,2),
    apparentTemperatureMaxTime TIMESTAMP DEFAULT NULL
);

CREATE TABLE Conditions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    icon VARCHAR(50),
    dewPoint DECIMAL(5,2),
    pressure DECIMAL(7,2),
    windBearing INT,
    cloudCover DECIMAL(3,2),
    uvIndex DECIMAL(3,2),
    visibility DECIMAL(5,2),
    ozone DECIMAL(6,2),
    sunriseTime TIMESTAMP DEFAULT NULL,
    sunsetTime TIMESTAMP DEFAULT NULL,
    moonPhase DECIMAL(3,2)
);

CREATE TABLE Weather (
    id INT AUTO_INCREMENT PRIMARY KEY,
    short_summary VARCHAR(255),
    long_summary TEXT,
    precipIntensity DECIMAL(5,2),
    precipProbability DECIMAL(3,2),
    humidity DECIMAL(3,2),
    visibility DECIMAL(5,2),
    temperature_id INT,
    apparent_temperature_id INT,
    wind_id INT,
    conditions_id INT,
    FOREIGN KEY (temperature_id) REFERENCES Temperature(id),
    FOREIGN KEY (apparent_temperature_id) REFERENCES ApparentTemperature(id),
    FOREIGN KEY (wind_id) REFERENCES Wind(id),
    FOREIGN KEY (conditions_id) REFERENCES Conditions(id)
);

CREATE TABLE Ride (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(100),
    destination VARCHAR(100),
    cab_type VARCHAR(50),
    product_id VARCHAR(50),
    name VARCHAR(100),
    price_id INT,
    time_id INT,
    weather_id INT,
    FOREIGN KEY (price_id) REFERENCES Price(id),
    FOREIGN KEY (time_id) REFERENCES Time(id),
    FOREIGN KEY (weather_id) REFERENCES Weather(id)
);

