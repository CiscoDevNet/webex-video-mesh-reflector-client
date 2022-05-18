## Verify Video Mesh Node Port Ranges With Reflector Tool in the Web Interface
The reflector tool (a combination of a server on the Video Mesh node and client through a Python script) is used to verify whether the required TCP/UDP ports are open from Video Mesh nodes.

Before you begin

Download a copy of the Reflector Tool Client (Python script).

For the script to work properly, ensure that you're running Python 2.7.10 or later in your environment.

Currently, this tool supports SIP endpoints to Video Mesh nodes and intracluster verification.

## Procedure
Step 1	From the customer view in https://admin.webex.com, enable maintenance node for the Video Mesh Node as described in https://help.webex.com/article/nxep7tb/Move-a-Cloud-Registered-Node-in-to-Maintenance-Mode.

Step 2 Wait for the node to show a 'Ready for maintenance' status in Control Hub.

Step 3 Open the Webex Video Mesh node interface.

For instructions, see https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cloudCollaboration/wbxt/videomesh/cmgt_b_webex-video-mesh-deployment-guide/cmgt_b_hybrid-media-deployment-guide_chapter_0100.html#id_108616.

Step 4	Scroll to Reflector Tool, and then start either the TCP Reflector Server or UDP Reflector Server, depending on what protocol you want to use.

Step 5	Click Start Reflector Server, and then wait for the server to start successfully.

You'll see a notice when the server starts.

Step 6	From a system (such as a PC) on a network that you want Video Mesh nodes to reach, run the script with the following command:

$ python <local_path_to_client_script>/reflectorClient.py --ip <ip address of the server> --protocol <tcp or udp>
At the end of the run, the client shows a success message if all the required ports are open:
  
<img width="766" alt="Screenshot 2022-05-17 at 12 35 45 AM" src="https://user-images.githubusercontent.com/104610885/168664464-41e00185-ae1f-47fc-98ca-9fcab2aa3586.png">

Step 7	Resolve any port issues on the firewall and then rerun the above steps.

Step 8	Run the client with --help to get more details.
  
 <img width="759" alt="Screenshot 2022-05-17 at 12 37 44 AM" src="https://user-images.githubusercontent.com/104610885/168664649-d3cae450-9a15-4e59-a00d-d8d7c4d97209.png">
