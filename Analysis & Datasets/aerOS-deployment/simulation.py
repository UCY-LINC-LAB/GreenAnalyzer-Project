from tqdm import tqdm
import heapq
from typing import List
import logging

logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')

class Task:
    def __init__(self, task_id, cpu, memory, duration, power):
        self.task_id = task_id
        self.cpu = cpu
        self.memory = memory
        self.duration = duration  # in seconds
        self.power = power

    def __repr__(self):
        return f"Task({self.task_id}, CPU: {self.cpu}, Mem: {self.memory}, Dur: {self.duration}, Power: {self.power})"


    def __lt__(self, other):
        # Compare tasks based on task_id
        return self.task_id < other.task_id

class ComputeNode:
    
    cpu_minimum = 3
    
    def __init__(self, node_id, total_cpu, total_memory):
        self.node_id = node_id
        self.total_cpu = total_cpu
        self.total_memory = total_memory
        self.available_cpu = total_cpu
        self.available_memory = total_memory
        self.running_tasks = []  # min-heap for task completion times (end_time, task)

    def can_accommodate(self, task: Task) -> bool:
        return self.available_cpu >= task.cpu and self.available_memory >= task.memory

    def assign_task(self, task: Task, current_time: int) -> bool:
        if self.can_accommodate(task):
            self.available_cpu -= task.cpu
            self.available_memory -= task.memory
            end_time = current_time + task.duration
            heapq.heappush(self.running_tasks, (end_time, task))
            return True
        return False

    def release_resources(self, current_time: int):
        while self.running_tasks and self.running_tasks[0][0] <= current_time:
            _, completed_task = heapq.heappop(self.running_tasks)
            self.available_cpu += completed_task.cpu
            self.available_memory += completed_task.memory
    @property
    def cpu_utilization(self):
        return round(100*max((self.total_cpu-self.available_cpu), self.cpu_minimum)/self.total_cpu,2)

    @property
    def memory_usage(self):
        return self.total_memory - self.available_memory

    @property
    def current_power(self):
        return round(self.cpu_utilization * 0.61 + 7.40, 2)
    
    def __repr__(self):
        return f"Node({self.node_id}, CPU: {self.cpu_utilization}, Mem: {self.memory_usage}, Power: {self.current_power})"

    def to_csv_line(self):
        return f"{self.node_id},{self.cpu_utilization},{self.memory_usage},{self.current_power}"

    def to_dict(self):
        return dict(
            node_id = self.node_id,
            cpu_util = self.cpu_utilization,
            memory_util = self.memory_usage,
            power = self.current_power
        )


class Service:
    def __init__(self, service_id, tasks: List[Task], start_at=None, tolerance=None):
        self.service_id = service_id
        self.tasks = tasks
        self.start_at = start_at
        self.tolerance = tolerance

    def __repr__(self):
        return f"Service({self.service_id}, Tasks: {self.tasks})"
    

def can_schedule_service(service: Service, nodes: List[ComputeNode]) -> bool:
    """
    Check if all tasks of a service can be scheduled concurrently.
    """
    required_resources = [(task.cpu, task.memory) for task in service.tasks]
    nodes_resources = [(node.available_cpu, node.available_memory) for node in nodes]
    
    # Sort by largest resource demand for a greedy fit
    required_resources.sort(reverse=True)
    nodes_resources.sort(reverse=True)

    for cpu, memory in required_resources:
        for i, (node_cpu, node_memory) in enumerate(nodes_resources):
            if node_cpu >= cpu and node_memory >= memory:
                # Allocate resources on this node
                nodes_resources[i] = (node_cpu - cpu, node_memory - memory)
                break
        else:
            # If any task cannot be scheduled, the whole service cannot be scheduled
            return False
    return True

def schedule_service(service: Service, nodes: List[ComputeNode], current_time: int) -> bool:
    """
    Assign all tasks of a service to nodes.
    """
    if can_schedule_service(service, nodes):
        for task in service.tasks:
            for node in nodes:
                if node.assign_task(task, current_time):
                    logging.info(f"Task {task.task_id} of Service {service.service_id} assigned to Node {node.node_id}")
                    break
        return True
    return False

def update_services_start_time(services: List[Service], ordered_emissions) -> List[Service]:
    new_services = []
    for service in services:
        tolerance_in_seconds = service.tolerance*60*60
        
        if tolerance_in_seconds and tolerance_in_seconds != 0:
            starting = service.start_at
            tolerance_in_seconds = tolerance_in_seconds + starting
            duration = service.tasks[0].duration
            filtered_emissions = ordered_emissions[ordered_emissions["seconds"]>starting]
            filtered_emissions = filtered_emissions[filtered_emissions["seconds"]<tolerance_in_seconds]
            if filtered_emissions.size>0:
                possible_start = int(filtered_emissions.head(1).seconds)
                service.start_at = possible_start if possible_start>=service.start_at else service.start_at
        new_services.append(service)
    
    return new_services

def schedule_services(services: List[Service], nodes: List[ComputeNode], simulation_time: int, ordered_emissions) -> List[dict]:
    current_time = 0
    history = []
    services = update_services_start_time(services, ordered_emissions)
    for current_time in tqdm(range(simulation_time)):
        logging.info(f"=== Time {current_time} ===")

        # Release resources for completed tasks
        for node in nodes:
            node.release_resources(current_time)

        # Try to schedule services
        for service in services[:]:  # Iterate over a copy of the services list
            if service.start_at and service.start_at>current_time:
                continue
            if schedule_service(service, nodes, current_time):
                logging.info(f"Service {service.service_id} scheduled.")
                services.remove(service)

        if not services:
            logging.info("All services scheduled.")

        
        # Print node states
        for node in nodes:
            logging.info(node)
            curr_element = node.to_dict()
            curr_element["time"] = current_time
            history.append(curr_element)

        is_running_services = len(services)>0                
        if not is_running_services: 
            logging.info("The running finished")
            # break
    return history