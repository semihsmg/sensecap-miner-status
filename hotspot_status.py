import yagmail
import time
import requests

# register your gmail with Application-Specific Password (https://support.google.com/accounts/answer/185833)
# https://github.com/kootenpv/yagmail#username-and-password
yag = yagmail.SMTP('mygmailusername@gmail.com')
to = 'x@y.com'

subject = 'Hotspot Needs Attention!'
body = ''

seconds = 1800.0  # 30 mins
start_time = time.time()
reset_report_counter = 0
names = ''

# get your API Key from Sensecap Dashboard under Account tab (https://status.sensecapmx.cloud/#/user/account)
url = 'https://status.sensecapmx.cloud/api/openapi/device/view_device?api_key=REPLACE_HERE'
explorer_url = 'https://explorer.helium.com/hotspots/'
dashboard_url = 'https://status.sensecapmx.cloud/#/hotspot/detail?sn='

# enter your hotspot serial numbers
serial_numbers = ['SERIAL_NUMBER_1', 'SERIAL_NUMBER_2']

response_json = ''

report_list = {}


def time_stamp():
    print(time.strftime('%d/%m/%Y - %H:%M:%S (UTC%z')[:-2] + ')')


def reset_dict(dict):
    for i, x in enumerate(serial_numbers):
        dict[i] = 0


reset_dict(report_list)

while True:
    for index, sn in enumerate(serial_numbers):
        response = requests.get(url + '&sn=' + sn)
        response_json = response.json()  # get hotspot informations

        # strip json and only get necessary info for quick review email
        name = response_json["data"]["name"]
        address = response_json["data"]["address"]
        synced_value = response_json["data"]["synced"]
        online_value = response_json["data"]["online"]
        relayed_value = True if response_json["data"]["relayed"] == 1 else False

        if synced_value == False or online_value == False or relayed_value == True:  # enter if the hotspot got issue
            # can be disabled if you want to run it in the background
            # print info of out of synced, offline or relayed hotspot(s)
            time_stamp()
            print(name)
            print("synced: " + str(synced_value))
            print("online: " + str(online_value))
            print("relayed: " + str(relayed_value))
            print(explorer_url + address)
            print(dashboard_url + sn)
            print('------------------------------')
            # end info

            if report_list[index] == 0:  # change mail body to this hotspot's informations
                body += \
                    '<a href=' + explorer_url + address + '>' + name + '</a>' + '\n' + \
                    "synced: " + str(synced_value) + '\n' + \
                    "online: " + str(online_value) + '\n' + \
                    "relayed: " + str(relayed_value) + '\n' + \
                    '<a href=' + dashboard_url + sn + '>Dashboard</a>' + '\n\n'

            report_list[index] += 1  # increase issue counter of hotspot

            if report_list[index] == 4:  # within 2 hours if hotspot still not online then add that hotspot name to a list and send reminder email
                names += name + ','

    if len(body) > 0:
        yag.send(to=to, subject=subject, contents=body)
        body = ''

    reset_report_counter += 1
    if reset_report_counter == 8:  # after 4 hours reset report_list to send email of all hotspots that needs attention
        reset_report_counter = 0
        reset_dict(report_list)

    if len(names) > 0:  # if names list contains any name send reminder email
        subject2 = names + ' still down!'
        yag.send(to=to, subject=subject2, contents='')
        names = ''

    time.sleep(seconds - ((time.time() - start_time) % seconds))
