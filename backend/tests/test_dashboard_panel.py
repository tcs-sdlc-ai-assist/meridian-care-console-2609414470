"""Verify dashboard and panel HTTP contracts."""
import pytest
from httpx import ASGITransport, AsyncClient
async def token(client, email):
    """Obtain seeded authentication for an API assertion."""
    response=await client.post('/api/v1/auth/login',json={'email':email,'password':'DemoPass123!'}); return response.json()['access_token']
@pytest.mark.asyncio
async def test_coordinator_dashboard_and_panel_are_scoped():
    """Return coordinator workload without exposing other panels."""
    from app.main import app
    async with app.router.lifespan_context(app):
      async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
        headers={'Authorization':f'Bearer {await token(client,"coordinator@meridian.example.com")}'}
        dashboard=await client.get('/api/v1/dashboard',headers=headers); panel=await client.get('/api/v1/members',headers=headers)
    assert dashboard.status_code==200 and dashboard.json()['metrics'][0]['value']==2
    assert panel.status_code==200 and all(item['coordinator_id']=='COORD-001' for item in panel.json()['items'])
@pytest.mark.asyncio
async def test_panel_rejects_missing_token():
    """Fail closed when no authorization header is supplied."""
    from app.main import app
    async with app.router.lifespan_context(app):
      async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client: response=await client.get('/api/v1/members')
    assert response.status_code==422
