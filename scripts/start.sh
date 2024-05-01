#!/bin/bash

pids=$(lsof -t -i :80 -sTCP:LISTEN | xargs -r -n1 ps -o pid=,cmd= | grep gunicorn | awk '{print $1}')

echo $pids

currentDir=$(pwd)
currentFolder=${PWD##*/} 

gnu_notice(){
  echo -e "SkyDrive Copyright (C) 2024 Thomas Logan Smith\nThis program comes with ABSOLUTELY NO WARRANTY;\nThis is free software, and you are welcome to redistribute it\nunder certain conditions.\n"
}

# do a sudo check!
if [ "$EUID" -ne 0 ]; then
  echo -e "\n[ERROR]: The SkyDrive start script requires root privileges. Please run it with sudo.\n"
  exit 1
fi

if [ "$currentFolder" == "scripts" ]; then
  cd ..
  currentDir=$(pwd)
fi


if [[ -z "$pids" ]]; then
  echo "No process found using port 80!"
else
  echo "Found gunicorn PIDs using port 80: $pids."
  for pid in $pids; do
    echo "Killing process $pid..."
    if sudo kill -9 "$pid" >/dev/null 2>&1; then
      echo "Process $pid killed!"
    else
      echo "Failed to kill process $pid."
    fi
  done
fi

#run pld script
sudo /usr/bin/python app/power_low_detector.py > skydrive-pld.log &

echo "starting SkyDrive webserver!" 
sudo gunicorn -w 4 -t 4 -b 0.0.0.0:80 'app:app' --timeout 600 > skydrive-gun.log