#!/usr/bin/env python3.9
import os, time, datetime, subprocess, sys, statistics
from zoneinfo import ZoneInfo

# ---------- CONFIG ----------
TOPIC = "my-home-temp-<SOME-PRIVATE-RAND-HASH-LIKE-UUID-OR-MD5>"
NTFY_URL = "https://ntfy.sh/" + TOPIC
LOG_FILE = "/home/pi/temps.log"
SUMMARY_STAMP = LOG_FILE + ".last_summary"
ALERT_STAMP = LOG_FILE + ".last_alert"
THRESHOLD_F = 50.0  # alert if below this
ALERT_COOLDOWN_MIN = 60  # minutes between low-temp alerts
USB_CMD = ["/usr/bin/usb_temp"]  # <-- set to your usb_temp path
CURL = "/usr/bin/curl"  # path to curl
LOCAL_TZ = ZoneInfo("America/Chicago")  # US CST
# ----------------------------


def post_ntfy(title, body, priority=3):
    # Uses curl to avoid Python SSL issues
    try:
        subprocess.run(
            [
                CURL,
                "-fsS",
                "-H",
                "Title: {}".format(title),
                "-H",
                "Priority: {}".format(priority),
                "-d",
                body,
                NTFY_URL,
            ],
            check=True,
            timeout=12,
        )
    except Exception as e:
        print("[ntfy error] {}".format(e), file=sys.stderr)


def read_celsius():
    out = subprocess.check_output(USB_CMD, text=True, timeout=10).strip()
    return float(out)


def c2f(c):
    return c * 1.8 + 32.0


def now_iso():
    # keep ISO in the log so parsing still works
    return datetime.datetime.now(LOCAL_TZ).isoformat(timespec="seconds")


def now_pretty():
    # human-friendly, with CST/CDT
    return datetime.datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %-I:%M %p %Z")


def append_log(ts, ftemp):
    with open(LOG_FILE, "a") as fh:
        fh.write("{}\t{:.2f}\n".format(ts, ftemp))


def touch(path):
    open(path, "a").close()
    os.utime(path, None)


def minutes_since(path):
    if not os.path.exists(path):
        return 1e9
    return (time.time() - os.path.getmtime(path)) / 60.0


def maybe_alert(ftemp):
    if ftemp < THRESHOLD_F and minutes_since(ALERT_STAMP) >= ALERT_COOLDOWN_MIN:
        post_ntfy(
            "LOW TEMP ALERT: {:.1f}°F".format(ftemp),
            "{}  Below {:.1f}°F.\nCurrent: {:.1f}°F".format(
                now_pretty(), THRESHOLD_F, ftemp
            ),
            priority=5,
        )
        touch(ALERT_STAMP)


def daily_summary_if_due():
    # run summary if 24h elapsed since SUMMARY_STAMP
    if minutes_since(SUMMARY_STAMP) < 23 * 60:
        return
    cutoff = time.time() - 24 * 3600
    rows = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                ts_s, f_s = line.split("\t")
                try:
                    ts = datetime.datetime.fromisoformat(ts_s).timestamp()
                except ValueError:
                    continue
                if ts >= cutoff:
                    rows.append((ts_s, float(f_s)))
    if not rows:
        post_ntfy("Daily Temp Summary", "No data in the last 24 hours.")
        touch(SUMMARY_STAMP)
        return

    temps = [v for _, v in rows]
    mean_v, min_v, max_v = statistics.mean(temps), min(temps), max(temps)
    tail = "\n".join(
        "{}  {:.1f}°F".format(
            datetime.datetime.fromisoformat(ts)
            .astimezone(LOCAL_TZ)
            .strftime("%Y-%m-%d %-I:%M %p %Z"),
            v,
        )
        for ts, v in sorted(rows, reverse=True)
    )
    body = (
        "mean/min/max (last 24h): {:.1f} / {:.1f} / {:.1f} °F\n" "Entries: {}\n\n{}"
    ).format(mean_v, min_v, max_v, len(rows), tail)
    post_ntfy("Daily Temp Summary", body, priority=4)
    touch(SUMMARY_STAMP)
    print("[summary] sent")


def collect_once():
    try:
        f = c2f(read_celsius())
        ts = now_iso()
        append_log(ts, f)
        maybe_alert(f)
        daily_summary_if_due()
        print("[collect] {}  {:.1f}°F".format(ts, f))
    except Exception as e:
        print("[collect error] {}".format(e), file=sys.stderr)


def read_ftemp_with_retries(timeout_s=90, interval_s=5):
    """Try to get °F reading, retrying for up to timeout_s seconds."""
    deadline = time.time() + timeout_s
    last_err = None
    while time.time() < deadline:
        try:
            return round(c2f(read_celsius()), 1), None
        except Exception as e:
            last_err = e
            time.sleep(interval_s)
    return None, last_err


def boot():
    # start 24h summary timer from boot
    touch(SUMMARY_STAMP)

    f, err = read_ftemp_with_retries(timeout_s=90, interval_s=5)
    if f is not None:
        post_ntfy(
            "Pi boot OK", "{}  Temp is {:.1f}°F".format(now_pretty(), f), priority=4
        )
        # log it and check alerts right away
        append_log(now_iso(), f)
        maybe_alert(f)
    else:
        post_ntfy(
            "Pi boot OK (sensor not ready)",
            "{}  Could not read sensor after 90s.\nError: {}".format(now_iso(), err),
            priority=4,
        )
    # hourly cron will keep going and summary will fire 24h after this touch()


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "collect"
    if mode == "collect":
        collect_once()
    elif mode == "report":
        f, err = read_ftemp_with_retries()
        if f is not None:
            post_ntfy("Instant Report", f"{now_pretty()}\nCurrent Temp: {f:.1f}°F", priority=3)
        else:
            post_ntfy("Instant Report Failed", f"Could not read sensor.\n{err}", priority=4)
    elif mode == "boot":
        boot()
    elif mode == "test":
        post_ntfy("Pi test", "This is a test from the Pi.", priority=5)
    else:
        print("Usage: script.py [collect|boot|test|report]")



