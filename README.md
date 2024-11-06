# K-Cuda

--------------------------------------------------------------------------------------------------------------------




#Tutorial: Instalação e Uso do Código

Cuda 12.6
````
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-wsl-ubuntu.pin
sudo mv cuda-wsl-ubuntu.pin /etc/apt/preferences.d/cuda-repository-pin-600
wget https://developer.download.nvidia.com/compute/cuda/12.6.2/local_installers/cuda-repo-wsl-ubuntu-12-6-local_12.6.2-1_amd64.deb
sudo dpkg -i cuda-repo-wsl-ubuntu-12-6-local_12.6.2-1_amd64.deb
sudo cp /var/cuda-repo-wsl-ubuntu-12-6-local/cuda-*-keyring.gpg /usr/share/keyrings/
sudo apt-get update
sudo apt-get -y install cuda-toolkit-12-6

````
Install libgm
````
apt update && apt upgrade
apt install git -y
apt install build-essential -y
apt install libssl-dev -y
apt install libgmp-dev -y
````
Python 
````
sudo apt-get install python3.9
````
Clonar o repositório
````
git clone https://github.com/vkThiago/KeyHuntCuda-vk.git
````
Instalação sem placa de video
````
cd KeyHuntCuda-vk
make all
````
Instalação com placa de video
````
cd KeyHuntCuda-vk
make gpu=1 CCAP=89 all
````

