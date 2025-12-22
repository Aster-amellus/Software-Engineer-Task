"""initial tables"""
from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String, nullable=False, unique=True),
        sa.Column("password_hash", sa.String, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("last_login", sa.DateTime, nullable=True),
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("topic", sa.String, nullable=False),
        sa.Column("keywords", sa.JSON, nullable=True),
        sa.Column("status", sa.String, default="queued"),
        sa.Column("stage", sa.String, default="KEYWORD_EXPAND"),
        sa.Column("progress", sa.Integer, default=0),
        sa.Column("config", sa.JSON, nullable=True),
        sa.Column("report_markdown", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "papers",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("arxiv_id", sa.String, nullable=False),
        sa.Column("title", sa.String, nullable=True),
        sa.Column("authors", sa.JSON, nullable=True),
        sa.Column("abstract", sa.Text, nullable=True),
        sa.Column("categories", sa.JSON, nullable=True),
        sa.Column("published_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
        sa.Column("pdf_url", sa.String, nullable=True),
        sa.Column("local_path", sa.String, nullable=True),
        sa.Column("download_status", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.UniqueConstraint("project_id", "arxiv_id", name="uq_project_arxiv"),
    )

    op.create_table(
        "analyses",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("paper_id", sa.Integer, sa.ForeignKey("papers.id"), nullable=False),
        sa.Column("schema_version", sa.String, nullable=True),
        sa.Column("extracted", sa.JSON, nullable=True),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("token_cost", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "exports",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("format", sa.String, nullable=True),
        sa.Column("local_path", sa.String, nullable=True),
        sa.Column("status", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
    )


def downgrade():
    op.drop_table("exports")
    op.drop_table("analyses")
    op.drop_table("papers")
    op.drop_table("projects")
    op.drop_table("users")
