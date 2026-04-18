import os
import time
import asyncio
from queue import Queue, Empty
from functools import wraps

import clickhouse_connect
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ClickHouse Explorer",
    description="Explore ClickHouse sample datasets in OpenBB Workspace",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://pro.openbb.co",
        "https://pro.openbb.dev",
        "https://excel.openbb.co",
        "https://excel.openbb.dev",
        "http://localhost:1420",
        "http://localhost:5050",
        "tauri://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

POOL_SIZE = 10
_client_pool = Queue(maxsize=POOL_SIZE)


def _create_client():
    return clickhouse_connect.get_client(
        host=os.environ["CLICKHOUSE_HOST"],
        port=int(os.environ.get("CLICKHOUSE_PORT", "8443")),
        username=os.environ.get("CLICKHOUSE_USER", "default"),
        password=os.environ["CLICKHOUSE_PASSWORD"],
        secure=True,
    )


def _get_client():
    try:
        return _client_pool.get_nowait()
    except Empty:
        return _create_client()


def _return_client(c):
    try:
        _client_pool.put_nowait(c)
    except:
        c.close()

WIDGETS = {}

_cache = {}
CACHE_TTL = 120


def register_widget(widget_config):
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        endpoint = widget_config.get("endpoint")
        if endpoint:
            if "widgetId" not in widget_config:
                widget_config["widgetId"] = endpoint
            WIDGETS[widget_config["widgetId"]] = widget_config

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def _run_query(sql):
    c = _get_client()
    try:
        result = c.query(sql)
        return [dict(zip(result.column_names, row)) for row in result.result_rows]
    finally:
        _return_client(c)


def cached_query(sql, ttl=CACHE_TTL):
    now = time.time()
    if sql in _cache:
        cached_time, cached_data = _cache[sql]
        if now - cached_time < ttl:
            return cached_data
    data = _run_query(sql)
    _cache[sql] = (now, data)
    return data


async def async_cached_query(sql, ttl=CACHE_TTL):
    now = time.time()
    if sql in _cache:
        cached_time, cached_data = _cache[sql]
        if now - cached_time < ttl:
            return cached_data
    data = await asyncio.to_thread(_run_query, sql)
    _cache[sql] = (now, data)
    return data


async def warm_cache():
    """Pre-warm cache with unfiltered queries in the background."""
    queries = [
        # UK Housing
        "SELECT round(avg(price)) AS avg_price, count() AS total_transactions FROM uk.uk_price_paid",
        "SELECT toYear(date) AS year, round(avg(price)) AS avg_price FROM uk.uk_price_paid GROUP BY year ORDER BY year DESC LIMIT 2",
        """SELECT toYear(date) AS year, round(avg(price)) AS avg_price, min(price) AS min_price,
            max(price) AS max_price, count() AS transactions FROM uk.uk_price_paid GROUP BY year ORDER BY year""",
        """SELECT town, round(avg(price)) AS avg_price, count() AS transactions FROM uk.uk_price_paid
            WHERE town != '' GROUP BY town HAVING transactions > 1000 ORDER BY avg_price DESC LIMIT 20""",
        """SELECT toYear(date) AS year, round(avgIf(price, type = 'detached')) AS detached,
            round(avgIf(price, type = 'semi-detached')) AS semi_detached,
            round(avgIf(price, type = 'terraced')) AS terraced,
            round(avgIf(price, type = 'flat')) AS flat,
            round(avgIf(price, type = 'other')) AS other FROM uk.uk_price_paid GROUP BY year ORDER BY year""",
        # NYC Taxi
        "SELECT round(avg(fare_amount), 2) AS avg_fare, round(avg(trip_distance), 2) AS avg_distance, count() AS total_trips FROM nyc_taxi.trips_small WHERE 1=1 ",
        """SELECT toHour(pickup_datetime) AS hour, count() AS trips, round(avg(fare_amount), 2) AS avg_fare,
            round(avg(trip_distance), 2) AS avg_distance, round(avg(passenger_count), 1) AS avg_passengers
            FROM nyc_taxi.trips_small WHERE 1=1  GROUP BY hour ORDER BY hour""",
        """SELECT pickup_ntaname AS pickup_zone, count() AS trips, round(avg(fare_amount), 2) AS avg_fare
            FROM nyc_taxi.trips_small WHERE pickup_ntaname != '' GROUP BY pickup_zone ORDER BY trips DESC LIMIT 20""",
        "SELECT pickup_ntaname AS zone FROM nyc_taxi.trips_small WHERE pickup_ntaname != '' GROUP BY zone ORDER BY zone",
    ]
    for sql in queries:
        try:
            await async_cached_query(sql, ttl=CACHE_TTL)
        except Exception:
            pass
