# heater
heater-control

Very simple control of a shelly relay depending on tibber price every hour
e.g. controlling a water heater

Getting started:
Update token and shelly-IP and run


Hardware used :
Rasbery PI 4
Shelly 1PM or similiar.
Temperature Sensor Add-on is suggested to measure water in tube, and to continue the project.


Note:
When wiring the heater get help by electrician, it's high voltage; AC 240/400 Volt. 
I have just used it to control heater with one phase coupling e.g. phase & neutral(240V)
and control the phase with Shelly1PM.
Not sure if the relay is capable of handling 400V, spec only says 16A.


Help with configuring Rasberry PI:
https://raspberrypi.stackexchange.com/questions/1318/boot-without-starting-x-server
https://learn.pi-supply.com/make/how-to-save-power-on-your-raspberry-pi/
