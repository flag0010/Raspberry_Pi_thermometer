# Raspberry_Pi_thermometer
Set up a raspberry pi 3b to monitor my house temp when i'm away. I've used a usb thermometer device called a TEMPer. It requires some USB hacking. 

## Steps

you need to install a temper USB monitor. i found a cmd named hid-query that does it. just a simple c program. idk where i got it, but it's something like this: https://github.com/burncycl/temperx-python3-influxdb

possibly the binary `hid-query` in this repo will work. i think it also needs hidapi (https://github.com/signal11/hidapi)

anyway, the bash command `usb_temp` runs hid-query and ask the thermometer for temp in some hex blob and returns it in deg. C, a la:

```
./usb_temp
23.06
```

that's the basics. 

here are two python3 scripts (require python3.9 or newer). 

`ntfy.USB.therm.temp.mon.py`

`ntfy.control.listener.py`

for both you need to edit the `TOPIC` var in the script to set a ntfy.sh topic, something like `my-home-temp-d15a0114-852a-476d-85df-7fd5fe21e322` so it's semi private as anyone with the url can find it

The first script above runs indefinitely and pulls and logs the temp every 1hr and reports to ntfy.sh every 24 hrs. It also issues a warning if the temp drops below 50 deg. F (you can adjust this). That warning will come every hour until the temp increases above 50 deg. F. on boot-up it also gives a status ping to the channel with the current temp, to let you know it's alive and well without waiting 24 hrs.

the second script is a listener. it must share the same topic as the first, and it listens to the topic and if it gets the message `temp now` it responds with the current temp. useful if you want a quick temp update.

both of these commands are orchestrated in the `crontab.txt` file so you can see how they work. they draw very little power and seem to be stable for days/weeks

finally, got to your ntfy.sh topics on the web (eg: https://ntfy.sh/my-home-temp-d15a0114-852a-476d-85df-7fd5fe21e322), and subscribe and/or subscribe using the phone app. this is how you get notifications

 
### lights
i also attached the lights_off shell script, it turns off the pi's little blinky leds, save a little power. it's also called in the crontab.txt

