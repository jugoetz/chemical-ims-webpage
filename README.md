Additional configuration during installation:

- Set up a crontab to run the update from Expereact every 3 h. A convenience script is provided in `utilities/`.
Open the user's cronjobs with `crontab -e`, then add this line:
```shell
0 */3 * * * ./<path_to_project_root>/utilities/inventory_update.sh
```

- Set up a daily database backup. 
  A convenience script is provided in `utilities/`. 
  Ensure you have a director `backup/` in your project root.
  Open the user's cronjobs with `crontab -e`, then add this line:
```shell
0 1 * * * ./<path_to_project_root>/utilities/database_backup.sh
```
