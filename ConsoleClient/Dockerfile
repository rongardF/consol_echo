# syntax=docker/dockerfile:1
# base image
FROM python:3.10-slim-buster
WORKDIR /app
COPY /app/. /app	
# dependencies
RUN apt update
RUN apt -y install libncurses5
RUN apt -y install wget
RUN wget https://packages.microsoft.com/config/ubuntu/20.04/packages-microsoft-prod.deb 
RUN dpkg -i packages-microsoft-prod.deb
RUN apt update 
RUN apt -y install apt-transport-https
RUN apt -y install aspnetcore-runtime-6.0
EXPOSE 5000
CMD [ "dotnet", "ConsoleClient.dll" ]