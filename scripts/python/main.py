import socket
import _thread
import time
import datetime as dt
import numpy as np
from Representation_Keras_MultiAgent_TensorInput import Representation_Keras_MultiAgent_TensorInput
from DeepQNetwork import DeepQNetwork
from DeepQNetwork_PrioritizedReplay import DeepQNetwork_PrioritizedReplay

from command_parser import command_parser

#rep = Representation_Tabular([4,12,12])
#rep = Representation_Tensorflow(4,0.1)
# rep = Representation_Tensorflow_Batch(inputs=3,
#                                       hidden_unit=4,
#                                       learning_rate=0.1,
#                                       batch_size=9*4,
#                                       trainpass=5000)


rep = DeepQNetwork_PrioritizedReplay                   (gridsize=3,
                                                        actionspaceperagent=5,
                                                        numberofagent=2,
                                                        #hidden_unit=[256, 512, 256],
                                                        hidden_unit=[25, 25],
                                                        learning_rate=0.1,
                                                        batch_size=32,
                                                        trainpass=25,
                                                        experiencebuffer = 128,
                                                        statePreprocessType = 'Tensor',
                                                        convolutionLayer=True
                                                        )

# rep = Representation_Keras_MultiAgent_TensorInput      (gridsize=3,
#                                                         actionspaceperagent=5,
#                                                         numberofagent=2,
#                                                         hidden_unit=[25,25],
#                                                         learning_rate=0.1,
#                                                         batch_size=32,
#                                                         trainpass=25,
#                                                         experiencebuffer=128)

# rep = Representation_Tensorflow_ExperienceReplay_TypeB(statedimperagent=2,
#                                                         actionspaceperagent=5,
#                                                         numberofagent=2,
#                                                         hidden_unit=[12,6],
#                                                         learning_rate=0.1,
#                                                         batch_size=1,
#                                                         trainpass=1,
#                                                         experiencebuffer=1)



# rep = Representation_Keras_MultiAgent                   (statedimperagent=2,
#                                                         actionspaceperagent=5,
#                                                         numberofagent=3,
#                                                         hidden_unit=[128,256],
#                                                         learning_rate=0.1,
#                                                         batch_size=32,
#                                                         trainpass=10,
#                                                         experiencebuffer=64)


# rep = Representation_Tensorflow_ExperienceReplay(       inputs=6,
#                                                         actionspaceperagent=5,
#                                                         numberofagent=2,
#                                                         hidden_unit=[12,6],
#                                                         learning_rate=0.1,
#                                                         batch_size=10,
#                                                         trainpass=1,
#                                                         experiencebuffer=20
#                                                         )

HOSTTX   ='127.0.0.1'
PORTRX = 5000
PORTTX = 4000

send_command_type = ''
send_ok = False
flag_continue = True

total_command_persec = 0
total_getval_persec = 0
total_setval_persec = 0
total_getgreedy_persec = 0

# UDP Receiver
def read():

    # Initialize parameters
    global flag_continue, send_command_type, send_ok,rep, total_command_persec, total_getgreedy_persec, total_setval_persec, total_getval_persec

    while flag_continue:
        # Read port when available
        data, addr = s.recvfrom(1024)

        # Convert the byte array to string
        rxstr = data.decode('utf-8')
        #print(rxstr)

        # Parse Received Command
        command, state, action, value , nextstate, status = command_parser(rxstr)

        # Send ok to client to let it know that packet received.
        #send_command_type = command
        #send_ok = True

        if command == 'setvalue':
            rep.Set_Value(state, action, value)
            total_setval_persec += 1
            s.sendto(("OK,setvalue").encode(), (HOSTTX, PORTTX))

        elif command == 'getvalue':
            val = rep.Get_Value(state, action)
            total_getval_persec+=1
            s.sendto(("OK,getvalue,"+ str(val) ).encode(), (HOSTTX, PORTTX))


        elif command == 'getgreedypair':
            #n1 = dt.datetime.now()
            arg, val = rep.Get_Greedy_Pair(state)
            total_getgreedy_persec += 1
            tmp = "OK,getgreedypair," + str(arg) + "," + str(val)
            s.sendto((tmp).encode(), (HOSTTX, PORTTX))
            #n2 = dt.datetime.now()
            #print(((n2-n1).microseconds)/1e3)

        elif command == 'experience':
            rep.Add_Experience(state, action, nextstate, value, status)
            total_setval_persec += 1
            s.sendto(("OK,experience").encode(), (HOSTTX, PORTTX))

        total_command_persec+=1

    print("Thread read() stopped.")

# UDP Transmitter
def write():

    # Initialize parameters
    global send_command_type,send_ok,flag_continue

    while flag_continue:

        if send_ok :
            send_ok = False
            s.sendto(("OK," + send_command_type).encode(), (HOSTTX, PORTTX))

        time.sleep(100/1000)

    print("Thread write() stopped.")


# UDP Transmitter
def userinput():

    # Initialize parameters
    global flag_continue

    while flag_continue:
        user_input = input()
        if user_input == "stop":
            rep.Save_Model()
            flag_continue = False
            _thread.exit()
            break

    print("Thread userinput() stopped.")


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", PORTRX))
print ('waiting on port:', PORTRX)

_thread.start_new_thread(read,())
_thread.start_new_thread(write,())
_thread.start_new_thread(userinput,())

while flag_continue:
    time.sleep(1)
    print('Total Command Per Sec:{} SetVal:{} GetVal:{} GetGreedy:{}'.format(total_command_persec,total_setval_persec,total_getval_persec,total_getgreedy_persec))
    total_command_persec=0
    total_setval_persec=0
    total_getval_persec=0
    total_getgreedy_persec=0




