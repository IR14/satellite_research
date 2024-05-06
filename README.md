# Платформа для отправки спутниковых сообщений с использованием GDEPC метода

Всем привет! Это моя выпускная квалификационная работа (ВКР) по теме «Исследование метода GDEPC для снижения стоимости Iridium-сообщения».

В рамках репозитория происходит исследование различных методов сжатия, сериализации и упаковки данных.

## Установка:

1. Создание виртуальной среды
```
python -m venv venv 
```
2. Активация окужения
```
source venv/bin/activate
```
3. Установка зависимостей
```
python -m pip install -r requirements.txt
```


## Запуск микросервисов:
Оркестратор данных на удаленном шлюзе:
```
python run.py -c config/settings.yml -s engine    
```
```
mosquitto_sub -h localhost -p 1883 -t test/topic  
```
Микросервис потоковой передачи данных из датасетов в топики MQTT:
```
python run.py -c config/publisher.yml -s publisher   
```
```
mosquitto_sub -h localhost -p 1883 -t test/publish_topic
```
