from classes.server import Server
from tornado.ioloop import IOLoop


if __name__ == "__main__":
    server= Server()
    IOLoop.current().start()