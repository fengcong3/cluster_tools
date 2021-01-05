# cluster_tools
A set of tools useful for improving productivity in a cluster

## QS
QS is a task delivery script suitable for pbs clusters. It has the functions of **monitoring memory, recording execution time, recording the execution status of each command, configuring the computing node conda environment, remote delivery,E-mail notification, and controlling the number of tasks in each queue**.
```
usage: QS [-h] -p THREADS -m MEMORY [-q [QUEUE]] [-c HOST] [-i PRIORITY]
          [-e CONDA] [-l EMAIL] [-r] [-s] [-a APPEND] [-n] [-o PORT]
          scripts [scripts ...]

quick qsub/fengcong@caas.cn

positional arguments:
  scripts               scripts of u wanna sub.

optional arguments:
  -h, --help            show this help message and exit
  -p THREADS, --threads THREADS
                        threads/core.(eg. -p 1)
  -m MEMORY, --memory MEMORY
                        memory usage,G(eg. -m 1)
  -q [QUEUE], --queue [QUEUE]
                        queue,default:csf_queue
  -c HOST, --host HOST  host,if specific multi-host,connect with '/'. (eg. -c
                        comput1/comput2)
  -i PRIORITY, --priority PRIORITY
                        priority,-1024 to 1020 (eg. -i 1020)
  -e CONDA, --conda CONDA
                        conda enviroment(eg. -e py3)
  -l EMAIL, --email EMAIL
                        email notification(eg. -l test@qq.com)
  -r, --memplot         Record memory usage and draw diagrams(eg. -r)
  -s, --stats           record exit status for each command(eg. -s)
  -a APPEND, --append APPEND
                        append to limit queue,Assign priority to limit
                        queue(eg. -a 3)
  -n, --nolocal         if not on login4,but u wana qsub job(eg. -n)
  -o PORT, --port PORT  if not on login4,but u wana qsub job,u must Specify
                        this parameter(eg. -o 40006)
```

## QS_server
QS_server is a multi-process task scheduling management script. Used in conjunction with QS, it is used to control the number of tasks in each queue and relieve the pressure of PBS scheduling when there are too many tasks.
```
usage: QS_server.py [-h] -p PORT [-q QUEUELEN]

Control the number of tasks in pbs queue.

optional arguments:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  socket port for listening
  -q QUEUELEN, --queuelen QUEUELEN
                        The length of each queue
```

## mypp
A simple script, when you have many scripts to execute, it can control the number of scripts you execute in parallel.
```
usage:  mypp script.list threads 
eg. 
    nohup mypp download.sh.list 10 &
```

## mypp2 
A simple script, when you have many commands to execute, it can control the number of commands you execute in parallel.
```
usage: mypp2 command_list.sh threads
```

## mywd
Monitor the memory usage of a background process and its child processes, and draw graphs.
```
usage: nohup mywd PID outprefix &
```

