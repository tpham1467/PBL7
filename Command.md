#### Export environment
```
    pip freeze > requirements.txt 
```

#### enable entrypoint.sh
```
    chmod +x ./entrypoint.sh
```

#### access django container 
```
    docker exec -it django /bin/sh
```

#### access shell python in django container
```
    python ./manage.py shell
```