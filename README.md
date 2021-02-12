# Silent messaging
Chat server & client for messaging.<br>
The service uses 2 factor authentication, login & Diffie Hellman.<br>
The server & each client gets each run an asymmetrical encryption only sharing its public key.<br>
<img src="linuxTest.png" width="350" title="Ubuntu" alt="Linux client test"><br>
Messages sent from unknown contact will not be shown on client screen & straight deleted from the memory.<br>
Service keeps metadata only about attempts of failed login so it can be checked out as an attack on the service.<br>
The messages are not saved anywhere & encrypted per each client so the server itself can't read them,<br>
<img src="windowsTest.png" width="350" title="Ubuntu" alt="Linux client test"><br>
this method used against man in the middle attack.<br>
Using also regex against sql injection.<br>
You get 3 types of users so it can be managed better.<br>
The service can run WAN & LAN alike.<br>
Server can be also blocked from itself & client can block itself from running when some actions accured.<br>
The server always checks up user connection so if the user brut existed the service without disconnecting it will disconnect him.<br>
Uses UTF-8 so on supported environments you can type on any language & use emojis.<br>