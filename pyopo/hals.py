import datetime
from pygame.locals import *


class hal:
    def __init__(self, data_stack):
        self._data_stack = data_stack

    def get_identifier(self) -> str:
        raise NotImplementedError()

    def process_io(self):
        raise NotImplementedError()

    def has_handle(self, status_handle) -> bool:
        raise NotImplementedError()

    def iowaitstat(self, status_handle):
        raise NotImplementedError()


class hal_tim(hal):
    """
    S3 Timers operate at 10Hz
    https://www.fogma.co.uk/prosoft/oplzone/s3/OSCalls.txt

    """

    def __init__(self, data_stack):
        super().__init__(data_stack)
        self._timers = []

    def get_identifier(self) -> str:
        return "TIM:"

    def process_io(self):
        timers_to_remove = []
        for timer in self._timers:
            if timer["end_datetime"] > datetime.datetime.now():
                # Timer has now completed
                self._data_stack.write(0, timer["expire"], timer["var_dsf_addr"])

                # Signal completion
                timer["signal"] = -46

                timers_to_remove.append(timer)
            else:
                current_val = (
                    datetime.datetime.now() - timer["start_dateime"]
                ).seconds * 10

                self._data_stack.write(0, current_val, timer["var_dsf_addr"])
                print(
                    f"Storing Timer value: {current_val} to DSF Offset {timer['var_dsf_addrt']}"
                )

    def iowaitstat(self, status_handle):
        for timer in self._timers:
            if timer["var_dsf_addr"] == status_handle:
                if timer["signal"]:
                    # There has been a signal
                    print("Clearing IO Signal")
                    timer["signal"] = None
                    return
                else:
                    # Await timer completion
                    print("Awaiting timer completion...")
                    input()
                    pass

    def add_timer(self, dsf_addr: int, expire: int):
        delta_seconds = expire / 10
        print(f"Timer request for {delta_seconds} seconds")

        self._timers.append(
            {
                "var_dsf_addr": dsf_addr,
                "value": 0,
                "expire": expire,
                "start_datetime": datetime.datetime.now(),
                "end_datetime": datetime.datetime.now()
                + datetime.timedelta(seconds=delta_seconds),
                "signal": -46,  # Start off with initial signal
            }
        )

    def has_handle(self, status_handle) -> bool:
        for timer in self._timers:
            if timer["var_dsf_addr"] == status_handle:
                return True

        return False
