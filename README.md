# E-Series-Automation
Tools and Scripts related to NetApp E-Series Storage Arrays

### Modify following lines in e_alertV2.py

Replace ‘@mySANtricityProxy.mydomain.com’ with your domain name

    mailfrom = “e-series.monitor@mySANtricityProxy.mydomain.com”

List of one or more email recipients, replace/add per your needs

    mailto = ["IT.manager@mydomain.com", "IT.Operationse@mydomain.com"]

Replace ‘mail.mydomain.com’ with your mail server

    server = smtplib.SMTP('mail.mydomain.com')

Set your WebProxy:PORT# here

    server_root_url = ''
e.g. server_root_url = 'https://mySANtricityProxy.mydomain.com:8443'

Ensure ro account has been enabled. 
Script uses ro/ro account. If you are using a different account, please change auth = entry

    auth = ('ro', 'ro')

If you need to suppress alerts for one or more arrays, add an entry in the "suppress:" section of config.yml for each host (by Name)

Confirm the script is executable and schedule the script via cron.

    e.g. To run the script at 7 am daily
    0 7 * * * /usr/local/bin/python3.5 /path/to/script/e_alertV2.py >>/tmp/e_alert.log 2>&1
