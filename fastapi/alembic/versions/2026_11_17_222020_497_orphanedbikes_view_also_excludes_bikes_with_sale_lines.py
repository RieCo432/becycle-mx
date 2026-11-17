"""#497 orphanedbikes view also excludes bikes with sale lines

Revision ID: 707389612f50
Revises: 5f8c2d91a3b7
Create Date: 2026-11-17 22:20:20.970431+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '707389612f50'
down_revision: Union[str, None] = '5f8c2d91a3b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # A bike with a sale line is not orphaned: deleting it would violate the
    # bikesalelines_bikeid_fkey constraint (no ON DELETE CASCADE), and the
    # recurring orphan-bike cull must never take out a bike that has been sold.
    op.execute("""CREATE OR REPLACE VIEW orphanedbikes AS SELECT b.id
      FROM bikes b
               LEFT JOIN (
                   SELECT count(con.id) num
                        ,con.bikeid
                   FROM contracts con
                   GROUP BY con.bikeid
               ) concounts ON concounts.bikeid = b.id
               LEFT JOIN (
                   SELECT count(sl.id) num
                        ,sl.bikeid
                   FROM bikesalelines sl
                   GROUP BY sl.bikeid
               ) slcounts ON slcounts.bikeid = b.id
      WHERE
          concounts.num IS NULL AND
          slcounts.num IS NULL;""")


def downgrade() -> None:
    # Restore the previous definition (contracts only).
    op.execute("""CREATE OR REPLACE VIEW orphanedbikes AS SELECT b.id
      FROM bikes b
               LEFT JOIN (
                   SELECT count(con.id) num
                        ,con.bikeid
                   FROM contracts con
                   GROUP BY con.bikeid
               ) concounts ON concounts.bikeid = b.id
      WHERE
          concounts.num IS NULL;""")
