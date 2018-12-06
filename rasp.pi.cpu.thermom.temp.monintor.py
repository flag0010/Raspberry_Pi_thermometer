import time, smtplib, os, sys
from email.mime.text import MIMEText

user_email, password = sys.argv[1], sys.argv[2]

def get_CPU_temp_load():
    '''returns [CPU temp, CPU load 1 min, CPU load 5 min, CPU load 15 min]'''
    a = os.popen('vcgencmd measure_temp')
    f = a.next().strip().split('=')[-1].replace("'C", '')
    cpu_temp = float(f)
    a = os.popen('uptime')
    f = [i.replace(',','') for i in a.next().split()[-3:]]
    loads = map(float, f)
    loads.insert(0, cpu_temp)
    return loads

def CtoF(C):
    '''because I think in Fahrenheit'''
    return C*1.8+32

def send_email(subj, body, user_email):
    '''send email using smtplib and your gmail acct,
    assumes you entered your gmail username and password as cmd line args'''
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(user_email, password)
    msg = MIMEText(body)
    msg['Subject'] = subj 
    server.sendmail(user_email, user_email, msg.as_string())
    server.close()

lm = [-18.243, 0.902, -4.173, -6.925, -2.423]
predLM = lambda i: lm[0]+lm[1]*i[1-1]+lm[2]*i[2-1]+lm[3]*i[3-1]+lm[4]*i[4-1]

idx, ct = 0, 0
temps = []
while 1:
    C =  predLM(get_CPU_temp_load())
    F = str(round(CtoF(C),1))
    temps.insert(0, time.asctime() +' temp=' + F +'F')
    #
    if C <= 10: #getting too cold! Notify every hr it stays too cold
        send_email('Warning! '+F+'F', '\n'.join(temps), user_email)
    else: #warm enough, send updates every 24 hrs
        ct+=1
        if ct > 23:
            body = '\n'.join(temps)
            subj = '24 hr temp update'
            send_email(subj, body, user_email) #email yourself
            ct = 0
    print idx, 'temperature estimate = ', F, 'F'
    time.sleep(60*60) #snooze 1hr
    idx+=1

    

