import logging
import sqlite3
from collections import namedtuple
from contextlib import closing

import arrow
import cfg
from date_range import DateRange
from datetime_util import hms
from harness import logger

_conn = None


DateEdit = namedtuple("DateEdit", ["ymd", "minutes", "reason"])
DateLog = namedtuple("DateLog", ["dt", "state", "reason"])


def init_schema(conn=None):
    logger.debug("initialising database")
    if not conn:
        conn = _connection()
    conn.execute('PRAGMA encoding = "UTF-8"')
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS active (
            start_time INTEGER NOT NULL,
            end_time INTEGER NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS edits (
            dt INTEGER NOT NULL,
            minutes INTEGER NOT NULL,
            reason TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS log (
            dt INTEGER NOT NULL,
            state TEXT NOT NULL,
            reason TEXT NOT NULL
        )
        """
    )


def _connection():
    global _conn
    if not _conn:
        filename = cfg.db_file
        logger.debug("database: %s" % filename)
        empty_db = not filename.exists()
        _conn = sqlite3.connect(filename)
        _conn.execute("PRAGMA foreign_keys = off")
        _conn.execute("PRAGMA temp_store = MEMORY")
        if logger.level == logging.DEBUG:
            _conn.set_trace_callback(lambda sql: logger.debug("SQL> %s" % sql))
        if empty_db:
            init_schema(_conn)

    return _conn


def current_range():
    conn = _connection()

    dt = arrow.now(tz=cfg.time_zone)
    dt = dt.floor("minute").to("UTC")

    # look for an existing range (fuzz to a few minutes)
    with closing(conn.cursor()) as cursor:
        cursor.execute(
            "SELECT start_time,end_time FROM active WHERE end_time BETWEEN ? AND ?",
            (dt.shift(minutes=-2).timestamp, dt.shift(minutes=1).timestamp),
        )
        row = cursor.fetchone()

    if row:
        return DateRange(
            arrow.get(row[0]).to(cfg.time_zone), arrow.get(row[1]).to(cfg.time_zone)
        )
    else:
        return None


def remove_empty_ranges():
    # setting back then away within the same minute will create a zero-minute
    # range.  these are safe to delete.

    conn = _connection()
    conn.execute("DELETE FROM active WHERE start_time = end_time")
    conn.commit()


def log_active():
    conn = _connection()

    dt = arrow.now(tz=cfg.time_zone)
    dt = dt.floor("minute").to("UTC")

    # look for an existing range (fuzz to a few minutes)
    with closing(conn.cursor()) as cursor:
        cursor.execute(
            "SELECT start_time,end_time FROM active WHERE end_time BETWEEN ? AND ?",
            (dt.shift(minutes=-2).timestamp, dt.shift(minutes=1).timestamp),
        )
        existing = cursor.fetchone()

    if existing:
        # update existing
        if logger.level == logging.DEBUG:
            start_dt = arrow.get(existing[0])
            end_dt = arrow.get(existing[1])
            logger.debug(
                "existing range: %s - %s (%s - %s)"
                % (start_dt, end_dt, start_dt.timestamp, end_dt.timestamp)
            )
        if dt.timestamp != existing[1]:
            conn.execute(
                "UPDATE active SET end_time=? WHERE start_time=?",
                (dt.timestamp, existing[0]),
            )
            conn.commit()

    else:
        # insert new range
        logger.debug("creating new range: %s (%s)" % (dt, dt.timestamp))
        conn.execute(
            "INSERT INTO active(start_time, end_time) VALUES (?, ?)",
            (dt.timestamp, dt.timestamp),
        )
        conn.commit()


def active_ranges(start_dt, end_dt):
    conn = _connection()

    start_time = start_dt.to("UTC").timestamp
    end_time = end_dt.to("UTC").timestamp
    logger.debug("%s (%s) - %s (%s)" % (start_dt, start_time, end_dt, end_time))

    where = "(%s)" % ") OR (".join(
        [
            " AND ".join(
                [
                    "(%s BETWEEN start_time AND end_time)" % start_time,
                    "(%s BETWEEN start_time AND end_time)" % end_time,
                ]
            ),
            " AND ".join(
                [
                    "(%s BETWEEN start_time AND end_time)" % start_time,
                    "(%s > end_time)" % end_time,
                ]
            ),
            " AND ".join(
                [
                    "(%s < start_time)" % start_time,
                    "(%s BETWEEN start_time AND end_time)" % end_time,
                ]
            ),
            " AND ".join(
                ["(start_time > %s)" % start_time, "(end_time < %s)" % end_time]
            ),
        ]
    )

    with closing(conn.cursor()) as cursor:
        cursor.arraysize = 10
        cursor.execute(
            "SELECT start_time, end_time FROM active WHERE %s ORDER BY start_time"
            % where
        )

        result = []
        while True:
            rows = cursor.fetchmany()
            if not rows:
                break

            for row in rows:
                row_start_dt = arrow.get(row[0]).to(cfg.time_zone)
                row_end_dt = arrow.get(row[1]).to(cfg.time_zone)
                logger.debug(
                    "%s - %s (%s)"
                    % (
                        row_start_dt.format("YYYY-MM-DD HH:mm"),
                        row_end_dt.format("YYYY-MM-DD HH:mm"),
                        hms((row_end_dt - row_start_dt).total_seconds()),
                    )
                )

                # truncate if the range extends beyond requested start or end
                if row_start_dt < start_dt:
                    logger.debug(
                        "truncating start %s to %s"
                        % (
                            row_start_dt.format("YYYY-MM-DD HH:mm"),
                            start_dt.format("YYYY-MM-DD HH:mm"),
                        )
                    )
                    row_start_dt = start_dt.clone()
                if row_end_dt > end_dt:
                    logger.debug(
                        "trimming end %s to %s"
                        % (
                            row_end_dt.format("YYYY-MM-DD HH:mm"),
                            end_dt.format("YYYY-MM-DD HH:mm"),
                        )
                    )
                    row_end_dt = end_dt.clone()

                result.append(DateRange(row_start_dt, row_end_dt))

    # split ranges which span midnight
    for dtr in result:
        while dtr.start_ymd != dtr.end_ymd:
            new_end = dtr.start_dt.clone().ceil("day")
            new_start = new_end.clone().shift(minutes=1)
            old_end = dtr.end_dt
            dtr.end_dt = new_end
            result.append(DateRange(new_start, old_end))

    result.sort()
    return result


def log_edit(dt, minutes, reason):
    assert dt.datetime.tzname() == cfg.time_zone_name
    ymd = dt.format("YYYYMMDD")

    conn = _connection()

    conn.execute(
        "INSERT INTO edits(dt, minutes, reason) VALUES (?, ?, ?)",
        (ymd, round(minutes), reason),
    )
    conn.commit()


def edits(dt):
    assert dt.datetime.tzname() == cfg.time_zone_name
    ymd = dt.format("YYYYMMDD")

    conn = _connection()

    with closing(conn.cursor()) as cursor:
        cursor.arraysize = 5
        cursor.execute(
            "SELECT minutes, reason FROM edits WHERE dt = %s ORDER BY ROWID" % ymd
        )

        result = []
        while True:
            rows = cursor.fetchmany()
            if not rows:
                break

            for row in rows:
                result.append(DateEdit(ymd, row[0], row[1]))
                logger.debug(result[-1])

    return result


def log_state_change(state, reason):
    timestamp = arrow.now(tz=cfg.time_zone).to("UTC").timestamp

    conn = _connection()

    conn.execute(
        "INSERT INTO log(dt, state, reason) VALUES (?, ?, ?)",
        (timestamp, state, reason),
    )
    conn.execute(
        "DELETE FROM log WHERE dt < ?",
        (arrow.now(tz=cfg.time_zone).shift(weeks=-4).to("UTC").timestamp,),
    )
    conn.commit()


def logs(dt):
    assert dt.datetime.tzname() == cfg.time_zone_name
    start_timestamp = dt.floor("day").to("UTC").timestamp
    end_timestamp = dt.ceil("day").to("UTC").timestamp

    conn = _connection()

    with closing(conn.cursor()) as cursor:
        cursor.arraysize = 5
        cursor.execute(
            "SELECT dt, state, reason FROM log WHERE dt BETWEEN %s AND %s ORDER BY dt"
            % (start_timestamp, end_timestamp)
        )

        result = []
        while True:
            rows = cursor.fetchmany()
            if not rows:
                break

            for row in rows:
                result.append(
                    DateLog(arrow.get(row[0]).to(cfg.time_zone), row[1], row[2])
                )
                logger.debug(result[-1])

    return result
