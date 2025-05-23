"""change

Revision ID: 4b6711515e58
Revises: 67431817031a
Create Date: 2025-05-09 16:04:32.771367

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b6711515e58'
down_revision: Union[str, None] = '67431817031a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tokens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('timeframe', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('percent_change_ema', sa.Float(), nullable=True))
        batch_op.drop_column('first_signal_price')
        batch_op.drop_column('pump_percent')
        batch_op.drop_column('pump_period')
        batch_op.drop_column('ema')
        batch_op.drop_column('sygnal_per_day')

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('tokens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sygnal_per_day', sa.INTEGER(), nullable=False))
        batch_op.add_column(sa.Column('ema', sa.FLOAT(), nullable=False))
        batch_op.add_column(sa.Column('pump_period', sa.INTEGER(), nullable=False))
        batch_op.add_column(sa.Column('pump_percent', sa.FLOAT(), nullable=False))
        batch_op.add_column(sa.Column('first_signal_price', sa.INTEGER(), nullable=True))
        batch_op.drop_column('percent_change_ema')
        batch_op.drop_column('timeframe')

    # ### end Alembic commands ###
