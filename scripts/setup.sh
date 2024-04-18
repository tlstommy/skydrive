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
  print_header "Setting up VENV."
  echo -e "cwd: - $currentDir"
  if [ -d "$currentDir/.venv" ]; then
    echo "VENV exists."
    source .venv/bin/activate
    
  else
    echo "VENV doesnt exist. Creating one..."
    /usr/bin/python3 -m venv .venv
    source .venv/bin/activate

  fi
  chmod -R 777 $currentDir/.venv > /dev/null &
  print_header "Installing python packages."
  sudo /usr/bin/python3 -m pip install -r requirements.txt --break-system-packages > /dev/null &
  show_loader "   Installing packages...    "

}

#look to see if a drive exists
check_and_mount_nvme_drive(){

    print_header "Checking for available NVME drives..."

    read nvme_drive drive_size drive_type mount_point < <(lsblk -o NAME,SIZE,TYPE,MOUNTPOINTS | grep "nvme" | awk 'NR==1 {print $1, $2, $3, $4}')

    if [ -n "$nvme_drive" ]; then
        echo "NVMe drive detected!"
        echo "Name: $nvme_drive, Size: $drive_size, Type: $drive_type, Mountpoint: $mount_point"

        print_warn "\nThe $drive_size drive, $nvme_drive, will be partitioned and all existing data on the drive will be destroyed."

        read -p "Would you like to proceed? [Y/n] " userInput
        userInput="${userInput^^}"

        if [[ $userInput == "Y" ]]; then
            print_success "You entered 'Y'. Proceeding with the installation.\n"
            sleep 2
        else
            print_error "Aborting!"
            sleep 1
            exit
        fi


        #partion the drive
        #sudo fdisk /dev/$nvme_drive   

        echo "Creating single partition..."

        echo -e "o\nn\np\n1\n\n\nw" | sudo fdisk /dev/$nvme_drive
        
        sleep 5
        print_success "\nPartition Created!"
        

        echo -e "\nFormatting partition to ext4..."
        sudo mkfs.ext4 /dev/"${nvme_drive}p1"

        print_success "${nvme_drive} formatted to ext4 on partiton ${nvme_drive}p1."
        
        sleep 3
        echo "mounting drive to /mnt/nvme..."
        sudo mkdir -p /mnt/nvme
        
        sudo mount "/dev/${nvme_drive}p1" /mnt/nvme


        echo "Running FSTAB to mount at boot..."
        UUID=$(sudo blkid -s UUID -o value "/dev/${nvme_drive}p1")

        # Check if the partitions UUID is already in fstab
        
        if ! grep -q "UUID=$UUID" /etc/fstab; then
          # Add to fstab for auto-mounting on boot
          echo "UUID=$UUID /mnt/nvme ext4 defaults,noatime 0 2" | sudo tee -a /etc/fstab
          echo "Added NVMe drive to /etc/fstab for automatic mounting."
        else
          echo "NVMe drive mount line  already in /etc/fstab."
        fi
            

        mkdir /mnt/nvme/data 
        sudo chmod -R 777 /mnt/nvme   
        print_success "\nDrive /dev/${nvme_drive}p1 mounted and formatted!"

      else
        print_warn "Error: No NVMe drive detected!"
        echo "Please reboot your pi and re-run this script to finish installation and allow an NVME drive to be detected! If you havent rebooted this script before this is normal."
        
        exit
    fi
}


enable_pcie_interface(){
  #enable pcie connector
  print_header "Enabling PCI-E lanes.."


  #add line to boot config file if its not there
  if ! grep -Fxq "# Enable the PCIe External connector." /boot/firmware/config.txt; then
    echo -e "\n# Enable the PCIe External connector.\ndtparam=pciex1\n" | sudo tee -a /boot/firmware/config.txt > /dev/null
  fi
  print_success "PCI-E lanes enabled."

}

node_install(){
  print_header "Installing NodeJS, NPM & Tailwind..."

  sudo apt-get install -y nodejs
  sudo apt-get install -y npm

  npm install -D tailwindcss

  npx tailwindcss -i ./static/src/input.css -o ./static/dist/css/output.css
  npx tailwindcss -i ./static/src/theme.css -o ./static/dist/css/theme.css
  print_success "Node and it's packages installed!"
  
}


set_hostname(){
  #set the hostname
  print_header "Setting hostname"
  sudo bash -c 'echo "skydrive" > "/etc/hostname"'
  sudo sed -i 's/127.0.0.1\s*localhost/127.0.0.1 skydrive/' /etc/hosts
  print_success "\nHostname set to skydrive!"
  echo -e "(This can be changed using raspi-config.)"
}

setup_bonjour(){
  print_header "Setting up Bonjour"

  sudo apt-get install -y avahi-daemon > /dev/null &
  show_loader "   [1/2] Installing avahi-daemon."

  sudo apt-get install -y netatalk > /dev/null &
  show_loader "   [2/2] Installing netatalk.    "

  print_success "Bonjour set up!\n"
}

create_settings_config(){

  JSON='{"pcie_gen3_mode": false,"require_pass": true,"apmode": true}'
  echo $JSON > $currentDir/config/settings.json
  sudo chmod -R 777 $currentDir/config/settings.json
  print_success "Configuration file created in $currentDir/config/ !"

}

password_set(){
  while true; do
    clear
    print_bold "Please specify a password to use when connecting to Skydrive."
    print_warn "Note: This is diffrent than the Pi User Password.\n"

    
    cd config
    touch pass
    cd ..
    password_file="$currentDir/config/pass"
   

    # Prompt for the password
    echo -n "Enter a password: "
    read -s password
    echo

    if [ "${#password}" -lt 8 ]; then
      print_warn "Password must be at least 8 characters long! Please try again."
      sleep 2
      continue
    fi

    # Prompt for the password again for confirmation
    echo -n "Confirm password: "
    read -s password_confirm
    echo

    echo $password
    echo $password_confirm

    # Check if passwords match
    if [ "$password" != "$password_confirm" ]; then
      print_warn "Passwords do not match! Please try again."
      sleep 2

    
 
    else
      # Save the password to the specified file
      echo "$password" > "$password_file"

      print_success "Password has been set!"
      break
    fi

    
  done   
}

update_rc_local(){
  print_header "Updating rc.local,.."
  if grep -Fxq "exit 0" /etc/rc.local; then
    sudo sed -i "/exit 0/i cd $currentWorkingDir && sudo bash $currentWorkingDir/scripts/start.sh > $currentWorkingDir/skydrive.log 2>&1 &" /etc/rc.local
    print_success "Added startup line to rc.local!"
  else
    print_error "ERROR: Unable to add to rc.local"
  fi
}

setup_samba(){

  local junk
  print_header "Setting up SMB (samba)..."
 
  
  
  sudo apt-get install -y samba samba-common-bin

  
  echo "[skydrive-smb]
  path = /mnt/nvme/data
  writeable=Yes
  create mask=0777
  directory mask=0777
  public=no" | sudo tee -a /etc/samba/smb.conf

  print_bold "Creating new SMB User 'pi' with previously specified password..."
  
  echo -e "${password}\n${password}" | sudo smbpasswd -a -s pi

  #restart samba service
  sudo systemctl restart smbd


  print_success "\nCreated new samba share!"
  print_underline "Samba login info. (write this down!):"
  print_bold "Username:  pi"
  print_bold "Password:  ${password}"
  print_bold "Share:     \\\\skydrive\skydrive-smb"

  echo -e "\nPress ENTER to continue setup..."
  read -s junk
}

get_network_mode(){
  while true; do
    clear
    print_bold "How would you like to use Skydrive?"
    print_bold "[1] Use Skydrive as a network attached device on the current network."
    print_bold "[2] Use Skydrive as a standalone device with a broadcasted network.\n"

    
    read -p "Which mode you like to choose? [1, 2]: " userInput

    userInput="${userInput^^}"

    if [[ $userInput == "1" ]]; then
        print_success "You chose option 1, 'Network attached device'.\n"
        sleep 1
        while true; do


          read -p "Confirm: Would you like to proceed with the installion using this mode? [Y/n]: " userInput
          userInput="${userInput^^}"

          if [[ $userInput == "Y" ]]; then
              print_success "You entered 'Y'. Proceeding with the installation.\n"
              sleep 1
              wifiMode=lan
              break
          elif [[ $userInput == "N" ]]; then
              print_warn "Exiting!"
              exit
          else
              print_error "Invalid input! Please try again."
              sleep 1
          fi
       
        done
        break
    elif [[ $userInput == "2" ]]; then
        print_success "You chose option 2, 'Standalone device with a broadcasted network'.\n"
        sleep 1
        while true; do


          read -p "Confirm: Would you like to proceed with the installion using this mode? [Y/n]: " userInput
          userInput="${userInput^^}"

          if [[ $userInput == "Y" ]]; then
              print_success "You entered 'Y'. Proceeding with the installation.\n"
              sleep 1
              wifiMode=ap
              break
          elif [[ $userInput == "N" ]]; then
              print_warn "Exiting!"
              exit
          else
              print_error "Invalid input! Please try again."
              sleep 1
          fi
       
        done
        
        
        break
    else
        print_error "Invalid input! Please try again."
        sleep 1
    fi
  done
}

set_mode(){
  if [[ $wifiMode == "lan" ]]; then
    echo "lan mode on:"
    hostname -I | awk '{print $1}'
  elif [[ $wifiMode == "ap" ]]; then
    local junk
    clear
    
    #sudo nmcli device wifi hotspot ssid SkyDrive password ${password}
    print_success "\nSkydrive Hotspot Mode enabled!"
    print_underline "\nSkydrive Network Info:"
    print_bold "SSID:      SkyDrive"
    print_bold "Password:  ${password}"
    print_bold "\nThis network will be broadcasted from the Pi and can be connected to using the login details above."
    sleep 1
    echo -e "\nPress ENTER to continue setup..."
    read -s junk
  else
    print_error "Mode error 375!"
    sleep 1
  fi
}



resume_prompt(){
  
  
  print_header "Current Directory: $currentWorkingDir"
  print_bold "\nWelcome back!\nSkyDrive will continue setup shortly...\n"
  sleep 3
    
}

opening_prompt(){
  while true; do
    clear
    print_header "Current Directory: $currentWorkingDir"
    print_bold "\nThis script will install all the required packages and setup SkyDrive!\n"
    print_underline "$(print_bold "It will do the following:\n")"
    echo "   [•] Set the hostname to 'Skydrive'."
    echo "   [•] Setup bonjour."
    echo "   [•] Create a log file."
    echo "   [•] Mount the NVME drive."
    echo "   [•] Setup SMB & NPM."
    echo "   [•] Update rc.local so that the Webserver starts on boot."
    echo -e "   [•] Install Required Python packages via pip.\n"

    read -p "Would you like to proceed? [Y/n] " userInput
    userInput="${userInput^^}"

    if [[ $userInput == "Y" ]]; then
        print_success "You entered 'Y'. Proceeding with the installation.\n"
        sleep 2
        break
    elif [[ $userInput == "N" ]]; then
        print_warn "Exiting!"
        exit
    else
        print_error "Invalid input! Please try again."
        sleep 1
    fi
  done
}

show_loader(){
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

print_bold_no_e() {
  echo  "${bold}$1${normal}"
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


#run setup already check here
alreadyRanFlagFile="$currentDir/config/ranPart1.setup"
password_set
exit

#check if setup part 1 has been ran yet
if [ -e "$alreadyRanFlagFile" ]; then
  #it has ran before
  resume_prompt
  sudo rm -rf $currentDir/config/ranPart1.setup
else

  #it hasnt
  echo "The file does not exist."
  opening_prompt
  
  enable_pcie_interface

  #create part1 file for check later
  mkdir config
  sudo chmod -R 777 $currentDir/config # > /dev/null &
  cd config
  touch ranPart1.setup
  cd ..
  
  
  print_standout "\nPlease reboot your Pi and re-run this script to finish installation!"
  print_bold "The install script will resume its installation procedure from the current steps.\n"
  sleep 1
  exit

fi

create_settings_config

check_and_mount_nvme_drive


get_network_mode

echo ${wifiMode}

# Create the log file
sudo touch "$currentWorkingDir/skydrive.log"
print_success "Created logfile, skydrive.log"

password_set


setup_samba



make_venv

set_hostname

setup_bonjour



check_and_mount_nvme_drive


node_install

update_rc_local

set_mode
