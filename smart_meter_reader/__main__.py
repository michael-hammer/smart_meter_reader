import logging
import asyncio
from config import settings
from .clients import read_client
from .sinks import write_sink


def main():
    """Main function which can be used to run the smart meter reader in an endless loop.
    It generates a `read_client` and a `write_sink` task and owns an event loop in which
    all asyncio tasks are running.

    It does NOT expect any command line parameters as all configuration is received via
    dynaconf settings files.
    """
    logging.basicConfig(level=settings.debug_level)

    data_queue = asyncio.Queue(1)

    tasks = []
    try:
        # TODO: Not clear to me what the difference between create_task and 
        # ensure_future in my setting is .. BUT: first leads to some locking situation
        # together with Homie4 and the embedded asyncio loop for paho_mqtt
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(read_client(data_queue))
        asyncio.ensure_future(write_sink(data_queue))
        loop.run_forever()

        #loop = asyncio.new_event_loop()
        #tasks.append(loop.create_task(read_client(data_queue)))
        #tasks.append(loop.create_task(write_sink(data_queue)))
        #loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        print("Gracefull quit main loop ...")
    except Exception as e:
        print(e)
        pass
    finally:
        # for task in tasks:
        #     task.cancel()
        # # It seems you need to let the loop run at least until all tasks are in done 
        # # state to prevent ERROR messages
        # while not all([task.done() for task in tasks]):
        #     loop._run_once()
        loop.close()


if __name__ == '__main__':
    main()
