"""
Sensors are definitions in Dagster that allow you to instigate runs
based on some external state change.
For example, you can:

 - Launch a run whenever a file appears in an s3 bucket
 - Launch a run whenever another job materializes a specific asset
 - Launch a run whenever an external system is down
"""
