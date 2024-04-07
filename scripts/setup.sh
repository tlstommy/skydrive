#!/bin/bash

#formatting stuff
bold=$(tput bold)
underline=$(tput smul)
normal=$(tput sgr0)
standout=$(tput smso)
blink=$(tput blink)


red=$(tput setaf 1)
green=$(tput setaf 2)
yellow=$(tput setaf 3)

#make a venv if one doesnt exist
make_venv(){
  
  echo -e "cwd: - $currentDir"
  if [ -d "$currentDir/.venv" ]; then
    echo "venv exists."
    source .venv/bin/activate
    
  else
    echo "venv doesnt exist."
    python3 -m venv .venv
    source .venv/bin/activate

  fi

  
  
}

#look to see if a drive exists
check_and_mount_nvme_drive() {
    if lsblk | grep -q "nvme"; then
        echo "NVMe drive detected!"
        lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS | grep "nvme" | awk '{print "Name: " $1 ", Size: " $2 ", Type: " $3", Mountpoint: " $4}'

    else
        echo "No NVMe drive detected!"
        echo "Please reboot your pi and re-run this script to finish installation and allow an nvme drive to be detected! If you havent ran this setup script before this is normal."
        exit
    fi
}


enable_pcie_interface(){
  #enable pcie connector
  echo "run enable interfaces - dtparam check"


  #add line to boot config file if its not there
  if ! grep -Fxq "# Enable the PCIe External connector." /boot/firmware/config.txt; then
    echo -e "\n# Enable the PCIe External connector.\ndtparam=pciex1\n" | sudo tee -a /boot/firmware/config.txt > /dev/null


    echo -e "Please reboot your pi and re-run this script to finish installation!"
    exit 
  fi

  check_nvme_drive

}


show_loader() {
  local pid=$!
  local delay=0.1
  local spinstr='|/-\'
  printf "$1 [${spinstr:0:1}] "
  while ps a | awk '{print $1}' | grep -q "${pid}"; do
    local temp=${spinstr#?}
    printf "\r$1 [${temp:0:1}] "
    spinstr=${temp}${spinstr%"${temp}"}
    sleep ${delay}
  done
  if [[ $? -eq 0 ]]; then
    printf "\r$1 [\e[32m\xE2\x9C\x94\e[0m]\n"
  else
    printf "\r$1 [\e[31m\xE2\x9C\x98\e[0m]\n"
  fi
}


#status funcs
print_header() {
  echo -e "${bold}${underline}$1${normal}"
}

print_standout() {
  echo -e "${standout}$1${normal}"
}

print_blink() {
  echo -e "${blink}$1${normal}"
}

print_bold() {
  echo -e "${bold}$1${normal}"
}

print_underline() {
  echo -e "${underline}$1${normal}"
}


print_success() {
  echo -e "${green}$1${normal}"
}

print_error() {
  echo -e "${red}$1${normal}"
}

# better color vals than tput
print_warn() {
  echo -e "\e[38;2;255;255;0m$1\e[0m"

}

print_blue() {
  echo -e "\e[38;2;65;105;225m$1\e[0m"
}


# Set the current  and ip
currentDir=$(dirname "$PWD")
currentWorkingDir=$(pwd)
currentFolder=${PWD##*/} 
ipAddress=$(hostname -I | cut -d ' ' -f 1)

# do a sudo check!
if [ "$EUID" -ne 0 ]; then
  echo -e "\n[ERROR]: $(print_error "The installation script requires root privileges. Please run it with sudo.\n")"
  exit 1
fi

if [ "$currentFolder" == "scripts" ]; then
  cd ..
  currentDir=$(pwd)
  currentWorkingDir=$(pwd)
fi

echo -e "$currentDir"
echo -e "$currentWorkingDir"
echo -e "$currentFolder"
echo -e "$ipAddress"


make_venv

enable_pcie_interface

#flask run