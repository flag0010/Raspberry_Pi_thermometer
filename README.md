# Raspberry_Pi_thermometer
Hacking a Raspberry Pi 3B to estimate and send notifications about house temp

When I leave my home empty in the winter I always worry my furnace will die, causing my house to freeze (broken pipes/water damage). Commercial wifi based temperature notification systems are available (e.g. Nest), but all I've seen cost >$50. I wondered if I could do a decent job of estimating ambient temperature using the CPU thermometer built into my raspberry pi and a little stats.  So I trained a linear model, that used CPU temp (from `vcgencmd measure_temp` command) and CPU load (from `uptime` command), to estimate the real ambient temp (which I got from a USB thermometer).  The idea is that CPU temp is probably a combination of ambient temp + CPU load, and we can make some training data and use stats to separate out ambient temp from this equation.  It works pretty well.  Here's the model:

Ambient temp (in C) = -18.243 + CPU_temp * 0.902 + load_1m * -4.173 + load_5m * -6.925 + load_15m * -2.423 

Where # in load_#m, indicates the appropriate ave. load over the last # min from `uptime`. In my testing this method is within about 2 C 95% of the time.

Then I put this function into a python 2.7 script called `rasp.pi.cpu.thermom.temp.monintor.py`, which uses it to guess the temp every hr, email you a 24 hr report, and email you a warning every hr if the temp is below 10 C (50 F). The email set up is explained below.

You run it as follows:

`python rasp.pi.cpu.thermom.temp.monintor.py xxxusernamexxx@gmail.com xxxmypasswordxxx`

Where you need to enter your gmail address and password (see below for password detail, it's not the same one you use to check your gmail)

Basically, if you have a Raspberry Pi 3B (and they're only $35), you can use it to do a monitor your house temp while you are away and send you warnings if it gets really cold. 

EMAIL SETUP
You need a gmail account to send the emails through, and you'll have to configure gmail to allow your Pi to send email via SMTP. You can do this at https://myaccount.google.com/. From the homescreen under Sign-in & Security you should see a linked called Signing in to Google. And after clicking on that link click on App passwords. It will probably ask you to enter your gmail password next. Then you need to create a new app. Under the Select the app and device you want to generate the app password for. heading, select Other (custom name) in the select app box. Give it some name (I used "python"). And click Generate. This should then give you a 16 character password that will allow our temp sensor to send emails. Copy this password and save it (but keep it secret).

Note: I don't know the security implications of this. You are creating an alternate password that can be used to access at least parts (and maybe all) of your gmail. Google generates this password, and it seems pretty strong (16 random characters). However, if you are uncomfortable with this, quit now and delete this access (there should be a trash can icon next to the newly allowed "python" app). Alternatively, create a dummy gmail account that you'll use only for this purpose.


CAVEATS

1) You are going to need to leave you Pi running the whole time you are gone, and it needs to not sleep, run out of power, or crash. 

2) You'll need stable internet at your house. In my case I used wifi, so if the connection is lost there will be no temp. notification. 

3) To be notified, you'll obviously need to receive emails wherever you travel (so this isn't going to work if you go off the grid), and you'll need to check your emails semi-regularily (I'd imagine you have a day or so before your pipes freeze when it's sub-zero outside). 

4) You'll also need a plan in place if your furnace does die. Like call the neighbors, or furnace repair company, and have some way for them to enter the house. 

5) My Pi, is a Pi 3B, with a case and a heat sink, so it may dissipate heat in an unusual way. If yours is different, you should test it out next to a thermometer and see if it's close enough for you.

7) I tested this method in Minnesota in December. It's cold. I literally have no access to warmth. I have no idea if this hack works to protect against overheating (my concern was only freezing). So YMMV if you are worried about monitoring for high temps.

6) There is no warranty implied. This is a hack, it may work for you, or it may not and in that case I am in no way accountable. See the software license.
