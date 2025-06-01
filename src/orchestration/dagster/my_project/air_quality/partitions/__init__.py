"""
An asset definition can represent a collection of partitions
that can be tracked and materialized independently.
In many ways, each partition functions like its own mini-asset,
but they all share a common materialization function and dependencies.
Typically, each partition will correspond to a separate file,
or a slice of a table in a database.
"""
