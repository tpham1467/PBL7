## PBL7 - DUT
### Quick start project  
- Require Docker
#### #1. copy your env file by command line
```
    cp .env.example .env
```
#### #2. move to main folder and run command below
```
    docker-compose up -d --build
```
- Docker will be built and start in port 8001

#### #3. Access your browser and go to `http://localhost:8001`

### #Start project without docker
#### Create a virtual environment
For window
```
    py -m venv ENVPBL7
```

For Mac/Linux
```
    python3 -m venv ENVPBL7
```

#### Activation your virtual environment (move to main folder first)
For window
```
    ENVPBL7\Scripts\activate.ps1
```
For Mac/Linux
```
    source ENVPBL7/bin/activate
```

#### Install requirement (move to PBL7 folder first)
```
    pip install -r .\requirements.txt
```

#### Run Django server
#### #1. copy your env file by command line
```
    cp .env.example .env
```
#### #2. Move to PBL7 Folder and run command below
```
    py manage.py runserver
```