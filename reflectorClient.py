###############################################################################
#
#Copyright (c) (2018) Cisco Systems, Inc.
#Name: reflectorClient.py
#Purpose: Verifies whether ports for QoS or non-QoS or custom port range are
# open. This tool can be used before turning on QoS to identify and open blocked
# ports. Each run will display a summary at the end.
#Author: Eshak Tadipatri
#References:
#Description:
#Topology:
#Synopsis:
#Arguments:
#Sample Usage: Please use `--help` command line option.
#Pass/Fail Criteria:
#Sample Output:
#Test Steps:
#Notes:
#Known Bugs:
#Todo:
#See Also:
#End of Header:
###############################################################################

import socket
import sys
import getopt
import random
from time import sleep

success_port_list = []
failed_port_list = []

# +1 at the end to make the port inclusive.
non_qos_udp_ports_list = [5004] + list(range(34000, 34999+1))
non_qos_tcp_ports_list = [5004, 5060, 5061]

qos_udp_ports_list = [5004] + list(range(52500, 59499+1)) + \
    list(range(63000, 64667+1)) + list(range(10001, 13747+1)) + \
    list(range(25001, 27997+1)) + list(range(13750, 17498+1)) + \
    list(range(28000, 30998+1)) + list(range(17501, 21247+1)) + \
    list(range(31001, 33997+1))
qos_tcp_ports_list = [5004, 5060, 5061, 33432, 33433]

verify_port_list = []


def usage():
    print("""Usage:
      --ip and --protocol are mandatory.
      If start-port is specified, end-port is considered mandatory. If no starting port is specified, default ports are verified for connectivity.
      By default, tool checks for QoS ports unless --non-qos option is specified.
      Default QoS ports include: TCP - 5004, 5060, 5061 and UDP - 5004, 52500-59499 and 63000-64667.
      Default non QoS ports include: TCP - 5004, 5060, 5061 and UDP - 5004, 34000-34999.
      To verify single port, both start and end port should be the required port to verify.
      Examples:
      Below run is to verify non-qos ports using an input port range:
        python reflectorClient.py --ip <hmn-ip-address> --protocol <udp/tcp> --start-port 52000 --end-port 52501 --non-qos
      Below run in to verify default qos ports:
        python reflectorClient.py --ip <> --protocol <udp/tcp>""")


def verify_port_using_sockets(host, protocol, port, retry=False):

    global success_port_list
    global failed_port_list

    try:
        if protocol == "udp":
            # Create a UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # specifying 0 as port allows OS to pick an available port to bind the socket
            sock.bind(('0.0.0.0', 0))
            sock.settimeout(1)

            server_address = (host, port)
            # Send data
            _ = sock.sendto(str(port).encode(), server_address)

            # Receive response
            data, server = sock.recvfrom(4096)
            sock.close()
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('0.0.0.0', 0))
            sock.settimeout(1)
            server_address = (host, port)
            sock.connect(server_address)
            sock.sendall(str(port).encode())
            data = sock.recv(4096)
            sock.close()

        success_port_list.append(port)

        if retry and port in failed_port_list:
            failed_port_list.remove(port)

        return
    except socket.error:
        if port not in failed_port_list:
            failed_port_list.append(port)
        return


def show_progress(curr_value, total_values):
    # show something like:
    # $ Verifying ports: [---->       ] 40% - curr_value/total_values

    progress_bar_len = 30
    progress_percent = float(curr_value) / total_values
    progress_dashes = '-' * \
        int(round(progress_percent * progress_bar_len)-1) + '>'
    progress_remaining_spaces = ' ' * (progress_bar_len - len(progress_dashes))
    sys.stdout.write("\r [{}] {:.2f}%  Success/Failed/Total: {}/{}/{}".format(progress_dashes + progress_remaining_spaces,
                                                                              (progress_percent * 100), len(success_port_list), len(failed_port_list), total_values))
    sys.stdout.flush()

# Will return the output list by consolidating ranges in the given port list.
# Example: if input is [1,2,3,4,5] then output is [1-5]


def get_consolidated_list(input_port_list):
    output_list = []

    if len(input_port_list) == 0:
        return input_port_list
    else:
        prev = -10
        start_port = -11
        end_port = -12

        for curr in input_port_list:
            curr_port = int(curr)

            if curr_port - 1 == prev:
                # then it can be represented as range
                end_port = curr_port
            else:
                if start_port != end_port and end_port > start_port:
                    output_list.append(str(start_port) + "-" + str(end_port))
                elif end_port == -12 and start_port != -11:  # this is solo port
                    output_list.append(str(prev))

                # Reset the values
                start_port = -11
                end_port = -12

                # Set the starting point again.
                start_port = curr_port

            prev = curr_port

        # Handle last port
        if start_port != end_port and end_port > start_port:
            output_list.append(str(start_port) + "-" + str(end_port))
        else:
            output_list.append(str(prev))

        return output_list


def main(argv):

    global success_port_list
    global failed_port_list

    global verify_port_list

    remote_host = ''
    remote_port = ''
    protocol = ''

    start_port = -1
    end_port = -1
    default_ports = False

    retry_count = 4
    sleep_before_retry = 10

    qos_enabled = True

    try:
        # --hmn-ip
        # --protocol
        # --start-port
        # --end-port
        # --help
        opts, args = getopt.getopt(
            argv, "", ["ip=", "protocol=", "start-port=", "end-port=", "help", "non-qos"])

        if len(opts) == 0:
            usage()
            sys.exit(1)

        for opt, arg in opts:
            if opt in ("--ip"):
                remote_host = arg
            elif opt in ("--protocol"):
                protocol = arg
            elif opt in ("--start-port"):
                start_port = int(arg)
                if start_port < 0:
                    print(
                        "ERROR: Invalid --start-port number: {}. Please specify ports in 0-65535.".format(start_port))
                    print("Exiting Reflector Client tool...")
                    sys.exit(1)
            elif opt in ("--end-port"):
                end_port = int(arg)
                if end_port > 65535:
                    print(
                        "ERROR: Invalid --end-port number: {}. Please specify ports in 0-65535.".format(end_port))
                    print("Exiting Reflector Client tool...")
                    sys.exit(1)
            elif opt in ("--non-qos"):
                qos_enabled = False
                print("Starting Reflector Client in non-qos mode...")
            else:
                usage()
                sys.exit(1)

        if protocol == '' or remote_host == '':
            usage()
            sys.exit(1)

        if start_port != -1 and (end_port == -1 or end_port < start_port):
            usage()
            sys.exit(1)

        if qos_enabled:
            if protocol == "udp":
                verify_port_list = qos_udp_ports_list
            else:
                verify_port_list = qos_tcp_ports_list
        else:
            if protocol == "udp":
                verify_port_list = non_qos_udp_ports_list
            else:
                verify_port_list = non_qos_tcp_ports_list

        curr_port_index = 1
        total_num_of_ports = 0
        if start_port == -1 and end_port == -1:
            default_ports = True
            total_num_of_ports = len(verify_port_list)
            print("Please wait while verifying {} for ports: {} ...".format(
                protocol, get_consolidated_list(verify_port_list)))
            for remote_port in verify_port_list:
                verify_port_using_sockets(remote_host, protocol, remote_port)
                show_progress(curr_port_index, total_num_of_ports)
                curr_port_index += 1
                #sleep(0.05)
        else:
            # +1 to include last port.
            total_num_of_ports = len(range(start_port, end_port+1))
            print("Please wait while verifying {} for port range: {} - {} ...".format(
                protocol, start_port, end_port))
            # +1 to include last port.
            for remote_port in range(start_port, end_port+1):
                verify_port_using_sockets(remote_host, protocol, remote_port)
                show_progress(curr_port_index, total_num_of_ports)
                curr_port_index += 1

        print("\n")

        if len(failed_port_list) != 0:
            print("Failed ports in the first try: "), get_consolidated_list(
                failed_port_list)
            print("Retrying({} times) the above failed ports: ".format(retry_count))

        curr_retry_num = 0
        while len(failed_port_list) != 0 and curr_retry_num < retry_count:
            curr_retry_num += 1
            print("Retry number {}:".format(curr_retry_num))

            sleep(sleep_before_retry)
            for remote_port in failed_port_list:
                print("   Verifying port -> {}".format(remote_port))
                verify_port_using_sockets(
                    remote_host, protocol, remote_port, retry=True)

        print("###########################")
        if len(failed_port_list) != 0:
            print("Ports which are not open for {} are: {}".format(
                protocol, get_consolidated_list(failed_port_list)))
        else:
            if default_ports:
                print("No ports are blocked for {} in {}".format(
                    protocol, get_consolidated_list(verify_port_list)))
            else:
                print(
                    "No ports are blocked for {} in {}-{}".format(protocol, start_port, end_port))
        print("###########################")

        print("Exiting Reflector Client tool...")

        sys.exit(0)
    except getopt.GetoptError as e:
        print("Error: {}".format(e))
        usage()
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n Exiting Reflector Client... \n")
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
