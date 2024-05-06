import paho.mqtt.client as mqtt
import asyncio

from logging import getLogger

from pydantic import Field, BaseModel
from typing import Optional, Union, List, Dict

JsonSimpleType = Union[int, float, bool, None, str]
JsonType = Union[JsonSimpleType, List['JSONType'], Dict[str, 'JSONType']]

log = getLogger(__name__)


class MQTTConfig(BaseModel):
    address: str = Field(description="Адрес брокера")
    port: int = Field(description="Порт подключения")
    topic: str = Field(description="Топик для подписки")
    username: Optional[str] = Field(None, description="Логин для аутентификации")
    password: Optional[str] = Field(None, description="Пароль пользователя")
    timeout: int = Field(description="Таймаут между отправкой сообщений")


class BaseMQTTServiceConfig(BaseModel):
    broker: MQTTConfig = Field(description="Данные брокера сообщений MQTT")


class BaseMQTTService:
    def __init__(self, config: BaseMQTTServiceConfig):
        self._config = config
        self._address = config.broker.address
        self._port = config.broker.port
        self._topic = config.broker.topic
        self._username = config.broker.username
        self._password = config.broker.password
        self._timeout = config.broker.timeout

        self._client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self._client.on_connect = self.on_connect
        self._client.on_disconnect = self.on_disconnect
        self._client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc, properties) -> None:
        log.info(f"Connected to MQTT Broker: {self._address}:{self._port} with result code {rc}")

    @staticmethod
    def on_disconnect(client, userdata, flags, rc, properties) -> None:
        if rc != 0:
            log.info(f"Unexpected disconnection.")
        log.info(f"Disconnected with result code {rc}")

    async def connect(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._client.connect, self._address, self._port)
        self._client.loop_start()

    async def disconnect(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._client.disconnect)
        self._client.loop_stop()

    def on_message(self, client, userdata, message):
        # Переопределяем этот метод в подклассе, чтобы обрабатывать входящие сообщения
        pass

    async def init(self):
        # Открытие файла в отдельном потоке
        # with self.file_to_publish.open('r') as file:
        #     lines = await loop.run_in_executor(None, file.readlines)

        if self._username and self._password:
            self._client.username_pw_set(self._username, self._password)

        await self.connect()

    async def run(self) -> None:
        raise NotImplementedError
