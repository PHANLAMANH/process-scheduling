import sys


def counter():
    if not hasattr(counter, "counter"):
        counter.counter = 0
    counter.counter += 1
    return counter.counter


class Process:
    def __init__(self, arrival_time, list):
        self.first_arrival_time = arrival_time
        self.arrival_time = self.first_arrival_time
        self.using = "CPU"
        self.CPU_burst_time = []
        self.resource_usage = []
        self.process_num = counter()
        self.complete_time = -1
        self.total_CPU_burst_time = 0
        self.total_resource_usage = 0

        for t in list[0::2]:
            self.CPU_burst_time.append(t)
            self.total_CPU_burst_time += int(t)
        for t in list[1::2]:
            self.resource_usage.append(t)
            self.total_resource_usage += int(t)

    def switch(self):
        self.using = "resource" if (self.using == "CPU") else "CPU"

    def check_done(self):
        if (self.using == "CPU" and self.CPU_burst_time[0] == 0) or (
            self.using == "resource" and self.resource_usage[0] == 0
        ):
            return True
        return False

    def SetArrivalTime(self, t):
        self.arrival_time = t

    def SetCompleteTime(self, t):
        self.complete_time = t

    def GetArrivalTime(self):
        return self.arrival_time

    def GetFirstArrival(self):
        return self.first_arrival_time

    def GetCompleteTime(self):
        return self.complete_time

    def GetProcessNum(self):
        return int(self.process_num)

    def GetTotalCPUburst(self):
        return self.total_CPU_burst_time

    def GetTotalResourceUsage(self):
        return self.total_resource_usage

    def GetCPUBurstTime(self):
        return self.CPU_burst_time[0]

    def CPURemainEmpty(self):
        if self.CPU_burst_time:
            return False
        else:
            return True

    def Check_resource_remain(self):
        if self.resource_usage:
            return False
        else:
            return True

    def check_reduce(self):
        if self.using == "CPU":
            self.CPU_burst_time[0] -= 1
        elif self.using == "resource":
            self.resource_usage[0] -= 1

    def remove_empty_task(self):
        if self.CPU_burst_time and self.CPU_burst_time[0] == 0:
            self.CPU_burst_time.pop(0)
        if self.resource_usage and self.resource_usage[0] == 0:
            self.resource_usage.pop(0)


def GetArrivalTime(process):
    return process.GetArrivalTime()


def GetProcessNum(process):
    return process.GetProcessNum()


def GetRecentCPUBurstTime(process):
    return process.GetCPUBurstTime()


def GetRemainCPUBurstTime(process):
    return process.GetCPUBurstTime() - process.GetTotalCPUburst()


def AddingWaitingQueue(processes, process, is_prioritized=False):
    if not processes:
        processes.append(process)
    else:
        start = 0
        end = len(processes) - 1
        while start <= end:
            mid = (start + end) // 2
            if process.GetArrivalTime() == processes[mid].GetArrivalTime():
                if is_prioritized:
                    processes.insert(mid + 1, process)
                else:
                    processes.insert(mid, process)
                return
            elif process.GetArrivalTime() < processes[mid].GetArrivalTime():
                end = mid - 1
            else:
                start = mid + 1
        if is_prioritized:
            processes.insert(start, process)
        else:
            processes.insert(start + 1, process)


def get_input(input_file):
    with open(input_file) as input:
        input.seek(0)
        type = int(input.readline())
        if type == 2:
            time_quantum = int(input.readline())
        input.readline()
        processes = []
        for line in input:
            _line = line.strip().split(" ")
            list = []
            for number in _line[1:]:
                list.append(int(number))
            processes.append(Process(int(_line[0]), list))
    data = [type, processes]
    if data[0] == 2:
        data.insert(1, time_quantum)
    return data


def FCFS_scheduling(processes):
    CPU_Waiting_Queue = []
    resourceWaitingQueue = []
    CPU = []
    r = []
    completed = []
    time = 0

    while processes or CPU_Waiting_Queue or resourceWaitingQueue:
        # check for arriving processes
        removing_processes = []
        for process in processes:
            if process.GetArrivalTime() == time:
                AddingWaitingQueue(CPU_Waiting_Queue, process, True)
                removing_processes.append(process)
        for process in removing_processes:
            processes.remove(process)

        # process first CPU waiting queue process
        if CPU_Waiting_Queue and CPU_Waiting_Queue[0].GetArrivalTime() <= time:
            CPU.append(str(CPU_Waiting_Queue[0].GetProcessNum()))
            CPU_Waiting_Queue[0].check_reduce()
            if CPU_Waiting_Queue[0].check_done():
                if CPU_Waiting_Queue[0].Check_resource_remain():
                    CPU_Waiting_Queue[0].SetCompleteTime(time + 1)
                    CPU_Waiting_Queue[0].remove_empty_task()
                    completed.append(CPU_Waiting_Queue.pop(0))
                else:
                    CPU_Waiting_Queue[0].switch()
                    CPU_Waiting_Queue[0].SetArrivalTime(time + 1)
                    CPU_Waiting_Queue[0].remove_empty_task()
                    AddingWaitingQueue(resourceWaitingQueue, CPU_Waiting_Queue.pop(0))
        else:
            CPU.append("_")

        # process first resource waiting queue process
        if resourceWaitingQueue and resourceWaitingQueue[0].GetArrivalTime() <= time:
            r.append(str(resourceWaitingQueue[0].GetProcessNum()))
            resourceWaitingQueue[0].check_reduce()
            if resourceWaitingQueue[0].check_done():
                if resourceWaitingQueue[0].CPURemainEmpty():
                    resourceWaitingQueue[0].SetCompleteTime(time + 1)
                    resourceWaitingQueue[0].remove_empty_task()
                    completed.append(resourceWaitingQueue.pop(0))
                else:
                    resourceWaitingQueue[0].switch()
                    resourceWaitingQueue[0].SetArrivalTime(time + 1)
                    resourceWaitingQueue[0].remove_empty_task()
                    AddingWaitingQueue(CPU_Waiting_Queue, resourceWaitingQueue.pop(0))
        else:
            r.append("_")

        time += 1

    completed.sort(key=GetProcessNum)
    TT = []
    WT = []
    for n in range(len(completed)):
        TT.append(completed[n].GetCompleteTime() - completed[n].GetFirstArrival())
        WT.append(
            TT[n]
            - completed[n].GetTotalCPUburst()
            - completed[n].GetTotalResourceUsage()
        )

    return [CPU, r, TT, WT]


def RR_scheduling(quantum_time, processes):
    CPU_Waiting_Queue = []
    resourceWaitingQueue = []
    CPU = []
    r = []
    completed = []
    time = 0
    stack = 0
    while processes or CPU_Waiting_Queue or resourceWaitingQueue:
        if processes:
            for process in processes[::-1]:
                if process.GetArrivalTime() == time:
                    AddingWaitingQueue(CPU_Waiting_Queue, process, True)
                    processes.remove(process)
        if CPU_Waiting_Queue and CPU_Waiting_Queue[0].GetArrivalTime() <= time:
            stack += 1
            CPU.append(str(CPU_Waiting_Queue[0].GetProcessNum()))
            CPU_Waiting_Queue[0].check_reduce()
            if CPU_Waiting_Queue[0].check_done() or stack == quantum_time:
                if CPU_Waiting_Queue[0].check_done():
                    if CPU_Waiting_Queue[0].Check_resource_remain():
                        CPU_Waiting_Queue[0].SetCompleteTime(time + 1)
                        CPU_Waiting_Queue[0].remove_empty_task()
                        completed.append(CPU_Waiting_Queue.pop(0))
                    else:
                        CPU_Waiting_Queue[0].switch()
                        CPU_Waiting_Queue[0].SetArrivalTime(time + 1)
                        CPU_Waiting_Queue[0].remove_empty_task()
                        AddingWaitingQueue(
                            resourceWaitingQueue, CPU_Waiting_Queue.pop(0)
                        )
                else:
                    CPU_Waiting_Queue[0].SetArrivalTime(time + 1)
                    AddingWaitingQueue(CPU_Waiting_Queue, CPU_Waiting_Queue.pop(0))
                stack = 0
        else:
            CPU.append("_")

        if resourceWaitingQueue and resourceWaitingQueue[0].GetArrivalTime() <= time:
            r.append(str(resourceWaitingQueue[0].GetProcessNum()))
            resourceWaitingQueue[0].check_reduce()
            if resourceWaitingQueue[0].check_done():
                if resourceWaitingQueue[0].CPURemainEmpty():
                    resourceWaitingQueue[0].SetCompleteTime(time + 1)
                    resourceWaitingQueue[0].remove_empty_task()
                    completed.append(resourceWaitingQueue.pop(0))
                else:
                    resourceWaitingQueue[0].switch()
                    resourceWaitingQueue[0].SetArrivalTime(time + 1)
                    resourceWaitingQueue[0].remove_empty_task()
                    AddingWaitingQueue(CPU_Waiting_Queue, resourceWaitingQueue.pop(0))
        else:
            r.append("_")
        time += 1
    completed.sort(key=lambda x: x.GetProcessNum())
    TT = []
    WT = []
    for n in range(len(completed)):
        TT.append(completed[n].GetCompleteTime() - completed[n].GetFirstArrival())
        WT.append(
            TT[n]
            - completed[n].GetTotalCPUburst()
            - completed[n].GetTotalResourceUsage()
        )
    return [CPU, r, TT, WT]


def SJF_scheduling(processes):
    CPU_Waiting_Queue = []
    resourceWaitingQueue = []
    CPU = []
    r = []
    completed = []
    time = 0
    while processes or CPU_Waiting_Queue or resourceWaitingQueue:
        if processes:
            removing_processes = []
            for process in processes[::-1]:
                if process.GetArrivalTime() == time:
                    AddingWaitingQueue(CPU_Waiting_Queue, process, False)
                    removing_processes.append(process)
            for process in removing_processes:
                processes.remove(process)
        if CPU_Waiting_Queue:
            CPU_Waiting_Queue.sort(key=lambda x: x.GetTotalCPUburst())
            CPU.append(str(CPU_Waiting_Queue[0].GetProcessNum()))
            CPU_Waiting_Queue[0].check_reduce()
            if CPU_Waiting_Queue[0].check_done():
                if CPU_Waiting_Queue[0].Check_resource_remain():
                    CPU_Waiting_Queue[0].SetCompleteTime(time + 1)
                    CPU_Waiting_Queue[0].remove_empty_task()
                    completed.append(CPU_Waiting_Queue.pop(0))
                else:
                    CPU_Waiting_Queue[0].switch()
                    CPU_Waiting_Queue[0].SetArrivalTime(time + 1)
                    CPU_Waiting_Queue[0].remove_empty_task()
                    AddingWaitingQueue(resourceWaitingQueue, CPU_Waiting_Queue.pop(0))
        else:
            CPU.append("_")

        if resourceWaitingQueue:
            resourceWaitingQueue.sort(key=lambda x: x.GetTotalResourceUsage())
            r.append(str(resourceWaitingQueue[0].GetProcessNum()))
            resourceWaitingQueue[0].check_reduce()
            if resourceWaitingQueue[0].check_done():
                if resourceWaitingQueue[0].CPURemainEmpty():
                    resourceWaitingQueue[0].SetCompleteTime(time + 1)
                    resourceWaitingQueue[0].remove_empty_task()
                    completed.append(resourceWaitingQueue.pop(0))
                else:
                    resourceWaitingQueue[0].switch()
                    resourceWaitingQueue[0].SetArrivalTime(time + 1)
                    resourceWaitingQueue[0].remove_empty_task()
                    AddingWaitingQueue(CPU_Waiting_Queue, resourceWaitingQueue.pop(0))
        else:
            r.append("_")
        time += 1
    completed.sort(key=GetProcessNum)
    TT = []
    WT = []
    for n in range(len(completed)):
        TT.append(completed[n].GetCompleteTime() - completed[n].GetFirstArrival())
        WT.append(
            TT[n]
            - completed[n].GetTotalCPUburst()
            - completed[n].GetTotalResourceUsage()
        )
    return [CPU, r, TT, WT]


def SRTN_scheduling(processes):
    CPU_Waiting_Queue = []
    resourceWaitingQueue = []
    CPU = []
    r = []
    completed = []
    time = 0
    while processes or CPU_Waiting_Queue or resourceWaitingQueue:
        if processes:
            for process in processes[::-1]:
                if process.GetArrivalTime() == time:
                    AddingWaitingQueue(CPU_Waiting_Queue, process, True)
                    processes.remove(process)
        CPU_Waiting_Queue.sort(key=GetRemainCPUBurstTime())
        if CPU_Waiting_Queue and CPU_Waiting_Queue[0].GetArrivalTime() <= time:
            CPU.append(str(CPU_Waiting_Queue[0].GetProcessNum()))
            CPU_Waiting_Queue[0].check_reduce()
            if CPU_Waiting_Queue[0].check_done():
                if CPU_Waiting_Queue[0].Check_resource_remain():
                    CPU_Waiting_Queue[0].SetCompleteTime(time + 1)
                    CPU_Waiting_Queue[0].remove_empty_task()
                    completed.append(CPU_Waiting_Queue.pop(0))
                else:
                    CPU_Waiting_Queue[0].switch()
                    CPU_Waiting_Queue[0].SetArrivalTime(time + 1)
                    CPU_Waiting_Queue[0].remove_empty_task()
                    AddingWaitingQueue(resourceWaitingQueue, CPU_Waiting_Queue.pop(0))
        else:
            CPU.append("_")
        if resourceWaitingQueue and resourceWaitingQueue[0].GetArrivalTime() <= time:
            r.append(str(resourceWaitingQueue[0].GetProcessNum()))
            resourceWaitingQueue[0].check_reduce()
            if resourceWaitingQueue[0].check_done():
                if resourceWaitingQueue[0].CPURemainEmpty():
                    resourceWaitingQueue[0].SetCompleteTime(time + 1)
                    resourceWaitingQueue[0].remove_empty_task()
                    completed.append(resourceWaitingQueue.pop(0))
                else:
                    resourceWaitingQueue[0].switch()
                    resourceWaitingQueue[0].SetArrivalTime(time + 1)
                    resourceWaitingQueue[0].remove_empty_task()
                    AddingWaitingQueue(CPU_Waiting_Queue, resourceWaitingQueue.pop(0))
        else:
            r.append("_")
        time += 1
    completed.sort(key=GetProcessNum)
    TT = []
    WT = []
    for n in range(len(completed)):
        TT.append(completed[n].GetCompleteTime() - completed[n].GetFirstArrival())
        WT.append(
            TT[n]
            - completed[n].GetTotalCPUburst()
            - completed[n].GetTotalResourceUsage()
        )
    return [CPU, r, TT, WT]


def ScheduleProcessChoice(data):
    if data[0] == 1:
        result = FCFS_scheduling(data[1])
    elif data[0] == 2:
        result = RR_scheduling(data[1], data[2])
    elif data[0] == 3:
        result = SJF_scheduling(data[1])
    elif data[0] == 4:
        result = SRTN_scheduling(data[1])
    return result


def format_result(result):
    return result


def write_output(output_file, result):
    with open(output_file, "w") as output:
        for element in format_result(result):
            for number in element:
                output.write(str(number) + " ")
            output.write("\n")


def main():
    data = get_input(sys.argv[1])
    result = ScheduleProcessChoice(data)
    write_output(sys.argv[2], result)


if __name__ == "__main__":
    main()
