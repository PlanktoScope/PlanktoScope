
cd ~
sudo touch starting.sh
sudo chmod 777 starting.sh
sudo echo 'sudo chmod 777 /dev/i2c-1' >> starting.sh

sudo echo './starting.sh' >> .bashrc

sudo reboot
