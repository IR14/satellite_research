import asyncio
import argparse

from datetime import datetime
from pathlib import Path

import logging

from engine.engine import Engine, EngineConfig
from producer.messager import FilePublisher, FilePublisherConfig

from common.utils import load_yaml

# log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

logFormatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# fileHandler = logging.FileHandler(LOG_PATH)
# fileHandler.setFormatter(logFormatter)
# fileHandler.setLevel(logging.DEBUG)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.DEBUG)

# rootLogger.addHandler(fileHandler)
log.addHandler(consoleHandler)


def main():
    parser = argparse.ArgumentParser(description='Run services with configuration')
    parser.add_argument('--config', '-c', type=str, required=True, help='Path to configuration file')
    parser.add_argument(
        '--service',
        '-s',
        type=str,
        required=True,
        choices=['engine', 'publisher'],
        help='Specify the service to run: "engine" or "publisher"'
    )

    args = parser.parse_args()

    # Загрузка конфигурации
    config_path = Path(args.config).resolve()
    if not config_path.exists():
        log.error(f"Config file at {config_path} does not exist.")
        return

    # Инициализация и запуск сервиса в зависимости от аргумента
    if args.service == 'engine':
        config = EngineConfig.parse_obj(load_yaml(config_path))
        service = Engine(config)
    else:
        config = FilePublisherConfig.parse_obj(load_yaml(config_path))
        service = FilePublisher(config)
        print(service.data)

    loop = asyncio.get_event_loop()

    start_timestamp = datetime.now()
    loop.run_until_complete(service.init())
    log.debug(f'App engine initialized ({datetime.now() - start_timestamp} sec)')
    loop.create_task(service.run())
    loop.run_forever()
    # service.init()
    # service.run()


if __name__ == '__main__':
    main()
