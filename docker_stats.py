import socket
import json
import time

class DockerStats(object):

    def __init__(self, container_name):
        self.container_name = container_name
        self.raw_stats = None
        self.cpu_usage = None
        self.pid = None
        self.memory_usage = None
        self.collected_at = None
        self.file_name = None

    def collect_stats(self):
        socket_path = '/var/run/docker.sock'
        socket_connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        socket_connection.connect(socket_path)

        connection_string = f"GET http://localhost/containers/{self.container_name}/stats?stream=False HTTP/1.1\r\nHost: *\r\n\r\n".encode()

        while True:

            socket_connection.send(connection_string)

            response_data = socket_connection.recv(10000)
            content_lines = response_data.decode().split('\r\n')
            print(content_lines[10])
            version_dict = json.loads(content_lines[10])
            out_files = open('example.json', 'w')
            json.dump(version_dict, out_files)
            # print(response_data)
            time.sleep(1)
        # version_dict = json.loads(content_lines[])
        # print(version_dict)
        

if __name__ == "__main__":
    container_name = 'echoservice-ttd'

    container_stats = DockerStats(container_name)

    container_stats.collect_stats()
