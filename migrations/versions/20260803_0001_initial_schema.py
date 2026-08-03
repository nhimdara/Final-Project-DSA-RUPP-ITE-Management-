"""Create initial student management tables."""

from alembic import op
import sqlalchemy as sa

revision = "20260803_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("courses", sa.Column("code", sa.String(20), primary_key=True),
                    sa.Column("name", sa.String(120), nullable=False),
                    sa.Column("credits", sa.Integer(), nullable=False))
    op.create_index("ix_courses_name", "courses", ["name"])
    op.create_table("students", sa.Column("student_id", sa.String(20), primary_key=True),
                    sa.Column("name", sa.String(120), nullable=False),
                    sa.Column("department", sa.String(120), nullable=False),
                    sa.Column("year", sa.Integer(), nullable=False))
    op.create_index("ix_students_name", "students", ["name"])
    op.create_table("users", sa.Column("username", sa.String(50), primary_key=True),
                    sa.Column("password_hash", sa.String(255), nullable=False),
                    sa.Column("role", sa.String(30), nullable=False),
                    sa.Column("student_id", sa.String(20), nullable=True))
    op.create_table(
        "enrollments",
        sa.Column("student_id", sa.String(20), sa.ForeignKey("students.student_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("course_code", sa.String(20), sa.ForeignKey("courses.code", ondelete="CASCADE"), primary_key=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.CheckConstraint("score >= 0 AND score <= 100", name="valid_score"),
    )


def downgrade() -> None:
    op.drop_table("enrollments")
    op.drop_table("users")
    op.drop_index("ix_students_name", table_name="students")
    op.drop_table("students")
    op.drop_index("ix_courses_name", table_name="courses")
    op.drop_table("courses")
