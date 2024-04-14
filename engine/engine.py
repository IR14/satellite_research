from typing import Optional, Union
from pydantic import Field
from pathlib import Path

from common.utils import SingletonMeta

import skyfield
from skyfield.api import load


class EngineConfig:
    position: Union[float, float, float] = Field(description="Текущие координаты системы")
    operation_group: str = Field(description="Группа оперируемых спутников")
    data_url: Optional[str] = Field(description="URL-источник для получения TLE данных")
    data_format: str = Field(description="Формат данных для описания астрономических величин спутников")
    # tolerance: 0.001
    # elevation_deg: 60
    # hours_predict: 1
    # modem_port: "/dev/ttyUSB0"
    # root_node: str
    # # TODO: Убрать значение по умолчанию.
    # channel: Channel = Channel.voice
    # settings_path: Optional[str]
    # nlp_url: Optional[str]
    # state_removal_delay_s: int
    # state_lifetime_s: int
    # recalcs_limit: int
    # prometheus_port: int = Field('', env='PROMETHEUS_PORT')
    # nlp_logging: bool = Field(False, env='NLP_LOGGING')
    # steps_topic: str
    # evp_topic: str
    # session_topic: str = Field(description='Топик для сообщения с мапингом с сессий от модорка кроссбару')
    # voice_nlp: bool = Field(False, description='Флаг включения nlp для голосовых транскрипций')
    # chat_nlp: bool = Field(False, description='Флаг включения nlp для сообщений чата')
    # ssbo_id: str = Field('', description='Динамический id для вызова сценариев субо')
    # experiments: List[str] = Field([], description='Список экспериментальных модификаторов поведения')
    # kafka_producer: AsyncProducerConfig
    # kafka_consumer: AsyncConsumerConfig
    # # TODO: Временное, убрать.
    # db: PostgreConfig


class EngineConfigWrapper(metaclass=SingletonMeta):
    def __init__(self, config: Optional[EngineConfig] = None) -> None:
        self._config = config

    @property
    def config(self) -> EngineConfig:
        return self._config


class Engine:
    def __init__(self, config: EngineConfig, satellites: Optional[...]) -> None:
        self._config = config
        self._position = config.position
        self._operation_group = config.operation_group
        self._data_format = config.data_format
        self._data_url = config.data_url
        # self._satellites =

    def load_skyfield_tle(self, path: Path, operation_group=None, data_format=None, data_url=None):
        operation_group = operation_group or self._operation_group
        data_format = data_format or self._data_format

        if not data_url:
            data_url = ''.join([
                self._data_url,
                f'?GROUP={operation_group}&FORMAT={data_format}'
            ])

        filename = '.'.join([
            operation_group,
            data_format
        ])

        if data_format == 'tle':
            return load.tle_file(data_url, filename=path / filename)

