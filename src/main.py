"""!
@file main.py
    This file that runs two tasks, both controlling individual motors. The motors
    are run using the code developed in the previous ME 405 labs.
    
@author mecha12
@date   13-Feb-2023
"""

import gc # Memory allocation garbage collector
import pyb # Micropython library
import utime # Micropython version of time library
import cotask # Run cooperatively scheduled tasks in a multitasking system
import task_share # Tasks share data 

from closed_loop_control import clCont # The closed loop control method from closed_loop_control.py
from motor_driver import MotorDriver # The method to drive the motor from motor_drive.py
from encoder_reader import EncoderReader # Read encoder method from encoder_reader.py


def task1_fun(shares):
    """!
    Task which puts things into a share and a queue.
    @param shares A list holding the share and queue used by this task
    """
    
    '''Control Loop Setup'''
    Kp = 0.06				#0.1 excessive oscillation,  0.005 good performance, 0.002 underdamped
    cll = clCont(0, Kp) # Set proportional constant gain for motor 1
    
    '''Serial Bus Setup'''
    ser = pyb.UART(2,115200) # Set serial port
    
    while True:
        '''!
        Runs the motor controller program
        '''
        
        t = utime.ticks_ms() - zeroPoint # Current time since starting the motor driver
        p = enc1.read() # Current position of motor 1
        ser.write(f"Motor 1,{t},{p} \r\n") # Write to the serial port
        lvl = cll.run(8000, p) # Run closed loop controller
        moe1.set_duty_cycle(lvl) # Set the duty cycle
        
        yield

def task2_fun(shares):
    """!
    Task which takes things out of a queue and share and displays them.
    @param shares A tuple of a share and queue from which this task gets data
    """
    
    '''Serial Bus Setup'''
    Kp = 0.06				#0.1 excessive oscillation,  0.005 good performance, 0.002 underdamped
    cll = clCont(0, Kp) # Set proportional gain constant for motor 2
    
    '''Serial Bus Setup'''
    ser = pyb.UART(2,115200) # Set serial port 
    
    while True:
        '''!
        Runs the motor controller program
        '''
        
        t = utime.ticks_ms() - zeroPoint # Current time since starting the motor driver
        p = enc2.read() # Current position of motor 2
        ser.write(f"Motor 2,{t},{p} \r\n") # Write to the serial port
        lvl = cll.run(16000, p) # Run closed loop controller
        moe2.set_duty_cycle(lvl) # Set the duty cycle

        yield

# This code creates a share, a queue, and two tasks, then starts the tasks. The
# tasks run until somebody presses ENTER, at which time the scheduler stops and
# printouts show diagnostic information about the tasks, share, and queue.
if __name__ == "__main__":
    
    #First sets up both motors and their respective encoders with the correct
    #pins and timers.
    ''' Motor 1 Setup Below'''
    pinA10 = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP)
    pinB4 = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP)
    pinB5 = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP)
    tim1 = 3
    moe1 = MotorDriver(pinA10,pinB4,pinB5,tim1)
    
    ''' Encoder 1 Setup Below'''
    pinB6 = pyb.Pin(pyb.Pin.board.PB6, pyb.Pin.IN)
    pinB7 = pyb.Pin(pyb.Pin.board.PB7, pyb.Pin.IN)
    enc1 = EncoderReader(pinB6, pinB7, 4)
    enc1.zero()
    
    ''' Motor 2 Setup Below'''
    pinC1 = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP)
    pinA0 = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP)
    pinA1 = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP)
    tim2 = 5
    moe2 = MotorDriver(pinC1,pinA0,pinA1,tim2)
    
    ''' Encoder 2 Setup Below'''
    pinC6 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.IN)
    pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.IN)
    enc2 = EncoderReader(pinC6, pinC7, 8)
    enc2.zero()
    
    zeroPoint = utime.ticks_ms()

    # Create a share and a queue to test function and diagnostic printouts
    share0 = task_share.Share('h', thread_protect=False, name="Share 0")
    q0 = task_share.Queue('L', 16, thread_protect=False, overwrite=False,
                          name="Queue 0")

    # Create the tasks. If trace is enabled for any task, memory will be
    # allocated for state transition tracing, and the application will run out
    # of memory after a while and quit. Therefore, use tracing only for 
    # debugging and set trace to False when it's not needed
    task1 = cotask.Task(task1_fun, name="Task_1", priority=1, period=40,
                        profile=True, trace=False, shares=(share0, q0))
    task2 = cotask.Task(task2_fun, name="Task_2", priority=2, period=40,
                        profile=True, trace=False, shares=(share0, q0))
    cotask.task_list.append(task1)
    cotask.task_list.append(task2)
    
    ser = pyb.UART(2,115200)

    # Run the memory garbage collector to ensure memory is as defragmented as
    # possible before the real-time scheduler is started
    gc.collect()

    # Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
    while True:
        try:
            cotask.task_list.pri_sched()
        except KeyboardInterrupt:
            ser.write("Stahp\r\n") # Send stop message at keyboard interrupt
            break