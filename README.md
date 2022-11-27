# Console echo

## Description

This repository contains two separate console applications:
- ConsoleServer
- ConsoleClient
	
ConsoleServer is implemented in Python and will accept user input from keyboard and print it onto terminal as well as it will echo the input to client ConsoleClient application. 
ConsoleClient is implemented in C# and will receive user input from server application and will print it onto terminal in real time. 

## Installation

Clone the repository to your local machine. Navigate into repository directory on local machine and execute docker-compose to create images

```
git clone https://github.com/rongardF/console_echo.git
cd console_echo
docker-compose build --no-cache
```

## Usage

To use the applications, open up two terminal windows and in the first one run

```
docker run --ip 172.17.0.2 -it --rm console_echo-server
```

And then in the second one run 

```
docker run --ip 172.17.0.3 -it --rm console_echo-client
```

User can then provide input into terminal running the *console_echo-server* application and it will be echod to *console_echo-client* in real-time. User can enter text, delete text, 
start a new line and move around in the text.

To quit the application the user must press **ESCAPE** button in the *console_echo-server* application.

