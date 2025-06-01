"""
SQLAlchemy model utility functions and classes.
"""

# SQLAlchemy imports
from sqlalchemy import (
    asc,
    desc,
)
from sqlalchemy.orm import Query


class DefaultOrderQuery(Query):
    """
    Custom Query class to apply default ordering to queries.
    """

    def __init__(self, entities, session=None):
        super().__init__(entities, session)
        if entities:
            entity = entities[0]
            if hasattr(entity, "class_") and hasattr(
                entity.class_, "__default_order_by__"
            ):
                order_by_clauses = []

                for (
                    column_name,
                    direction,
                ) in entity.class_.__default_order_by__.items():
                    column_attr = getattr(entity.class_, column_name, None)

                    if column_attr is not None:
                        if direction.lower() == "asc":
                            order_by_clauses.append(asc(column_attr))
                        elif direction.lower() == "desc":
                            order_by_clauses.append(desc(column_attr))
                        else:
                            raise ValueError(
                                f"Invalid order direction '{direction}' for column '{column_name}'"
                            )

                # Apply all order_by clauses to the query
                if order_by_clauses:
                    self = self.order_by(*order_by_clauses)
