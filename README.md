# UDPControlHub

Simple app that creates HTTP and socket servers in separated threads. 
Basically, somewhat emulates interraction with hardware devices via UDP by using web-based interface.

- HTTP: handles basic routes, static files. In 'messages.html' (Send Message tab) you can type your username and message, send it.
- Sockets: awaits for POST-request from the 'Send message' form, saves recieved data to Storage/data.json (messages will not be displayed in the browser).

**Usage:**
1) Run it in Docker container: docker run -itd -p 3000:3000 -v D:\Storage:/app/Storage  amarakheo/simple-web-app
2) Then access the app in the browser: http://localhost:3000/
