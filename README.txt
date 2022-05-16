# Reflector Tool

## How to run

### Server
1. Enable maintenance node on the VMN (https://help.webex.com/en-us/nxep7tb/Move-a-Cloud-Registered-Node-in-to-Maintenance-Mode)
2. Enable reflector server from the VMN Web UI Trobuleshooting page (https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cloudCollaboration/wbxt/videomesh/cmgt_b_webex-video-mesh-deployment-guide/cmgt_b_hybrid-media-deployment-guide_chapter_0100.html#id_116218)
3. Wait for the server to start successfully.

### Client
1. Download the reflector tool client (https://github.com/CiscoDevNet/webex-video-mesh-reflector-client)
2. Ensure that python 2.7.10 or above is available in the enviroment.
3. Run the client script using:
```
$ python <path_to_client_script>/reflectorClient.py --ip <ip address of the server> --protocol <tcp or udp>
```
4. Please run client with --help to get more details.


