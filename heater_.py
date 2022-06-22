import ShellyPy
import asyncio
import aiohttp
import tibber
from ShellyPy import Shelly
from time import sleep
import time
import random
from datetime import timedelta, datetime

from tibber import Tibber

heater_IP = "191.x.x.x"
# https://developer.tibber.com/docs/guides/calling-api
ACCESS_TOKEN = "YOUR-ACCESS-TOKEN"
heater_state = ""
count = 0
timestamp = 0
tibber_connection = ""

#def _callback(pkg):
#    data = pkg.get("data")
#    if data is None:
#        return
#    print(data.get("liveMeasurement"))

async def main():
    waitsec = None
    global heater_state
    global count
    # heater_state='force_on'

    #async with aiohttp.ClientSession() as session:
    #tibber_connection = tibber.Tibber(ACCESS_TOKEN, websession=session)
    tibber_connection = tibber.Tibber(ACCESS_TOKEN)
    await tibber_connection.update_info()
    home = tibber_connection.get_homes()[0]
        #await home.rt_subscribe(_callback)
        #data = home.rt_subscribe.get(_callback)
        #if data is None:
        #    return
        #print(_callback.get("liveMeasurement"))


    #await tibber_connection.update_info()
    print(tibber_connection.name)
    home = tibber_connection.get_homes()[0]
    await home.update_info()

    while True:
        try:
            tibber_connection
        except NameError:
            # print("Dooh! Tibber connection error")
            tibber_connection: Tibber = tibber.Tibber(ACCESS_TOKEN)
            sleep(0.1)
            await tibber_connection.update_info()
            print(tibber_connection.name)
            home = tibber_connection.get_homes()[0]
            await home.update_info()
            print(home.address1)

        await home.update_price_info()
        level = home.current_price_info.get("level")
        print(home.current_price_info)
        #print(_callback(pkg).get("liveMeasurement"))
        #  await tibber_connection.close_connection()

        count = count + 1
        if count >= 10:
            print("10th time ~10h ago, set relay to be sure and try harder...")
            heater_toggle(heater_state, True)
            # TODO: add if solar panel check with Pulse
            print("DEBUG: timestamp: " + str(timestamp) + "datetime.utcnow(): " + str(datetime.utcnow()))
            count = 0
        if timestamp + timedelta(hours=14) >= datetime.utcnow():
           heater_state = "force_on"  # Try harder,
           # set relay with higher price to be sure if ~ 14h ago heater was on

        if level == 'VERY_CHEAP':
            heater_toggle(True)
        elif level == 'CHEAP':
            if timestamp + timedelta(hours=10) >= datetime.utcnow():  # 10h ago? heater on
                print(level + " - 10h ago? heater on")
                heater_toggle(True)
                waitsec = 4800  # Let Heater be on longer ~1,5h, 10h ago it was on
            elif heater_state == 'force_on':
                print(level + " - force on")
                heater_toggle(True, True)
                waitsec = 4800  # Let Heater be on longer ~1,5h long time ago it was on
            else:
                heater_toggle(False)
        elif level == 'NORMAL':
            if heater_state == 'force_on':
                print(level + " - force on")
                heater_toggle(True, True)
                waitsec = 3600  # Let Heater be on ~1h, long time ago it was on
            else:
                heater_toggle(False)
        elif level == 'EXPENSIVE':
            if heater_state == 'force_on':
                print(level + " - force on")
                heater_toggle(True, True)
            else:
                heater_toggle(False)
        elif level == 'VERY_EXPENSIVE':
            heater_toggle(False, True)
        else:
            print("ERROR: Ooops!! ... price info unknown:" + level)

        if waitsec is None:  # Wait until next ~full hour
            waitsecuntilhour = (60 - int(time.strftime("%M"))) * 60
            # waitsecuntilhour = 5
            print("waitsecuntilhour:" + str(waitsecuntilhour))
            waitsec = waitsecuntilhour  # To next Tibber poll of price level
        rand: int = random.randint(-30, 60)
        if rand + waitsec > 0:  # # Some random for fun
            waitsec = waitsec + rand
        print("Wait %f minutes." % (round(waitsec / 60, 2)))
        print("Current time: %s" % time.strftime("%a %b %d %H:%M:%S"))
        print("Latest relay on time: %s" % (str(timestamp)))
        print("Next evaluation: %s" % (str(datetime.now() + timedelta(seconds=waitsec))))
        sleep(waitsec)
        waitsec = None


def heater_toggle(setrelay, force=False):
    global heater_state
    global timestamp

    if heater_state != setrelay or force is True:
        print("Connect to 'Heater' ShellyPM")
        # Heater Shelly-PM
        try:
            device: Shelly = ShellyPy.Shelly(heater_IP)
            # WILL throw an exception if the device is not reachable, gives a bad response or requires a login
            print("Toggle relay to state: %s" % setrelay)
        except Exception:
            print("ERROR: Shelly device:" + device.print() + "not reachable. IP:" + heater_IP)
        if not heater_state:
            print("Heater relay state unknown.. first run ?")
        if force:
            print("Force Set Relay no matter what, 'I think i'm paranoid'")
        try:
            device.relay(0, turn=setrelay)  # set the relay at index 0
            heater_state = setrelay
        except Exception:
            print("ERROR: Failure setting relay state:" + setrelay)
    else:
        print("Relay already state: %s" % setrelay)
        heater_state = setrelay
    if setrelay:
        timestamp = datetime.utcnow()  # Set timestamp the last time relay was _ON_ (- timedelta(seconds=15))
    force = False  # Reset force flag


def __exit__(self, *args):
    self.tibber_connection.close_connection()
    sleep(1)
    print("Tibber connection closed")


if __name__ == '__main__':
    #asyncio.ensure_future(run())
    loop = asyncio.get_event_loop()
    #loop.run_forever()
    loop.run_until_complete(main())


