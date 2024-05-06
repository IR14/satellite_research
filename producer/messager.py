import asyncio
from pathlib import Path

from pydantic import Field

from logging import getLogger

from common.utils import read_csv, load_json
from common.model import BaseMQTTService, BaseMQTTServiceConfig

import json
import pandas as pd

log = getLogger(__name__)


class FilePublisherConfig(BaseMQTTServiceConfig):
    file_to_publish: Path = Field(description="Путь к файлу, который будем высвобождать")


class FilePublisher(BaseMQTTService):
    def __init__(self, config: FilePublisherConfig) -> None:
        super().__init__(config=config)

        self.file_to_publish = Path(config.file_to_publish)

        if not self.file_to_publish.is_file():
            log.info(f"No file found at {self.file_to_publish}")
            return

        self.data = self.process_file(self.file_to_publish)

    async def run(self):
        await self.publish_messages()
        await self.disconnect()

    @staticmethod
    def process_file(file_path: Path):
        file_type = file_path.suffix
        if file_type == '.json':
            data = load_json(file_path)
        elif file_type == '.csv':
            # data = read_csv(file_path)
            data = pd.read_csv(file_path)
            data.columns = range(len(data.columns))
            data = data.to_dict(orient='records')
        else:
            log.error(f"File type {file_type} does not supported!")

        return data

    async def publish_messages(self):
        loop = asyncio.get_event_loop()

        for message in self.data:
            await loop.run_in_executor(None, self._client.publish, self._topic, json.dumps(message))
                # log.info(f"Published: {message.strip()}")
            await asyncio.sleep(self._timeout * 0.5)  # Ожидание перед следующим сообщением
