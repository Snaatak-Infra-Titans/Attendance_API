"""
Module for postgres related methods and class
"""

# pylint: disable=import-error,unnecessary-lambda

import os
from collections import OrderedDict
from typing import List

import yaml
import psycopg2
import psycopg2.extras

from models.message import CustomMessage, HealthMessage
from models.user_info import EmployeeInfo
from client.redis import MiddlewareSDKFacade

CONFIG_FILE = os.getenv('CONFIG_FILE', 'config.yaml')


class CorePostgresClient:
    """Class for defining the interface for Postgres Client"""

    def __init__(self):

        self.db_config = {
            "database": os.getenv("POSTGRES_DB", "attendance_db"),
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", "password"),
            "port": int(os.getenv("POSTGRES_PORT", "5432"))
        }

        self.client = None

        self.connect()

    # ==========================================================
    # Database Connection
    # ==========================================================

    def connect(self):
        """Create PostgreSQL connection"""

        try:

            self.client = psycopg2.connect(
                database=self.db_config["database"],
                host=self.db_config["host"],
                user=self.db_config["user"],
                password=self.db_config["password"],
                port=self.db_config["port"]
            )

            # IMPORTANT
            self.client.autocommit = True

            print("PostgreSQL connection established")

        except Exception as error:

            print(f"Database connection failed: {error}")

            raise error

    # ==========================================================
    # Ensure Active Connection
    # ==========================================================

    def ensure_connection(self):
        """Reconnect if connection is closed"""

        try:

            if self.client is None:
                self.connect()

            elif self.client.closed != 0:
                print("Reconnecting PostgreSQL...")
                self.connect()

        except Exception as error:

            print(f"Connection validation failed: {error}")

            self.connect()

    # ==========================================================
    # Convert DB Response
    # ==========================================================

    def _record_to_domain_model(self, response):

        return EmployeeInfo(
            id=response.get("id"),
            name=response.get("name"),
            status=response.get("status"),
            date=response.get("date")
        )

    # ==========================================================
    # Read Single Attendance
    # ==========================================================

    def read_employee_attendance(self, id_value) -> EmployeeInfo:
        """Function to read a particular employee attendance details"""

        try:

            self.ensure_connection()

            cursor = self.client.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )

            read_query = """
                SELECT id, name, status, date
                FROM records
                WHERE id = %s
            """

            cursor.execute(read_query, (id_value,))

            response = cursor.fetchone()

            cursor.close()

            if response is None:
                return None

            return self._record_to_domain_model(
                OrderedDict(response)
            )

        except Exception as error:

            print(f"read_employee_attendance error: {error}")

            return None

    # ==========================================================
    # Read All Attendance
    # ==========================================================

    def read_all_employee_attendance(self) -> List[EmployeeInfo]:
        """Function to read all employee attendance records"""

        try:

            self.ensure_connection()

            cursor = self.client.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )

            cursor.execute(
                """
                SELECT id, name, status, date
                FROM records
                ORDER BY id DESC
                """
            )

            response = cursor.fetchall()

            cursor.close()

            return list(
                map(
                    lambda _: self._record_to_domain_model(_),
                    response,
                )
            )[::-1]

        except Exception as error:

            print(f"read_all_employee_attendance error: {error}")

            return []

    # ==========================================================
    # Create Attendance
    # ==========================================================

    # pylint: disable=invalid-name,redefined-builtin

    def create_employee_attendance(self, id, name, status, date):
        """Function to create attendance record of the employee"""

        insert_query = """
            INSERT INTO records (id, name, status, date)
            VALUES (%s,%s,%s,%s)

            ON CONFLICT (id, date)

            DO UPDATE SET
                name = EXCLUDED.name,
                status = EXCLUDED.status
        """

        record_to_insert = (id, name, status, date)

        try:

            self.ensure_connection()

            cursor = self.client.cursor()

            cursor.execute(insert_query, record_to_insert)

            cursor.close()

            return CustomMessage(
                message=f"Successfully created the record for the employee id: {id}"
            )

        except Exception as error:

            print(f"create_employee_attendance error: {error}")

            return CustomMessage(
                message="Failed to create attendance record"
            )

    # ==========================================================
    # Detailed Health Check
    # ==========================================================

    def attendance_detail_health(self):
        """Function to get the detailed health of attendance API"""

        try:

            self.ensure_connection()

            cursor = self.client.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )

            cursor.execute(
                "SELECT id, name, status, date FROM records LIMIT 1"
            )

            cursor.close()

            return HealthMessage(
                message="Attendance API is running fine and ready to serve requests",
                postgresql="up",
                redis=MiddlewareSDKFacade.cache.redis_status(),
                status="up",
            ), 200

        except Exception as error:

            print(f"attendance_detail_health error: {error}")

            return HealthMessage(
                message="Attendance API is not healthy, please check logs",
                postgresql="down",
                redis=MiddlewareSDKFacade.cache.redis_status(),
                status="down",
            ), 400

    # ==========================================================
    # Basic Health Check
    # ==========================================================

    def attendance_health(self):
        """Function to get the health of attendance API"""

        try:

            self.ensure_connection()

            cursor = self.client.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )

            cursor.execute(
                "SELECT id, name, status, date FROM records LIMIT 1"
            )

            cursor.close()

            return CustomMessage(
                message="Attendance API is running fine and ready to serve requests",
            ), 200

        except Exception as error:

            print(f"attendance_health error: {error}")

            return CustomMessage(
                message="Attendance API is not healthy, please check logs",
            ), 400
