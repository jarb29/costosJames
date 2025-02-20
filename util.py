from typing import Dict, Union
from collections import defaultdict
from decimal import Decimal
import pandas as pd


def calculate_tiempo_corte(data, averages):
    for item in data:
        espesor_avg = averages.get(str(item['espesor']))  # convert Decimal to string
        if espesor_avg is not None:
            item['tiempo_corte'] = round(float(item['metros'])/espesor_avg, 2)  # convert Decimal to float and round to 2 decimal places
    return data


def average_dict_values(data_dict: Dict[str, Dict[str, Union[float, Decimal]]]) -> Dict[str, Decimal]:
    result = defaultdict(float)
    count = defaultdict(int)

    for outer_key, inner_data in data_dict.items():
        for inner_key, values in inner_data.items():
            result[inner_key] += float(values)
            count[inner_key] += 1

    # Calculate the average and round it to 2 decimal places:
    return {k: round(result[k] / count[k], 2) for k in result}

def calculate_tiempo_corte(data, averages):
    for item in data:
        espesor_avg = averages.get(str(item['espesor']))  # convert Decimal to string
        if espesor_avg is not None:
            item['tiempo_corte'] = round(float(item['metros'])/espesor_avg, 2)  # convert Decimal to float and round to 2 decimal places
    return data


def sum_up_values(data):
    summed_data = {}
    for pv, items in data.items():
        total_kg = sum(float(item['kg']) for item in items)

        total_tiempo_corte = sum(float(item['time']) if 'time' in item else 0 for item in items)

        summed_data[pv] = {
            'total_kg': round(total_kg, 2),
            'total_tiempo_corte': round(total_tiempo_corte, 2)
        }

    return summed_data

def calculate_total_price(data: dict, kg_price: float, time_price: float) -> dict:
    new_data = {}
    for key, value in data.items():
        new_data[key] = {
            "total_kg": value["total_kg"],
            "total_tiempo_corte": value["total_tiempo_corte"],
            "precio_kg": round(value["total_kg"] * kg_price, 2),
            "precio_tiempo": round(value["total_tiempo_corte"] * time_price, 2)
        }
    return new_data

def convert_dict_to_df(data):
    df = pd.DataFrame.from_dict(data, orient='index')
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'pv'}, inplace=True)

    return df

from datetime import datetime
def get_months_and_years_since(date_str):

    initial_date = datetime.strptime(date_str, "%d/%m/%Y")
    current_date = datetime.now()

    months = set()
    years = set()

    while initial_date <= current_date:
        months.add(initial_date.month)
        years.add(initial_date.year)
        initial_date = add_months(initial_date, 1)

    # Separate current month and year
    cur_month = current_date.month
    cur_year = current_date.year

    return sorted(list(months)), sorted(list(years)), cur_month, cur_year


def add_months(date, months):
    month = date.month - 1 + months
    year = date.year + month // 12
    month = month % 12 + 1
    day = min(date.day, [31,29,31,30,31,30,31,31,30,31,30,31][month-1])
    return datetime(year, month, day)



from datetime import datetime
from typing import List, Dict, Any


def process_grouped_data(grouped_data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, str]]:
    """
    Process the grouped data to extract the newest 'closeAt' date for each 'pv' in YYYY-MM-DD format.

    Args:
    - grouped_data: A dictionary where each key is a 'pv' and the value is a list of dictionaries containing 'closeAt' dates.

    Returns:
    - A list of dictionaries containing 'pv' and the newest 'closeAt' date in YYYY-MM-DD format.
    """

    def extract_date_ymd(timestamp: str) -> str:
        """
        Extract the date in YYYY-MM-DD format from an ISO 8601-formatted timestamp string.

        Args:
        - timestamp: An ISO 8601-formatted timestamp string.

        Returns:
        - The date as a string in YYYY-MM-DD format.
        """
        if timestamp.endswith('Z'):
            timestamp = timestamp[:-1]
        datetime_obj = datetime.fromisoformat(timestamp)
        return datetime_obj.strftime('%Y-%m-%d')

    def find_newest_date(dates: List[str]) -> str:
        """
        Find the newest date from a list of ISO 8601-formatted date strings.

        Args:
        - dates: A list of ISO 8601-formatted date strings.

        Returns:
        - The newest date as an ISO 8601-formatted date string.
        """
        datetime_dates = [datetime.fromisoformat(date.replace('Z', '+00:00')) for date in dates]
        newest_date = max(datetime_dates)
        return newest_date.isoformat() + 'Z'

    results = []
    for pv, data in grouped_data.items():
        closeAt_dates = [item['closeAt'] for item in data if 'closeAt' in item]
        if closeAt_dates:
            newest_date = find_newest_date(closeAt_dates)
            results.append({'pv': pv, 'closeAt': extract_date_ymd(newest_date)})

    return results

from typing import List, Dict, Any


def filter_by_year_month(data: List[Dict[str, Any]], year: int, month: int) -> List[str]:
    """
    Filter the list of pv based on the given year and month.

    Args:
    - data: A list of dictionaries where each dictionary contains 'pv' and 'closeAt' keys.
    - year: The year to filter by.
    - month: The month to filter by.

    Returns:
    - A list of 'pv' strings that match the given year and month.
    """
    filtered_pvs = []
    for item in data:
        close_at_date = item.get('closeAt')
        if close_at_date:
            date_parts = close_at_date.split('-')
            item_year = int(date_parts[0])
            item_month = int(date_parts[1])

            if item_year == year and item_month == month:
                filtered_pvs.append(item['pv'])

    return filtered_pvs

def round_to_two_decimals(value: float) -> float:
    """
    Rounds a floating-point number to two decimal places.

    Args:
    - value: The floating-point number to round.

    Returns:
    - The number rounded to two decimal places.
    """
    return round(value, 2)




def round_to_two_decimals2(num):
    """Rounds a number to two decimal places and formats it with thousands separators."""
    formatted_num = "{:,.2f}".format(num).replace(",", ".")
    # Remove the last two characters (".00") if they exist
    if formatted_num.endswith(".00"):
        formatted_num = formatted_num[:-3]
    return formatted_num


def filter_by_close_month_year(data, month, year):
    """
    Filters the list of dictionaries by the 'closeAt' value based on the provided month and year

    :param data: List of dictionaries containing the data
    :param month: Month to filter by (1-12)
    :param year: Year to filter by (e.g. 2024)
    :return: Filtered list of dictionaries
    """

    filtered_data = []

    for record in data:
        # Parsing the 'closeAt' value to a datetime object
        close_at_date = datetime.fromisoformat(record['closeAt'].replace("Z", "+00:00"))
        # print(close_at_date , "close_at_date ")
        # print(close_at_date.month, "MONTH")
        # print(close_at_date.year, "YEAR")
        # Checking if the month and year match
        if close_at_date.month == month and close_at_date.year == year:
            filtered_data.append(record)

    return filtered_data

