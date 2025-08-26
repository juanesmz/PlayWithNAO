# NAO te enSeña

## Description
This desktop app will create a TCP/IP communication with a NAO robot. Then, the user will be able to setup an activity that will enable a sign detection process related to one of the topics: cordiality, numbers and colors.

## Requirements
- Python 3.12.6

## Installation
### 1. Create environment
```bash
conda create --name PlayWithNAO python=3.12.3
```
### 2. Instalar dependencias | Install dependencies
```bash
conda activate PlayWithNAO
pip install -r requirements.txt
```
### 3. Ejecutar | Run
```bash
python main.py
```

## NAO setup
For the TCP/IP communication a python script must be continously running on the NAO. The python script is full_server.py

### 1. Transfer files to NAO
```bash
scp path/to/full_server.py nao@nao_ip:/path/where/script/is/saved
```
### 2. SSH connection to NAO (ssh password usually is nao)
```bash
ssh nao@nao_ip
```
### 3. Run script (The script argument is the ip of your pc at the network shared with the NAO)
```bash
python path/to/full_server.py --server_ip YOUR_PC_IP
```
