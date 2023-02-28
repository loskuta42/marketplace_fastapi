"""01_initial-db

Revision ID: a3f3c396221e
Revises: 576ed5079bb7
Create Date: 2023-02-17 13:41:50.135999

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a3f3c396221e'
down_revision = '576ed5079bb7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_files_created_at', table_name='files')
    op.drop_index('ix_files_user_id', table_name='files')
    op.drop_table('files')
    op.drop_index('ix_users_created_at', table_name='users')
    op.drop_table('users')
    op.drop_table('directories')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('directories',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('path', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='directories_pkey'),
    sa.UniqueConstraint('path', name='directories_path_key')
    )
    op.create_table('users',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('username', sa.VARCHAR(length=125), autoincrement=False, nullable=False),
    sa.Column('hashed_password', sa.VARCHAR(length=125), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='users_pkey'),
    sa.UniqueConstraint('username', name='users_username_key'),
    postgresql_ignore_search_path=False
    )
    op.create_index('ix_users_created_at', 'users', ['created_at'], unique=False)
    op.create_table('files',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=125), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('path', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('size', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('is_downloadable', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='files_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='files_pkey'),
    sa.UniqueConstraint('path', name='files_path_key')
    )
    op.create_index('ix_files_user_id', 'files', ['user_id'], unique=False)
    op.create_index('ix_files_created_at', 'files', ['created_at'], unique=False)
    # ### end Alembic commands ###