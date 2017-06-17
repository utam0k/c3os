import c3os.db as db
from c3os import api
from c3os import client
from c3os import cntl
from c3os import monitor


def start_all_service():
    """ Starting all module """
    api.start()
    cntl.start()
    monitor.start()
    client.start()
    print("Started all module")
    print('\t====================== Started all servicies ======================')


def main():
    """ Main routine """
    start_all_service()

    while True:
        pass

if __name__ == '__main__':
    main()
