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
  sudo apt-get install -y sysvbanner > /dev/null 
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


enable_interfaces(){


  echo "Enabling interfaces..."

  #install i2c tools if its not already installed.
  sudo apt-get install -y i2c-tools > /dev/null

  #enable pcie connector
  print_header "Enabling PCI-E lanes..."


  #add line to boot config file if its not there
  if ! grep -Fxq "# Enable the PCIe External connector." /boot/firmware/config.txt; then
    echo -e "\n# Enable the PCIe External connector.\ndtparam=pciex1\n" | sudo tee -a /boot/firmware/config.txt > /dev/null
  fi
  print_success "PCI-E lanes enabled."

  sleep 1

  print_header "Arming I2C interface..."

  
  sudo sed -i 's/^dtparam=i2c_arm=.*/dtparam=i2c_arm=on/' /boot/firmware/config.txt
  sudo raspi-config nonint do_i2c 0
  
  print_success "I2C Interface armed.\n"



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

  JSON='{"pcie_gen3_mode": false,"require_pass": true,"apmode": false}'
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
   

    #prompt for the password
    echo -n "Enter a password: "
    read -s password
    echo

    if [ "${#password}" -lt 8 ]; then
      print_warn "Password must be at least 8 characters long! Please try again."
      sleep 2
      continue
    fi

    #prompt for the password confirmation
    echo -n "Confirm password: "
    read -s password_confirm
    echo

    

    #check if passwords match
    if [ "$password" != "$password_confirm" ]; then
      print_warn "Passwords do not match! Please try again."
      sleep 2

 
    else
      #save the password
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
    print_bold "[1] Use Skydrive as a network attached device on the current network. (LAN Mode)"
    print_bold "[2] Use Skydrive as a standalone device with a broadcasted network. (AP Mode)\n"

    
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



#check for i2c device
detect_i2c_device(){
  sudo i2cdetect -y 1
  
  output=$(sudo i2cget -y 1 0x36 2>&1) 
  if [[ "$output" == "Error: Read failed" ]]; then
      echo "Error detected: $output"
      print_error "Error! no i2c device detected at address 0x36"
      exit
  else
      #i2c 36 is found so continue
      echo "$output"
      print_success "i2c detected!"
      
  fi


}



resume_prompt(){
  
  
  print_header "Current Directory: $currentWorkingDir"
  print_bold "\nWelcome back!\nSkyDrive will continue setup shortly...\n"
  sleep 3
    
}

opening_prompt(){
  while true; do
    print_header "Current Directory: $currentWorkingDir"
    print_bold "This script will install all the required packages and setup SkyDrive!\n"
    print_underline "$(print_bold "It will do the following:")"
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
        clear
    fi
  done
}

gnu_notice(){
  clear
  echo -e "\nSkyDrive Copyright (C) 2024 Thomas Logan Smith\nThis program comes with ABSOLUTELY NO WARRANTY;\nThis is free software, and you are welcome to redistribute it\nunder certain conditions.\n"
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
elif [ "$currentFolder" == "skydrive" ]; then
  currentDir=$(pwd)
  currentWorkingDir=$(pwd)
fi


#run setup already check here
alreadyRanFlagFile="$currentDir/config/ranPart1.setup"

#check if setup part 1 has been ran yet
if [ -e "$alreadyRanFlagFile" ]; then
  #it has ran before
  resume_prompt
  sudo rm -rf $currentDir/config/ranPart1.setup
else

  #it hasnt
  gnu_notice
  sleep 3
  
  opening_prompt
  
  enable_interfaces

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

#for power, not really that nessecary
detect_i2c_device

create_settings_config

check_and_mount_nvme_drive


# Create the log file
sudo touch "$currentWorkingDir/skydrive.log"
print_success "Created logfile, skydrive.log"

password_set

setup_samba

make_venv

set_hostname

setup_bonjour

node_install

update_rc_local

sleep 3
clear
banner "SkyDrive"
print_success "$(print_bold "SkyDrive has been successfully installed!")"

print_header "Helpful Info:"
echo "  [•] You can fully shut off SkyDrive by quickly pressing the PSW button three times. Press it once to power off the Pi"
echo "  [•] Have an issue or suggestion? Please, submit it here!"
echo -e "      https://github.com/tlstommy/SkyDrive/issues\n"


print_warn "$(print_bold "(Please reboot your Raspberry Pi to complete installation)")"
print_bold "After your Pi is rebooted, you can access the web UI by going to $(print_blue "'skydrive.local'") or $(print_blue "'$ipAddress'") in your browser.\n"
read -p "Would you like to restart your Raspberry Pi now? [Y/n] " userInput
userInput="${userInput^^}"

if [[ $userInput == "Y" ]]; then
    print_success "You entered 'Y', Restarting now...\n"
    sleep 2
    sudo reboot now
elif [[ $userInput == "N" ]]; then
    print_warn "Please restart your Raspberry Pi later to apply changes.\n"
    exit
else
    print_error "Unknown input, please restart later to apply changes.\n"
    sleep 1
fi

