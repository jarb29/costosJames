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
        total_tiempo_corte = sum(item['tiempo_corte'] for item in items)

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

