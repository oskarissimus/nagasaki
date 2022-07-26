tutaj znajduje się docker-compose który jest ręcznie odpalany na serwerze jednorazowo

domyślna ścieżka z volume data to

```
/home/$USER/grafana
```

na prod zrobić

```
mkdir /home/$USER/grafana
docker-compose up -d
```
