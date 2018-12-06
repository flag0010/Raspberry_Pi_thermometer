# Raspberry_Pi_thermometer


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
