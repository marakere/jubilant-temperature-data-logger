"""
DML statements
"""

INSERT = """
    INSERT INTO RECORD_TEMPERATURE (SENSOR_ID ,TEMPERATURE_READING, TEMPERATURE_CAPTURE_TS)
    VALUES ('{SENSOR_ID}' ,'{TEMPERATURE_READING}', '{TEMPERATURE_CAPTURE_TS}')
"""

GET_ALL = """
    SELECT * FROM RECORD_TEMPERATURE;
"""

GET_BY_FILTER = """
    SELECT * FROM RECORD_TEMPERATURE WHERE {_filter}
"""

GET_BY_ID = """
    SELECT * FROM RECORD_TEMPERATURE WHERE sensor_id = {id}
"""

PUT = """
    UPDATE RECORD_TEMPERATURE SET {values} WHERE sensor_id = {id}
"""

DELETE = """
    DELETE from RECORD_TEMPERATURE WHERE sensor_id = {id}
"""

CONDITIONS = {
    "start_date": "date(TEMPERATURE_CAPTURE_TS) >= '{0}'",
    "end_date": "date(TEMPERATURE_CAPTURE_TS) <= '{0}'",
    "sensor_id": "sensor_id = '{0}'"
}
