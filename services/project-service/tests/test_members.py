# import pytest

# @pytest.mark.asyncio
# async def test_add_member(client):
#     create_project_response = await client.post(
#         "/v1/projects",
#         headers={"X-User-Id":"1"},
#         json={"key": "SJ", "name": "Sjira"}
#     )
#     project_id = create_project_response.json()["id"]

#     response = await client.post(
#         f"/v1/projects/{project_id}/members",
#         headers={"X-User-Id":"1"},
#         json={"user_id":2, "role": "MEMBER"}
#     )

#     assert response.status_code == 200

#     data = response.json()
#     assert data["id"] == 1
#     assert data["project_id"] == project_id
#     assert data["user_id"] == 2
#     assert data["role"] == "MEMBER"

# @pytest.mark.asyncio
# async def test_owner_cannot_be_added_as_member(client):
#     create_project_response = await client.post(
#         "/v1/projects",
#         headers={"X-User-Id":"1"},
#         json={"key": "SJ", "name": "Sjira"}
#     )
#     project_id = create_project_response.json()["id"]

#     response = await client.post(
#         f"/v1/projects/{project_id}/members",
#         headers={"X-User-Id":"1"},
#         json={"user_id":1, "role": "MEMBER"}
#     )

#     assert response.status_code == 400

#     data = response.json()["detail"] == "Owner is already part of the project"