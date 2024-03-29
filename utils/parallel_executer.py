import subprocess


class ParallelExecutor:
    def __init__(self, limit: int):
        assert limit > 0, "Limit cannot be less than zero"
        self.limit: int = limit
        self.__executing: list = []
        self.__finished: list = []

    def execute(self, *args, **kwrgs):
        if len(self.__executing) >= self.limit:
            proc = self.__executing.pop(0)
            proc.wait()
            self.__finished.append(proc)

        self.__executing.append(subprocess.Popen(*args, **kwrgs))

    def finish(self):
        for proc in self.__executing:
            proc.wait()
            self.__finished.append(proc)

        return list(self.__finished)

    def clear(self):
        self.finish()

        self.__finished.clear()
        self.__executing.clear()
