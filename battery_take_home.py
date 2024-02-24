# @Author: Pushpak Dubey

import csv
from abc import ABC, abstractmethod
import os

# Constants
BATTERY_CAPACITY = 100  # in kWh
EFFICIENCY = 0.90  # 90% efficiency


class CSVFileHandler:
    """The CSVFileHandler class provides utility functions to support the main library."""

    @staticmethod
    def read_csv(file_path, expected_field=None):
        CSVFileHandler.check_file(file_path)
        with open(file_path, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            if expected_field:
                assert CSVFileHandler.check_expected_fields(reader,
                                                            expected_field), "Missing column in csv file. Please check again."
            return list(reader)

    @staticmethod
    def check_file(file_path):
        assert file_path.endswith("csv"), "Invalid file type. Please provide a CSV file."
        assert os.path.isfile(file_path), f"The file '{file_path}' does not exist. Please check the file path."
        assert os.path.exists(file_path), f"The file '{file_path}' cannot be found. Please verify the file path."

    @staticmethod
    def check_expected_fields(csv_reader, expected_fields):
        return all(i in csv_reader.fieldnames for i in expected_fields)


class Battery(ABC):
    """Battery is an abstract base class that defines the interface for all batteries."""

    @abstractmethod
    def calculateSoc(self, hour, power, current_soc):
        """Calculates and returns the State of Charge (SOC) of the battery."""
        pass


class BatteryImpl(Battery):
    """BatteryImpl is a concrete class that implements the Battery interface."""

    def calculateSoc(self, hour, power, current_soc):
        """Calculates and returns the State of Charge (SOC) of the battery."""
        assert isinstance(hour, (int, float)), "Invalid input: 'hour' should be a number."
        assert isinstance(power, (int, float)), "Invalid input: 'power' should be a number."
        assert isinstance(current_soc, (int, float)), "Invalid input: 'current_soc' should be a number."
        assert 0 <= current_soc <= 1, "Invalid input: 'current_soc' should be between 0 and 1"
        energy = power * hour
        loss = energy * (1 - EFFICIENCY)
        current_soc = current_soc - (energy + abs(loss)) * 0.01
        return current_soc


class PowerCalculator:
    """PowerCalculator class is responsible for calculating and printing the SOC at each time step."""

    def __init__(self, battery: Battery, csv_reader: CSVFileHandler):
        self.battery = battery
        self.csv_reader = csv_reader

    def calculate(self, file_path):
        """Calculates and prints the SOC at each time step."""
        try:
            data = self.csv_reader.read_csv(file_path)
            soc = 0.80
            print("Time,Power,SOC")
            prev_time = None
            for row in data:
                current_time = row['Time']
                if prev_time:
                    # Calculate time difference in hours
                    hour, minute = map(int, current_time.split(':'))
                    current_time_in_hours = hour + minute / 60
                    hour, minute = map(int, prev_time.split(':'))
                    prev_time_in_hours = hour + minute / 60
                    time_gap = current_time_in_hours - prev_time_in_hours
                else:
                    time_gap = 0.5  # Default value for the first time step
                prev_time = current_time
                power = int(row['Power'])
                soc = self.battery.calculateSoc(time_gap, power, soc)
                print(f"{row['Time']},{row['Power']},{soc:.2f}")
        except Exception as e:
            print(f"Failed to calculate due to : {e}")


# Usage

file = "power_over_time.csv"

if file:
    csv_reader = CSVFileHandler()
    battery = BatteryImpl()
    calculator = PowerCalculator(battery, csv_reader)
    calculator.calculate(file)
else:
    print("Please provide a file")
