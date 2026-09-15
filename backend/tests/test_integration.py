"""Exercise a cross-feature seeded care journey."""
import pytest
from httpx import ASGITransport,AsyncClient
@pytest.mark.asyncio
async def test_login_dashboard_member_detail_and_closure_chain():
 """Carry authenticated identity through dashboard, detail, and care-gap mutation."""
 from app.main import app
 async with app.router.lifespan_context(app):
  async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
   login=await client.post('/api/v1/auth/login',json={'email':'coordinator@meridian.example.com','password':'DemoPass123!'});headers={'Authorization':f"Bearer {login.json()['access_token']}"}
   dashboard=await client.get('/api/v1/dashboard',headers=headers); detail=await client.get('/api/v1/members/MEM-1001',headers=headers); closed=await client.post('/api/v1/members/MEM-1001/gaps/GAP-1001/close',headers=headers,json={'reason':'Integrated demo flow'})
 assert login.status_code==200 and dashboard.status_code==200 and detail.json()['ssn']=='***-**-6789' and closed.status_code==204
