
"""
Lambda handler to process the APIgateway event
"""
import sys
import copy
import json
import datetime

import pymysql

import log
import queries
import app_config

logger = log.get_logger(__name__)


class RequestHandler:

    def __init__(self, event, context):
        self._event = copy.deepcopy(event)
        self._context = copy.deepcopy(context)
        self._db_config = app_config.DB_CONFIG

    def _connect(self):
        self._connection = pymysql.connect(
            self._db_config['db_host'], self._db_config['db_user'],
            self._db_config['db_passwd'], self._db_config['db_name'])

    def _run_query(self, query, req_data=False):
        try:
            with self._connection.cursor() as cur:
                cur.execute(query)
                cur.close()
                self._connection.commit()
                if req_data:
                    row_headers = [row[0] for row in cur.description]
                    row_values = cur.fetchall()
                    json_data = []
                    for value in row_values:
                        json_data.append(dict(zip(row_headers, value)))
                    return json_data
        except pymysql.Error as err:
            print(err)
            return self._respond(500, "Internal Error"+err)

    def _get(self):
        _response = self._run_query(queries.GET_ALL, True)
        return self._respond(200, _response)

    def _get_by_id(self):
        _id = (self._event["path"].split("/"))[-1]
        print(queries.GET_BY_ID.format(id=str(_id)))
        _response = self._run_query(
            queries.GET_BY_ID.format(id=str(_id)), True)
        return self._respond(200, _response)

    def _get_by_filter(self):
        query_params = self._event["queryStringParameters"]
        _filter = ' and '.join([
            f'{queries.CONDITIONS.get(prop).format(value)}'
            for prop, value in query_params.items()
        ])
        print(queries.GET_BY_FILTER.format(
            _filter=_filter
        ))
        _response = self._run_query(queries.GET_BY_FILTER.format(
            _filter=_filter
        ), True)
        return self._respond(200, _response)

    def _get_handler(self):
        return self._get_by_filter() if self._event["queryStringParameters"] else \
            (self._get() if len(self._event["path"].split(
                "/")) <= 2 else self._get_by_id())

    def _put_handler(self):
        body = json.loads(self._event["body"])
        _id = (self._event["path"].split("/"))[-1]
        if body.get("TEMPERATURE_CAPTURE_TS"):
            if not self._validate_date_format(body.get("TEMPERATURE_CAPTURE_TS")):
                return self._respond(400, "Invalid date format")

        _filter = ','.join([
            f"{prop} = '{value}'"
            for prop, value in body.items()
        ])
        self._run_query(queries.PUT.format(values=_filter, id=_id))
        return self._respond(200, "Record update successful")

    def _validate_date_format(self, date):
        try:
            datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            return True
        except Exception:
            return False

    def _post_handler(self):
        body = json.loads(self._event["body"])
        if body.get("TEMPERATURE_CAPTURE_TS"):
            if not self._validate_date_format(body.get("TEMPERATURE_CAPTURE_TS")):
                return self._respond(400, "Invalid date format")

        self._run_query(queries.INSERT.format(SENSOR_ID=body["SENSOR_ID"],
                                              TEMPERATURE_CAPTURE_TS=body["TEMPERATURE_CAPTURE_TS"],
                                              TEMPERATURE_READING=body["TEMPERATURE_READING"]
        ))
        return self._respond(200, "Record insert successful")

    def _delete_handler(self):
        _id = (self._event["path"].split("/"))[-1]
        self._run_query(queries.DELETE.format(id=_id))
        return self._respond(200, "Record delete successful")

    def _respond(self, status_code, message):
        return {
            "statusCode": status_code,
            "body": json.dumps({
                "message": message
            }, sort_keys=True, default=str),
        }

    def _request_handler(self):
        method = self._event["httpMethod"].lower()
        return getattr(self, f"_{method}_handler")()

    def process(self):
        self._connect()
        return self._request_handler()


def lambda_handler(event, context):
    """
    Lambda handler to read the event and process
    """
    logger.debug(f"lambda event  - {event}")
    try:
        return RequestHandler(event, context).process()
    except Exception as err:
        logger.error(err)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Internal Server Error"+err
            }, sort_keys=True, default=str),
        }


if __name__ == '__main__':
    event = {
        "httpMethod": "GET",
        "path": "/tags/1",
        "body": '''{
            "TEMPERATURE_CAPTURE_TS": "2011-03-14 02:53:50"
        }''',
        "queryStringParameters": '''{}'''
    }
