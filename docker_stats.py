import socket
import json
import time
import os
import csv

SOCKET_PATH = '/var/run/docker.sock'
HEADERS = ['timestamp', 'mem_percentage', 'cpu_percentage', 'num_pid']


class DockerStats(object):

    def __init__(self, container_name, file_path):
        self.container_name = container_name
        self.file_path = file_path

    @property
    def connection_string(self):
        connection_string = f"GET http://localhost/containers/{self.container_name}/stats?stream=False HTTP/1.1\r\nHost: *\r\n\r\n".encode()
        return connection_string

    @property
    def file_descriptor(self):

        if os.path.exists(self.file_path):
            
            file_fd = open(self.file_path, 'a', newline='', encoding='utf-8')
            csv_writer = csv.writer(file_fd)
            return csv_writer

        else:
            
            file_fd = open(self.file_path, 'w', newline='', encoding='utf-8')
            csv_writer = csv.writer(file_fd)
            csv_writer.writerow(HEADERS)
            return csv_writer


def collect_stats(cont_stats: DockerStats):
    socket_connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    socket_connection.connect(SOCKET_PATH)
    socket_connection.settimeout(1.25)
    conn_string = cont_stats.connection_string
    csv_writer = cont_stats.file_descriptor
    
    while True:

        socket_connection.send(conn_string)
        complete_string = b""

        while True:
            try:
                response_data = socket_connection.recv(4096)
                if b'\r\n\r\n' in response_data:
                    complete_string = complete_string + response_data
                    break
                complete_string = complete_string + response_data
            except socket.timeout:
                break
                
        print(complete_string)
        # for i in range(2):
        #     response_data = socket_connection.recv(4096)
        #     complete_string = complete_string + response_data
        #     # content_lines = response_data.decode().split('\r\n')
        #     print(complete_string)

        # print(complete_string)
        
        content_lines = complete_string.decode().split('\r\n')
        # print(content_lines)
        version_dict = json.loads(content_lines[10])
        
        timestamp = version_dict['read']
        
        # Computing the memory use percentage

        used_memory = version_dict['memory_stats']['usage'] - version_dict['memory_stats']['stats']['cache']
        available_memory = version_dict['memory_stats']['limit']
        mem_percentage = (used_memory / available_memory) * 100

        # Computing the CPU use percentage

        cpu_delta = version_dict["cpu_stats"]["cpu_usage"]["total_usage"] - version_dict["precpu_stats"]["cpu_usage"]["total_usage"]
        system_cpu_delta = version_dict["cpu_stats"]["system_cpu_usage"] - version_dict["precpu_stats"]["system_cpu_usage"]
        number_cpus = version_dict["cpu_stats"]["online_cpus"]
        cpu_percentage = (cpu_delta / system_cpu_delta) * number_cpus * 100

        # PID Stats 

        num_pid = version_dict["pids_stats"]["current"]
        csv_writer.writerow([timestamp, mem_percentage, cpu_percentage, num_pid])
        time.sleep(1)
        

if __name__ == "__main__":
    container_name = 'mlinfer-nb'
    file_name = './dataset/mlinfer-nb_eg.csv'
    container_stats = DockerStats(container_name=container_name, file_path=file_name)

    collect_stats(container_stats)