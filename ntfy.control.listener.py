import subprocess
import json
import sys
import time
import os

# ---------- CONFIG ----------
# Your Real Topic
TOPIC = "my-home-temp-<SOME-PRIVATE-RAND-HASH-LIKE-UUID-OR-MD5>"
NTFY_URL = "https://ntfy.sh/" + TOPIC + "/json"

# The command you type on your phone to trigger the update
TRIGGER_PHRASE = "temp now"

# Path to your existing temperature monitor script
TARGET_SCRIPT = "/home/pi/Desktop/temp_monitor/ntfy.USB.therm.temp.mon.py"
# ----------------------------


def listen_loop():
    print(f"Listening on {TOPIC} for '{TRIGGER_PHRASE}'...")

    # Start curl in streaming mode (-N)
    cmd = ["/usr/bin/curl", "-s", "-N", NTFY_URL]

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )

    try:
        for line in process.stdout:
            if not line.strip():
                continue

            try:
                data = json.loads(line)

                # Check for message events
                if data.get("event") == "message":
                    incoming_msg = data.get("message", "").strip()

                    # Case-insensitive check (so 'Temp Now' or 'temp now' both work)
                    if incoming_msg.lower() == TRIGGER_PHRASE.lower():
                        print(f"Received trigger! Running report...")

                        # Call the monitor script with the 'report' argument
                        subprocess.run([sys.executable, TARGET_SCRIPT, "report"])

            except json.JSONDecodeError:
                pass

    except Exception as e:
        print(f"Stream error: {e}")
    finally:
        process.kill()


if __name__ == "__main__":
    # Auto-reconnect loop in case internet drops
    while True:
        try:
            listen_loop()
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Crashed: {e}")

        print("Connection lost. Reconnecting in 10 seconds...")
        time.sleep(10)
