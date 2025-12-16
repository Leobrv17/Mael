import asyncio
from time import sleep

from sqlalchemy import select

from app.models.kanban import KanbanColumn
from app.models.ticket import TicketTimeSegment


def test_time_tracking_segments(client, db_session, event_loop):
    async def _run():
        headers = {"Authorization": "Bearer test-token"}
        org_resp = client.post("/api/v1/organizations/", json={"name": "Acme"}, headers=headers)
        assert org_resp.status_code == 200
        org_id = org_resp.json()["id"]

        project_resp = client.post(
            "/api/v1/projects/",
            json={"name": "Proj", "organization_id": org_id},
            headers=headers,
        )
        project_id = project_resp.json()["id"]

        to_do = KanbanColumn(project_id=project_id, name="TO_DO", position=1)
        in_progress = KanbanColumn(project_id=project_id, name="IN_PROGRESS", position=2)
        done = KanbanColumn(project_id=project_id, name="DONE", position=3)
        db_session.add_all([to_do, in_progress, done])
        await db_session.commit()
        await db_session.refresh(to_do)
        await db_session.refresh(in_progress)
        await db_session.refresh(done)

        ticket_resp = client.post(
            "/api/v1/tickets/",
            json={
                "project_id": project_id,
                "title": "Test",
                "column_id": to_do.id,
                "priority": "MEDIUM",
            },
            headers=headers,
        )
        ticket_id = ticket_resp.json()["id"]

        move_resp = client.post(
            f"/api/v1/tickets/{ticket_id}/move",
            json={"column_id": in_progress.id},
            headers=headers,
        )
        assert move_resp.status_code == 200

        move_resp = client.post(
            f"/api/v1/tickets/{ticket_id}/move",
            json={"column_id": done.id},
            headers=headers,
        )
        assert move_resp.status_code == 200

        segments = await db_session.scalars(
            select(TicketTimeSegment).where(TicketTimeSegment.ticket_id == ticket_id)
        )
        seg_list = list(segments)
        assert len(seg_list) == 1
        assert seg_list[0].ended_at is not None

    event_loop.run_until_complete(_run())
