Additional configuration during installation:


Set up a daily database backup. 
  A convenience script is provided in `utilities/`. 
  Ensure you have a directory `backup/` in your project root.
  Open the user's cronjobs with `crontab -e`, then add this line:
```shell
0 1 * * * ./<path_to_project_root>/utilities/database_backup.sh
```
------------
Set up a crontab to run the update from Expereact every 3 h. **This consists of two parts on two different machines**
Machine A needs access to the expereact server. Machine B is the production machine.

On machine A, set up a cronjob to run the script `utilities/inventory_download.sh`.
Open the user's cronjobs with `crontab -e`, then add this line:
```shell
0 */3 * * * ./<path_to_project_root>/utilities/inventory_download.sh
```
In addition, machine A needs to hold an SSH key that allows connection to machine B and
the environment_variable `SSH_PASSPHRASE` must be set to the passphrase of the key.

On machine B, set up a cronjob to run the convenience script `utilities/inventory_update.sh`.
Open the user's cronjobs with `crontab -e`, then add this line:
```shell
30 */3 * * * ./<path_to_project_root>/utilities/inventory_update.sh
```