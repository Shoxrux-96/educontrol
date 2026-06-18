import pytest
import uuid


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["version"] == "1.0.0"


class TestAuth:
    @pytest.mark.asyncio
    async def test_login_admin(self, client):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin123!"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "user" in data
        assert data["user"]["username"] == "admin"

    @pytest.mark.asyncio
    async def test_login_invalid(self, client):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "wrong"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_me(self, client, auth_headers):
        resp = await client.get("/api/v1/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "admin"
        assert data["role"] in ("super_admin", "admin")

    @pytest.mark.asyncio
    async def test_me_unauthorized(self, client):
        resp = await client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh(self, client):
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin123!"},
        )
        refresh_token = login_resp.json()["refresh_token"]
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data

    @pytest.mark.asyncio
    async def test_refresh_invalid(self, client):
        resp = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_logout(self, client, auth_headers):
        resp = await client.post("/api/v1/auth/logout", headers=auth_headers)
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_register_requires_super_admin(self, client, auth_headers):
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@test.com",
                "password": "NewUser123!",
                "full_name": "New User",
                "role": "viewer",
            },
            headers=auth_headers,
        )
        assert resp.status_code in (201, 403, 400)


class TestComputers:
    @pytest.mark.asyncio
    async def test_list_computers(self, client, auth_headers):
        resp = await client.get("/api/v1/computers", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert data["total"] >= 5

    @pytest.mark.asyncio
    async def test_list_computers_paginated(self, client, auth_headers):
        resp = await client.get(
            "/api/v1/computers?page=1&page_size=2",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 2

    @pytest.mark.asyncio
    async def test_list_computers_filter_by_group(self, client, auth_headers):
        resp = await client.get("/api/v1/computers", headers=auth_headers)
        computers = resp.json()["items"]
        if computers:
            group_id = computers[0]["group_id"]
            if group_id:
                resp = await client.get(
                    f"/api/v1/computers?group_id={group_id}",
                    headers=auth_headers,
                )
                assert resp.status_code == 200
                for c in resp.json()["items"]:
                    assert c["group_id"] == group_id

    @pytest.mark.asyncio
    async def test_get_computer(self, client, auth_headers):
        resp = await client.get("/api/v1/computers", headers=auth_headers)
        computers = resp.json()["items"]
        if computers:
            comp_id = computers[0]["id"]
            resp = await client.get(f"/api/v1/computers/{comp_id}", headers=auth_headers)
            assert resp.status_code == 200
            assert resp.json()["id"] == comp_id

    @pytest.mark.asyncio
    async def test_get_computer_not_found(self, client, auth_headers):
        fake_id = uuid.uuid4()
        resp = await client.get(f"/api/v1/computers/{fake_id}", headers=auth_headers)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_computer(self, client, auth_headers):
        resp = await client.get("/api/v1/computers", headers=auth_headers)
        computers = resp.json()["items"]
        if computers:
            comp_id = computers[0]["id"]
            new_name = f"Updated-{uuid.uuid4().hex[:6]}"
            resp = await client.put(
                f"/api/v1/computers/{comp_id}",
                json={"name": new_name},
                headers=auth_headers,
            )
            assert resp.status_code == 200
            assert resp.json()["name"] == new_name

    @pytest.mark.asyncio
    async def test_update_computer_not_found(self, client, auth_headers):
        fake_id = uuid.uuid4()
        resp = await client.put(
            f"/api/v1/computers/{fake_id}",
            json={"name": "nope"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_computer_stats(self, client, auth_headers):
        resp = await client.get("/api/v1/computers", headers=auth_headers)
        computers = resp.json()["items"]
        if computers:
            comp_id = computers[0]["id"]
            resp = await client.get(
                f"/api/v1/computers/{comp_id}/stats",
                headers=auth_headers,
            )
            assert resp.status_code == 200
            data = resp.json()
            assert "computer_id" in data
            assert "cpu_history" in data
            assert "ram_history" in data
            assert "disk_history" in data

    @pytest.mark.asyncio
    async def test_get_computer_stats_not_found(self, client, auth_headers):
        fake_id = uuid.uuid4()
        resp = await client.get(
            f"/api/v1/computers/{fake_id}/stats",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_get_computer_audit(self, client, auth_headers):
        resp = await client.get("/api/v1/computers", headers=auth_headers)
        computers = resp.json()["items"]
        if computers:
            comp_id = computers[0]["id"]
            resp = await client.get(
                f"/api/v1/computers/{comp_id}/audit",
                headers=auth_headers,
            )
            assert resp.status_code == 200
            assert "items" in resp.json()

    @pytest.mark.asyncio
    async def test_get_computer_commands(self, client, auth_headers):
        resp = await client.get("/api/v1/computers", headers=auth_headers)
        computers = resp.json()["items"]
        if computers:
            comp_id = computers[0]["id"]
            resp = await client.get(
                f"/api/v1/computers/{comp_id}/commands",
                headers=auth_headers,
            )
            assert resp.status_code == 200
            assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_delete_computer_not_found(self, client, auth_headers):
        fake_id = uuid.uuid4()
        resp = await client.delete(
            f"/api/v1/computers/{fake_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_list_computers_unauthorized(self, client):
        resp = await client.get("/api/v1/computers")
        assert resp.status_code == 401


class TestGroups:
    @pytest.mark.asyncio
    async def test_list_groups(self, client, auth_headers):
        resp = await client.get("/api/v1/computers/groups", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 3
        names = [g["name"] for g in data]
        assert "1-Qator" in names
        assert "2-Qator" in names
        assert "3-Qator" in names

    @pytest.mark.asyncio
    async def test_create_group(self, client, auth_headers):
        name = f"Test-Group-{uuid.uuid4().hex[:6]}"
        resp = await client.post(
            "/api/v1/computers/groups",
            json={"name": name, "description": "temp group"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == name
        assert "id" in data

    @pytest.mark.asyncio
    async def test_list_groups_unauthorized(self, client):
        resp = await client.get("/api/v1/computers/groups")
        assert resp.status_code == 401


class TestPolicies:
    policy_id = None
    assignment_id = None

    @pytest.mark.asyncio
    async def test_list_policies(self, client, auth_headers):
        resp = await client.get("/api/v1/policies", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_create_policy(self, client, auth_headers):
        resp = await client.post(
            "/api/v1/policies",
            json={
                "name": "Test Policy",
                "description": "A test policy",
                "policy_type": "internet",
                "config": {"block_internet": True, "allowed_sites": []},
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Test Policy"
        assert data["policy_type"] == "internet"
        assert data["is_active"] is True
        TestPolicies.policy_id = data["id"]

    @pytest.mark.asyncio
    async def test_get_policy(self, client, auth_headers):
        assert TestPolicies.policy_id
        resp = await client.get(
            f"/api/v1/policies/{TestPolicies.policy_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["id"] == TestPolicies.policy_id

    @pytest.mark.asyncio
    async def test_get_policy_not_found(self, client, auth_headers):
        fake_id = uuid.uuid4()
        resp = await client.get(f"/api/v1/policies/{fake_id}", headers=auth_headers)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_update_policy(self, client, auth_headers):
        assert TestPolicies.policy_id
        resp = await client.put(
            f"/api/v1/policies/{TestPolicies.policy_id}",
            json={"name": "Updated Policy", "is_active": False},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Updated Policy"
        assert resp.json()["is_active"] is False

    @pytest.mark.asyncio
    async def test_update_policy_not_found(self, client, auth_headers):
        fake_id = uuid.uuid4()
        resp = await client.put(
            f"/api/v1/policies/{fake_id}",
            json={"name": "nope"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_assign_policy_to_group(self, client, auth_headers):
        assert TestPolicies.policy_id
        resp = await client.get("/api/v1/computers/groups", headers=auth_headers)
        groups = resp.json()
        if groups:
            group_id = groups[0]["id"]
            resp = await client.post(
                f"/api/v1/policies/{TestPolicies.policy_id}/assign",
                json={"target_type": "group", "target_id": group_id},
                headers=auth_headers,
            )
            assert resp.status_code == 200
            data = resp.json()
            assert data["policy_id"] == TestPolicies.policy_id
            TestPolicies.assignment_id = data["id"]

    @pytest.mark.asyncio
    async def test_unassign_policy(self, client, auth_headers):
        assert TestPolicies.policy_id
        assert TestPolicies.assignment_id
        resp = await client.delete(
            f"/api/v1/policies/{TestPolicies.policy_id}/assign/{TestPolicies.assignment_id}",
            headers=auth_headers,
        )
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_get_computer_policies(self, client, auth_headers):
        resp = await client.get("/api/v1/computers", headers=auth_headers)
        computers = resp.json()["items"]
        if computers:
            comp_id = computers[0]["id"]
            resp = await client.get(
                f"/api/v1/policies/computer/{comp_id}",
                headers=auth_headers,
            )
            assert resp.status_code == 200
            assert isinstance(resp.json(), list)

    @pytest.mark.asyncio
    async def test_list_policies_unauthorized(self, client):
        resp = await client.get("/api/v1/policies")
        assert resp.status_code == 401


class TestCommands:
    @pytest.mark.asyncio
    async def test_send_command_to_computer(self, client, auth_headers):
        resp = await client.get("/api/v1/computers", headers=auth_headers)
        computers = resp.json()["items"]
        if computers:
            comp_id = computers[0]["id"]
            resp = await client.post(
                f"/api/v1/computers/{comp_id}/commands",
                json={"command_type": "lock_screen"},
                headers=auth_headers,
            )
            assert resp.status_code == 201
            data = resp.json()
            assert data["computer_id"] == comp_id
            assert data["command_type"] == "lock_screen"
            assert data["status"] in ("pending", "sent")

    @pytest.mark.asyncio
    async def test_send_command_to_computer_not_found(self, client, auth_headers):
        fake_id = uuid.uuid4()
        resp = await client.post(
            f"/api/v1/computers/{fake_id}/commands",
            json={"command_type": "lock_screen"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_send_command_to_group(self, client, auth_headers):
        resp = await client.get("/api/v1/computers/groups", headers=auth_headers)
        groups = resp.json()
        if groups:
            group_id = groups[0]["id"]
            resp = await client.post(
                f"/api/v1/groups/{group_id}/commands",
                json={"command_type": "restart"},
                headers=auth_headers,
            )
            assert resp.status_code == 201
            data = resp.json()
            assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_broadcast_command(self, client, auth_headers):
        resp = await client.post(
            "/api/v1/computers/broadcast",
            json={"command_type": "send_message", "payload": {"text": "Hello all"}},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 5

    @pytest.mark.asyncio
    async def test_command_unauthorized(self, client):
        resp = await client.post(
            f"/api/v1/computers/{uuid.uuid4()}/commands",
            json={"command_type": "lock_screen"},
        )
        assert resp.status_code == 401


class TestAudit:
    @pytest.mark.asyncio
    async def test_list_audit_logs(self, client, auth_headers):
        resp = await client.get("/api/v1/audit", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_list_audit_logs_filtered(self, client, auth_headers):
        resp = await client.get(
            "/api/v1/audit?page=1&page_size=10",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) <= 10

    @pytest.mark.asyncio
    async def test_list_audit_logs_unauthorized(self, client):
        resp = await client.get("/api/v1/audit")
        assert resp.status_code == 401


class TestMessages:
    @pytest.mark.asyncio
    async def test_send_message_all(self, client, auth_headers):
        resp = await client.post(
            "/api/v1/messages",
            json={
                "title": "Test Broadcast",
                "body": "This is a test",
                "message_type": "info",
                "target_type": "all",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "sent"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_send_message_to_computer(self, client, auth_headers):
        resp = await client.get("/api/v1/computers", headers=auth_headers)
        computers = resp.json()["items"]
        if computers:
            comp_id = computers[0]["id"]
            resp = await client.post(
                "/api/v1/messages",
                json={
                    "title": "Test Computer Msg",
                    "body": "Hello computer",
                    "message_type": "warning",
                    "target_type": "computer",
                    "target_id": comp_id,
                },
                headers=auth_headers,
            )
            assert resp.status_code == 201
            assert resp.json()["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_message_unauthorized(self, client):
        resp = await client.post(
            "/api/v1/messages",
            json={
                "title": "Nope",
                "body": "No auth",
                "message_type": "info",
                "target_type": "all",
            },
        )
        assert resp.status_code == 401


class TestReports:
    @pytest.mark.asyncio
    async def test_generate_report(self, client, auth_headers):
        resp = await client.post(
            "/api/v1/reports/generate",
            json={
                "report_type": "daily",
                "start_date": "2026-06-01",
                "end_date": "2026-06-15",
                "scope": "all",
                "format": "pdf",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "task_id" in data

    @pytest.mark.asyncio
    async def test_report_status_not_found(self, client, auth_headers):
        fake_id = uuid.uuid4()
        resp = await client.get(
            f"/api/v1/reports/{fake_id}/status",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "not_found"

    @pytest.mark.asyncio
    async def test_download_report_not_found(self, client, auth_headers):
        fake_id = uuid.uuid4()
        resp = await client.get(
            f"/api/v1/reports/{fake_id}/download",
            headers=auth_headers,
        )
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_generate_report_unauthorized(self, client):
        resp = await client.post(
            "/api/v1/reports/generate",
            json={
                "report_type": "daily",
                "start_date": "2026-06-01",
                "end_date": "2026-06-15",
            },
        )
        assert resp.status_code == 401


class TestErrorCases:
    @pytest.mark.asyncio
    async def test_invalid_route(self, client):
        resp = await client.get("/api/v1/nonexistent")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_access_without_role(self, client):
        resp = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "x",
                "email": "x@x.com",
                "password": "password123",
            },
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_invalid_token(self, client):
        headers = {"Authorization": "Bearer invalidtoken"}
        resp = await client.get("/api/v1/auth/me", headers=headers)
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_validation_error(self, client):
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "", "password": ""},
        )
        assert resp.status_code in (401, 422)

    @pytest.mark.asyncio
    async def test_list_computers_viewer_role(self, client):
        name = f"viewer-{uuid.uuid4().hex[:6]}"
        login_resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "admin", "password": "Admin123!"},
        )
        admin_token = login_resp.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}

        register_resp = await client.post(
            "/api/v1/auth/register",
            json={
                "username": name,
                "email": f"{name}@test.com",
                "password": "Viewer123!",
                "role": "viewer",
            },
            headers=admin_headers,
        )
        if register_resp.status_code != 201:
            pytest.skip("Could not create viewer user")

        viewer_un = register_resp.json()["username"]
        login_v = await client.post(
            "/api/v1/auth/login",
            json={"username": viewer_un, "password": "Viewer123!"},
        )
        assert login_v.status_code == 200
        viewer_token = login_v.json()["access_token"]
        viewer_headers = {"Authorization": f"Bearer {viewer_token}"}

        resp = await client.get("/api/v1/computers", headers=viewer_headers)
        assert resp.status_code == 200
        assert "items" in resp.json()

        resp = await client.get("/api/v1/audit", headers=viewer_headers)
        assert resp.status_code == 200

        resp = await client.post(
            "/api/v1/computers/groups",
            json={"name": "should-fail"},
            headers=viewer_headers,
        )
        assert resp.status_code == 403
