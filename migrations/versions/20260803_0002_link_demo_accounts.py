"""Link demo student and parent accounts to S001."""

from alembic import op

revision = "20260803_0002"
down_revision = "20260803_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE users SET student_id = 'S001' WHERE username IN ('student', 'parent') AND student_id IS NULL")


def downgrade() -> None:
    op.execute("UPDATE users SET student_id = NULL WHERE username IN ('student', 'parent') AND student_id = 'S001'")
