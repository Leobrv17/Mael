"""initial tables"""

from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("e_invoicing_required_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("firebase_uid", sa.String(length=255), nullable=False, unique=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("name", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("is_active", sa.Boolean, default=True),
    )
    op.create_table(
        "org_memberships",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("role", sa.Enum("OWNER", "ADMIN", "MEMBER", "CLIENT", name="globalrole")),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("name", sa.String(length=255)),
        sa.Column("description", sa.String(length=500)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "project_memberships",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id", ondelete="CASCADE")),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column(
            "role",
            sa.Enum(
                "PROJECT_OWNER",
                "MAINTAINER",
                "CONTRIBUTOR",
                "REPORTER",
                "VIEWER",
                name="projectrole",
            ),
        ),
    )
    op.create_table(
        "kanban_columns",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id", ondelete="CASCADE")),
        sa.Column("name", sa.String(length=100)),
        sa.Column("position", sa.Integer),
        sa.Column("is_default", sa.Boolean, default=False),
    )
    op.create_table(
        "sprints",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id", ondelete="CASCADE")),
        sa.Column("name", sa.String(length=255)),
        sa.Column("goal", sa.String(length=500)),
        sa.Column("start_date", sa.DateTime(timezone=True)),
        sa.Column("end_date", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id", ondelete="CASCADE")),
        sa.Column("sprint_id", sa.Integer, sa.ForeignKey("sprints.id")),
        sa.Column("column_id", sa.Integer, sa.ForeignKey("kanban_columns.id")),
        sa.Column("title", sa.String(length=255)),
        sa.Column("description", sa.Text()),
        sa.Column("priority", sa.Enum("LOW", "MEDIUM", "HIGH", "CRITICAL", name="priority")),
        sa.Column("estimation_minutes", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "ticket_assignees",
        sa.Column("ticket_id", sa.Integer, sa.ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    )
    op.create_table(
        "ticket_comments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ticket_id", sa.Integer, sa.ForeignKey("tickets.id", ondelete="CASCADE")),
        sa.Column("author_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("body", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "ticket_time_segments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ticket_id", sa.Integer, sa.ForeignKey("tickets.id", ondelete="CASCADE")),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ticket_id", sa.Integer, sa.ForeignKey("tickets.id", ondelete="CASCADE")),
        sa.Column("action", sa.String(length=255)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("actor_id", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("details", sa.Text()),
    )
    op.create_table(
        "notification_preferences",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("channel", sa.Enum("IN_APP", "EMAIL", name="notificationchannel")),
        sa.Column("enabled", sa.Boolean, default=True),
    )
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("title", sa.String(length=255)),
        sa.Column("body", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("read", sa.Boolean, default=False),
    )
    op.create_table(
        "quotes",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("number", sa.String(length=50)),
        sa.Column("title", sa.String(length=255)),
        sa.Column("status", sa.Enum("DRAFT", "ACCEPTED", "CONVERTED", name="quotestatus")),
        sa.Column("valid_until", sa.DateTime(timezone=True)),
        sa.Column("accepted_at", sa.DateTime(timezone=True)),
        sa.Column("accepted_by_ip", sa.String(length=64)),
        sa.Column("accepted_by_user", sa.Integer, sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "quote_lines",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("quote_id", sa.Integer, sa.ForeignKey("quotes.id", ondelete="CASCADE")),
        sa.Column("description", sa.Text()),
        sa.Column("quantity", sa.Integer),
        sa.Column("unit_price", sa.Numeric(10, 2)),
    )
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id", ondelete="CASCADE")),
        sa.Column("number", sa.String(length=50)),
        sa.Column("status", sa.Enum("DRAFT", "ISSUED", "LOCKED", name="invoicestatus")),
        sa.Column("title", sa.String(length=255)),
        sa.Column("issue_date", sa.DateTime(timezone=True)),
        sa.Column("locked", sa.Boolean, default=False),
        sa.Column("legal_mentions", sa.Text()),
        sa.Column("pdf_checksum", sa.String(length=128)),
        sa.Column("pdf_content_type", sa.String(length=64)),
        sa.Column("pdf_blob", sa.LargeBinary()),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "invoice_lines",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("invoice_id", sa.Integer, sa.ForeignKey("invoices.id", ondelete="CASCADE")),
        sa.Column("description", sa.Text()),
        sa.Column("quantity", sa.Integer),
        sa.Column("unit_price", sa.Numeric(10, 2)),
    )
    op.create_table(
        "agenda_events",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column("project_id", sa.Integer, sa.ForeignKey("projects.id", ondelete="CASCADE")),
        sa.Column("type", sa.Enum("MEETING", "TASK", "REMINDER", name="agendaeventtype")),
        sa.Column("title", sa.String(length=255)),
        sa.Column("description", sa.Text()),
        sa.Column("start_at", sa.DateTime(timezone=True)),
        sa.Column("end_at", sa.DateTime(timezone=True)),
    )
    op.create_table(
        "email_outbox",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("recipient", sa.String(length=255)),
        sa.Column("subject", sa.String(length=255)),
        sa.Column("body", sa.Text()),
        sa.Column("status", sa.Enum("PENDING", "SENT", "FAILED", name="emailstatus")),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("last_error", sa.Text()),
    )



def downgrade() -> None:
    for table in [
        "email_outbox",
        "agenda_events",
        "invoice_lines",
        "invoices",
        "quote_lines",
        "quotes",
        "notifications",
        "notification_preferences",
        "events",
        "ticket_time_segments",
        "ticket_comments",
        "ticket_assignees",
        "tickets",
        "sprints",
        "kanban_columns",
        "project_memberships",
        "projects",
        "org_memberships",
        "users",
        "organizations",
    ]:
        op.drop_table(table)
