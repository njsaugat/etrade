from testing import Writer

class Printer:
    def __init__(self):
        self.printer=Writer()
    
    def print(self,message):
        self.printer.write(message)


printer=Printer()
printer.print("Hello world")


class Engine:
    def start(self):
        print("engine started")


class Car:
    def __init__(self) -> None:
        self.engine=Engine()

    
    def start(self):
        self.engine.start()

car=Car()
car.start()
print(__name__)