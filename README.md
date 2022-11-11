This branch has only the utilities needed to update the inventory and is designed to be used with machines
that have access to expereact.ethz.ch (staff-net/chem-org) and ssh access to cbs.ethz.ch


Additional configuration during installation:

Needs a virtual environment containing
- python3
- paramiko (needs the Rust compiler for installation)
- scp
- lxml

Set up a crontab to run the update from Expereact every 3 h. **This consists of two parts on two different machines**
Machine A needs access to the expereact server. Machine B is the production machine.

On machine A, set up a cronjob to run the script `utilities/inventory_download.sh`.
Open the user's cronjobs with `crontab -e`, then add this line:
```shell
0 */3 * * * /bin/bash ./<path_to_project_root>/utilities/inventory_download.sh
```
In addition, machine A needs to hold an SSH key that allows connection to machine B and
the environment_variable `SSH_PASSPHRASE` must be set to the passphrase of the key 
(n.b. env variables for cron need to be set inside crontab).
