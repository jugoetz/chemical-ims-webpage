"""
Utility script that has to be executed on a machine with access to Expereact.
Connects to https://expereact.ethz.ch to download a list of all chemicals in the system, then uses scp to transfer the
list to the production server (that cannot access Expereact)
"""
import requests
import os
import lxml.html as lh
from pathlib import Path
import paramiko
from scp import SCPClient


def parse_expereact(path, local):
    """
    Download a list of all chemicals from expereact,
    parse the html table inside there and return a variable holding the parsed data
    :param local: set to True to avoid reloading expereact data (takes some 20 seconds)
    :type local: bool
    """
    # fetch expereact export
    if local is False:
        source_url = "https://expereact.ethz.ch/searchstock?for=chemexper&bl=1000000&so=Field10.15&search=+AND" \
                     "+Field10.15%3D%2225%22&for=report&mime_type=application/vnd.ms-excel "
        file = requests.get(source_url)  # source url from outer scope
        with open(path, 'wb') as newfile:
            newfile.write(file.content)  # download to local file
            # (intermediate download to local file is necessary for reliable parsing)
    with open(path, 'rb') as file:  # load local file
        # Parse html into variable doc
        doc = lh.parse(file)
    # extract table contents and return
    return doc.xpath('//tr')


def upload_data(path):
    def createSSHClient(server, port, user, password):
        """taken from https://stackoverflow.com/questions/250283/how-to-scp-in-python"""
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(server, port, user, password)
        return client

    password = os.environ.get('SSH_PASSPHRASE')
    ssh = createSSHClient(server='cbs.ethz.ch', port=22, user='w3_cbs', password=password)
    scp = SCPClient(ssh.get_transport())
    scp.put(path, remote_path=r'/instances/home/cbs/webapps/django-chem-ims/chemical-ims-webpage/inventorymanagement/')
    return


def main():
    data_path = Path('../inventorymanagement/expereact_source.dat')
    # _ = parse_expereact(path=data_path, local=False)
    upload_data(path=data_path)


if __name__ == '__main__':
    main()
