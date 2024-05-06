import asyncio
import paho.mqtt.client as mqtt

from typing import Optional, List
from pydantic import Field
# BaseSettings moved from pydantic
from common.model import BaseMQTTService, BaseMQTTServiceConfig, MQTTConfig
from pathlib import Path

from logging import getLogger


import skyfield
from skyfield.api import load

log = getLogger(__name__)


class EngineConfig(BaseMQTTServiceConfig):
    position: List[float] = Field(description="Текущие координаты системы")
    operation_group: str = Field(description="Группа оперируемых спутников")
    data_url: Optional[str] = Field(None, description="URL-источник для получения TLE данных")
    data_format: str = Field(description="Формат данных для описания астрономических величин спутников")
    publish_topic: MQTTConfig


class Engine(BaseMQTTService):
    def __init__(self, config: EngineConfig) -> None:
        super().__init__(config=config)

        self._position = config.position
        self._operation_group = config.operation_group
        self._data_format = config.data_format
        self._data_url = config.data_url

        self._message_queue = asyncio.Queue()

        # SUBSCRIBE
        self._client.on_message = self.on_message

        # PUBLISH
        self._publish_topic = config.publish_topic
        self._publish_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        if self._publish_topic.username and self._publish_topic.password:
            self._publish_client.username_pw_set(self._publish_topic.username, self._publish_topic.password)
        self._publish_client.connect(self._publish_topic.address, self._publish_topic.port)
        self._publish_client.loop_start()

    # def load_skyfield_tle(self, path: Path, operation_group=None, data_format=None, data_url=None):
    #     operation_group = operation_group or self._operation_group
    #     data_format = data_format or self._data_format
    #
    #     if not data_url:
    #         data_url = ''.join([
    #             self._data_url,
    #             f'?GROUP={operation_group}&FORMAT={data_format}'
    #         ])
    #
    #     filename = '.'.join([
    #         operation_group,
    #         data_format
    #     ])
    #
    #     if data_format == 'tle':
    #         return load.tle_file(data_url, filename=path / filename)

    def on_message(self, client, userdata, msg):
        # Обработка пришедшего сообщения из топика 1 и добавление его в очередь
        message = msg.payload.decode()
        # self._message_queue.put(message)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.process_message(message))

    async def process_message(self, message: str):
        # Добавление полученного сообщения в очередь
        await self._message_queue.put(message)

    async def send_message(self, message: str):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._client.publish, self._topic, message)
        await asyncio.sleep(5)

    # async def cash_message(self, message):
    #     await self._message_queue.put(message)

    async def send_messages_to_topic_2(self):
        while True:
            if not self._message_queue.empty():
                message = await self._message_queue.get()
                self._publish_client.publish(self._publish_topic.topic, message)
                # await asyncio.sleep(0.1)
                self._message_queue.task_done()  # Отмечаем выполнение задачи
            await asyncio.sleep(5)  # Ожидание 5 секунд перед следующей отправкой

    async def run(self):
        # TODO: В конечной реализации будем слушать топик с сообщениями на отправку
        # TODO: Если мы не готовы к отправке (по расписанию), то сообщение будет класться в локальный стек с приоритетом
        self._client.subscribe(self._topic)

        asyncio.create_task(self.send_messages_to_topic_2())

        while True:
            # await self.cash_message("Hello from MQTT")
            # await asyncio.sleep(self._timeout)
            await asyncio.sleep(0.1)
