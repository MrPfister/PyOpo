import datetime
from datetime import date
from pyopo.opl_exceptions import *
import logging       
import logging.config   

logging.config.fileConfig(fname="logger.conf")
_logger = logging.getLogger()                            
#_logger.setLevel(logging.DEBUG)

def qcode_year(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x1E - YEAR")
    stack.push(0, datetime.datetime.now().year)
    

def qcode_month(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x17 - MONTH")
    stack.push(0, datetime.datetime.now().month)
    

def qcode_day(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x04 - DAY")
    stack.push(0, datetime.datetime.now().day)


def qcode_datetosecs(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x45 - DATETOSECS")
    stack.push(1, int(datetime.datetime.now().timestamp()))


def qcode_hour(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x12 - HOUR")
    stack.push(0, datetime.datetime.now().hour)
    

def qcode_minute(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x16 - MINUTE")
    stack.push(0, datetime.datetime.now().minute)


def qcode_second(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x1C- SECOND")
    stack.push(0, datetime.datetime.now().second)


def qcode_datim(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0xC1- DATIM$")
    # Example output: Tue 26 May 1992 13:01:44

    datetime_string = datetime.datetime.now().strftime("%a %d %b %Y %H:%M:%S")
    stack.push(3, datetime_string)
    
    

def qcode_month_str(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0xCD - MONTH$ pop%")

    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    m = stack.pop()

    if m < 1 or m > 12:
        raise(KErrOutOfRange)

    stack.push(3, months[m-1])


def qcode_dayname(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0xC2 - DAYNAME$ pop%1")

    daynames = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

    dow = stack.pop()

    if dow < 1 or dow > 7:
        raise(KErrOutOfRange)

    stack.push(3, daynames[dow-1])


def qcode_days(procedure, data_stack, stack):
    #_logger.debug(f"0x57 0x40 - DAYS pop%3 pop%2 pop%1")

    y = stack.pop()
    m = stack.pop()
    d = stack.pop()

    # Input validation
    if y < 1900 or y > 2100:
        raise(KErrOutOfRange)
    
    if m < 1 or m > 12:
        raise(KErrOutOfRange)
    
    if d < 1 or d > 31:
        raise(KErrOutOfRange)

    # Returns the number of days since 1/1/1900
    delta = date(y, m, d) - date(1900, 1, 1)
    days = delta.days

    print (f" - DAYS {d} {m} {y} = {days}")
    stack.push(0, days)


def qcode_secstodate(procedure, data_stack, stack):
    #_logger.debug(f"0xFB - secstodate pop8 pop%7 pop%6 pop%5 pop%4 pop%3 pop%2 pop%1")

    yrday_addr = stack.pop()
    sc_addr = stack.pop()
    mn_addr = stack.pop()
    hr_addr = stack.pop()
    dy_addr = stack.pop()
    mo_addr = stack.pop()
    yr_addr = stack.pop()
    s = stack.pop()

    secstodate=datetime.datetime.fromtimestamp(s)

    data_stack.write(0, secstodate.year, yr_addr)
    data_stack.write(0, secstodate.month, mo_addr)
    data_stack.write(0, secstodate.day, dy_addr)
    data_stack.write(0, secstodate.hour, hr_addr)
    data_stack.write(0, secstodate.minute, mn_addr)
    data_stack.write(0, secstodate.second, sc_addr)
    data_stack.write(0, secstodate.timetuple().tm_yday, yrday_addr)