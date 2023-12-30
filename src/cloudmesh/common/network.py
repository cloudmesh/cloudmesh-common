import socket


class PortGenerator:
    class PortGenerator:
        def __init__(self, base_port):
            """
            Initializes a PortGenerator object.

            Parameters:
            - base_port (int): The starting port number.

            Attributes:
            - base_port (int): The starting port number.
            - last (int): The last generated port number.
            """
            self.base_port = base_port

    def is_port_available(self, port):
        """
        Check if a given port is available in use.

        Parameters:
        - port (int): The port number to check.

        Returns:
        - bool: True if the port is available, False otherwise.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        if result == 0:
            print(f"Port {port} is in use")
            return False
        else:
            print(f"Port {port} is available")
            return True

    def get_port(self, port=None, n=100):
        """
        Returns an available port within a specified range starting from a port if specified.
        If not specified we will search from the base port

        Args:
            port (int, optional): The starting port number. If not provided, the base port will be used.
            n (int, optional): The number of ports to check for availability.

        Returns:
            int: An available port number.

        Raises:
            Exception: If no available port is found within the specified range.
        """
        port = self.port if port is None else port
        for i in range(0, n):
            if self.is_port_available(port):
                return port
            port += 1
        raise Exception(f"Could not find available port in range {self.last} - {port}")

