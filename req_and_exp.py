from typing import List
import streamlit as st
import requests
import asyncio
import httpx
import time
from concurrent.futures import ThreadPoolExecutor


def access_one_city_temp(city_name, api_key):
    lat, lon = get_lat_long_sync(city_name, api_key)
    temp = get_weather_data_sync(lat, lon, api_key)
    return temp


async def get_lat_long_async(city_name, api_key, client):
    base_url = f"http://api.openweathermap.org/geo/1.0/direct"
    params = {
        'q': city_name,
        'appid': api_key,
    }
    response = await client.get(base_url, params=params)
    if response.status_code == 200:
        response = response.json()[0]
        return response['lat'], response['lon']
    else:
        return {"error": response.status_code}

async def get_weather_data_async(lat, lon, api_key, client):
    base_url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,  # широта
        'lon': lon,  # долгота
        'appid': api_key,
        'units': 'metric',
    }
    response = await client.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()['main']['temp']
    else:
        return {"error": response.status_code}

def get_lat_long_sync(city_name, api_key):
    base_url = f"http://api.openweathermap.org/geo/1.0/direct"
    params = {
        'q': city_name,
        'appid': api_key,
    }
    response = requests.get(base_url, params=params)
    print(response.status_code)
    if response.status_code == 200:
        response = response.json()[0]
        return response['lat'], response['lon']
    else:
        return {"error": response.status_code}


def get_weather_data_sync(lat, lon, api_key):
    base_url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,  # широта
        'lon': lon,  # долгота
        'appid': api_key,
        'units': 'metric',
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()['main']['temp']
    else:
        return {"error": response.status_code}


def big_sync_fun(city_name, api_key):
    base_url = f"http://api.openweathermap.org/geo/1.0/direct"
    params = {
        'q': city_name,
        'appid': api_key,
    }
    response = requests.get(base_url, params=params)
    print(response.status_code)
    if response.status_code == 200:
        response = response.json()[0]

    lat, lon = response['lat'], response['lon']

    base_url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': lat,  # широта
        'lon': lon,  # долгота
        'appid': api_key,
        'units': 'metric',
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()['main']['temp']
    else:
        return {"error": response.status_code}

def thread_part(API_key: str, cities: List, n_threads=4):
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=n_threads) as executor:
        temps = list(executor.map(lambda args: big_sync_fun(*args),
                                  [(city, API_key) for city in cities]))

    elapsed_time = time.time() - start_time
    return temps, elapsed_time

def sync_part(API_key: str, pos_cities_options: List):
    results = []
    start_time = time.time()
    for city in pos_cities_options:
        lat, lon = get_lat_long_sync(city, API_key)
        curr_temp = get_weather_data_sync(lat, lon, API_key)
        results.append(curr_temp)
    elapsed_time = time.time() - start_time
    return results, elapsed_time


async def async_part(API_key: str, cities: List):
    start_time = time.time()
    async with httpx.AsyncClient() as client:
        tasks01 = [get_lat_long_async(city, API_key, client) for city in cities]
        places = await asyncio.gather(*tasks01)
        tasks02 = [get_weather_data_async(lat, lon, API_key, client) for lat, lon in places]
        temps = await asyncio.gather(*tasks02)
    elapsed_time = time.time() - start_time
    return temps, elapsed_time


def make_experiments(API_key: str, exp_options: List, pos_cities_options: List):

    st.markdown("## API Calls Speed Analysis")

    st.markdown("Текущие замеры:")

    if 'Sync' in exp_options:
        st.markdown("#### :blue-background[Synchronous Сalls]")
        sequential_results, sequential_time = sync_part(API_key, pos_cities_options)
        st.write(f"Time taken: {sequential_time:.2f} seconds")
        st.write(f"Maked total sync requests: {len(pos_cities_options) * 2}")

    if 'Async' in exp_options:
        st.markdown("#### :blue-background[Asynchronous Сalls]")
        async_results, async_time = asyncio.run(async_part(API_key, pos_cities_options))
        st.write(f"Time taken: {async_time:.2f} seconds")
        st.write(f"Maked total asyncrequests: {len(pos_cities_options) * 2}")

    if 'Multithread' in exp_options:
        st.markdown("#### :blue-background[Multithread Сalls]")
        threaded_results, threaded_time = thread_part(API_key, pos_cities_options)
        st.write(f"Time taken: {threaded_time:.2f} seconds")
        st.write(f"Maked total multithread requests: {len(pos_cities_options) * 2}")

    st.markdown("")
    st.markdown("#### :blue-background[Замеры полученные однажды]:")
    st.markdown("Maked total requests: 30 * 3 = 90")
    st.markdown("Synchronous: 3.99 seconds")
    st.markdown("Asynchronous: 0.38 seconds")
    st.markdown("Multithread: 1.18 seconds")
    st.markdown("")
    st.markdown("Самыми быстрыми в этот раз оказались асинхронные запросы, что логично, ибо у нас тут запросы с возможностью задержки. Хотя может стоило поэксперементировать с кол-вом потоков.")