##fengcong@caas.cn
##2020-9-4 15:11:50

##v1 : Control the number of tasks in pbs queue.

#This application is resident in the background of login4.
#Whenever the queue is changed, the tasks to be delivered in the queue will be backed up to a file.
#The queues of different users are backed up to different places.(eg. these home dir)but this need root access.

#usage: python __file__  -b back.up.dir -q queue.len.file( queue_name  Q_number)
#e.g python __file__  -b /home/fengcong/.QS_server.queue -q /home/fengcong/.QS_server.queue.bak/chengshifeng_cluster.limit

import argparse
import os,sys,shutil
import time
from queue import PriorityQueue
from multiprocessing.managers import BaseManager
from multiprocessing import Process
from multiprocessing import Lock
import datetime
import subprocess
import io
import socket

class Manager(BaseManager):
    pass

Manager.register('get_priorityQueue', PriorityQueue)


def queue_thread(pq,queue_name,queue_len,lock,qsub_file):
    #create file
    lock.acquire()
    if not os.path.exists(qsub_file):
        os.system("touch %s"%(qsub_file))
    lock.release()
    #get user name
    user = os.popen('whoami')
    user = user.readline()
    user = user.strip('\n')

    #get stat of this queue
    while True:
        time.sleep(10)
        #info = os.popen("qstat -u %s | awk '{if($3==\"%s\" && $10==\"Q\")print}' | wc -l"%(user,queue_name))
        Qnum=9999
        #Qnum=info.readline()
        #Qnum=int(Qnum.strip('\n'))
        proc = subprocess.Popen("qstat -u %s | awk '{if($3==\"%s\" && $10==\"Q\")print}' | wc -l"%(user,queue_name), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=-1)
        proc.wait()
        stream_stdout = io.TextIOWrapper(proc.stdout, encoding='utf-8')
        stream_stderr = io.TextIOWrapper(proc.stderr, encoding='utf-8')
        str_stdout = str(stream_stdout.read())
        str_stderr = str(stream_stderr.read())
        Qnum=int(str_stdout.strip('\n'))
        if str_stderr.strip() != "": #if login3 down
            print("[%s][Error]:%s"%(str(datetime.datetime.now()),str_stderr))
            sys.stdout.flush()
            continue
        # print("queue:%s\t%d"%(queue_name,Qnum)) ########
        while Qnum < queue_len[queue_name]:
            if not pq.empty():
                cmd_tuple=pq.get()
                ## qsub
                print("[%s][%s qsub]:%s"%(str(datetime.datetime.now()),queue_name,cmd_tuple[3]))
                sys.stdout.flush()
                os.system("cd %s && %s"%(cmd_tuple[2],cmd_tuple[3]))
                
                lock.acquire()
                ouf = open(qsub_file,"a+")
                ouf.write("%s<---->%d<---->%s<---->%s<---->%s\n"%(cmd_tuple[1],-1*cmd_tuple[0],cmd_tuple[2],cmd_tuple[3],cmd_tuple[4]))
                ouf.close()

                lock.release()
                ##
            else:
                break

            Qnum +=1


        # lock.acquire()
        # ouf = open(backup_file,"a+")
        # for i in pq.queue():
        #     ouf.write("%s<---->%d<---->%s\n"%(i[2],i[0],i[1]))
        # ouf.close()

        # lock.release()

def noqueue_thread(noqueue,noqueue_file):
    if not os.path.exists(noqueue_file):
        os.system("touch %s"%(noqueue_file))
    while True:
        time.sleep(10)
        if not noqueue.empty():
            cmd_tuple=noqueue.get()
            print("[%s][%s qsub]:%s"%(str(datetime.datetime.now()),"noqueue",cmd_tuple[3]))
            sys.stdout.flush()
            os.system("cd %s && %s"%(cmd_tuple[2],cmd_tuple[3]))
            ouf = open(noqueue_file,"a+")
            ouf.write("%s<---->%d<---->%s<---->%s<---->%s\n"%(cmd_tuple[1],-1*cmd_tuple[0],cmd_tuple[2],cmd_tuple[3],cmd_tuple[4]))
            ouf.close()


def socket_thread(write_path,port):
    port = port 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostname()
    s.bind((host,port))
    s.listen(5)
    print('listen at port :',port)
    sys.stdout.flush()
    while True:
        conn,addr = s.accept()
        
        while True:
            data = conn.recv(1024)
            data = data.decode()
            if not data:
                break
            # print('recieved message:',data)
            ##
            wf=os.open(write_path,  os.O_WRONLY)
            os.write(wf,bytes(data, 'utf-8'))
            os.close(wf)
        
        
        conn.close()
    
    s.close()


if __name__ == "__main__":
    cmdparser = argparse.ArgumentParser(description="Control the number of tasks in pbs queue." )

    #cmdparser.add_argument("-w","--workdir", dest="workdir",type=str, required=True,
    #                        help="work dir,used for backup the cmd queue")
    cmdparser.add_argument("-p","--port", dest="port",type=int, required=True,
                            help="socket port for listening")
    cmdparser.add_argument("-q","--queuelen", dest="queuelen",type=str, default="/public/home/fengcong/.QS_server.queue/chengshifeng_cluster.limit",
                            help="The length of each queue")
    
    args = cmdparser.parse_args()

    #get args
    user = os.popen('whoami')
    user = user.readline()
    user = user.strip('\n')
    work_dir= "/public/home/%s/.QS_server.queue/"%(user) #args.workdir   # workdir
    fifo_name = "QS_server.fifo.tmp"   #fifo name
    fifo_path = work_dir+"/tmp"     #fifo dir
    queuefile = args.queuelen  #limit file
    backup_file= work_dir+"/queue.backup"
    recv_file=work_dir+"/queue.recv"
    qsub_file=work_dir+"/queue.qsub"
    noqueue_file=work_dir+"/noqueue.qsub"
    port=args.port

    #creat dir
    os.system("mkdir -p %s"%(work_dir))

    if os.path.exists(fifo_path):
        shutil.rmtree(fifo_path)
        
    os.mkdir(fifo_path)
    #mkfifo 
    fifo_full_path = fifo_path+"/"+fifo_name
    print(fifo_full_path)
    os.mkfifo(fifo_full_path)

    #creat a proxy
    m = Manager()
    m.start()

    #init queuelist
    queue_dict={} #store queue list
    queue_len={}
    inf = open(queuefile,"r")
    for line in inf.readlines():
        ls = line.strip().split(" ")
        queue_dict[ls[0]] = m.get_priorityQueue()
        queue_len[ls[0]] = int(ls[1])
    inf.close()

    # queue_dict["big"].put((1,2))
    # # print(queue_dict["big"].queue())
    # print(dir(queue_dict["big"]))
    # print(queue_dict["big"])

    ##noqueue
    noqueue = m.get_priorityQueue()

    #init queulist from backup file
    if os.path.exists(qsub_file) and os.path.exists(recv_file) and os.path.exists(noqueue_file):
        os.system("sort %s %s %s | uniq -u > %s"%(qsub_file,noqueue_file,recv_file,backup_file))
        inf = open(backup_file,"r")
        record_num=0
        for line in inf.readlines():
            record_num+=1
            ls = line.strip().split("<---->") # queue_name<---->priroty<---->path<---->cmd<---->mlist
            if ls[0] == "noqueue":
                noqueue.put((int(ls[1])*-1,ls[0],ls[2],ls[3],ls[4]))
            else:
                queue_dict[ls[0]].put((int(ls[1])*-1,ls[0],ls[2],ls[3],ls[4]))  #p  queue path cmd
        inf.close()
        print("[%s][backup]:%s"%(str(datetime.datetime.now()),"read %d jobs from backup file."%(record_num)))
        sys.stdout.flush()


    #queue thread
    lock=Lock()
    queue_threads=[]  
    for i in queue_dict:
        queue_threads.append(Process(target=queue_thread,args=(queue_dict[i],i,queue_len,lock,qsub_file)))



    for thread in queue_threads:
        thread.start()

    noqueue_proc=Process(target=noqueue_thread,args=(noqueue,noqueue_file))
    noqueue_proc.start()

    
    socket_proc=Process(target=socket_thread,args=(fifo_full_path,port))
    socket_proc.start()
    
    

    while True:
        rf = os.open(fifo_full_path, os.O_RDONLY)
        #Start a round of reading 
        cmds=""
        while True:
            s = os.read(rf,1024)
            if len(s) == 0:
                break
            
            cmds +=bytes.decode(s)  # joint cmd string
        # print(cmds)
        #deal these cmds
        cmd_list = cmds.strip().split("\n") #queue_name<---->priroty<---->path<---->cmd<---->mlist
        ouf=open(recv_file,"a+")
        for cmd in cmd_list:
            ls = cmd.strip().split("<---->")
            print("[%s][recv]:%s"%(str(datetime.datetime.now()),cmd))
            sys.stdout.flush()
            if ls[0] == "noqueue":
                noqueue.put((int(ls[1])*-1,ls[0],ls[2],ls[3],ls[4]))
            else:
                queue_dict[ls[0]].put((int(ls[1])*-1,ls[0],ls[2],ls[3],ls[4]))  #add to pqueue
            ouf.write(cmd+"\n")
        ouf.close()
        
        #end this round of reading
        os.close(rf)

    for thread in queue_threads:
        thread.join()
