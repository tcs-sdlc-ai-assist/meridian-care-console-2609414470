"""Verify protected member care workflows."""
import pytest
from httpx import ASGITransport,AsyncClient
async def sign_in(client,email):
 """Return a seeded token."""
 return (await client.post('/api/v1/auth/login',json={'email':email,'password':'DemoPass123!'})).json()['access_token']
@pytest.mark.asyncio
async def test_detail_masks_identifiers_audits_and_closes_gap():
 """Mask sensitive identifiers, audit reads, and attribute closure."""
 from app.main import app
 async with app.router.lifespan_context(app):
  async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
   h={'Authorization':f'Bearer {await sign_in(client,"coordinator@meridian.example.com")}'}
   detail=await client.get('/api/v1/members/MEM-1001',headers=h); closed=await client.post('/api/v1/members/MEM-1001/gaps/GAP-1001/close',headers=h,json={'reason':'Completed screening'})
 assert detail.status_code==200 and detail.json()['ssn']=='***-**-6789' and detail.json()['mbi']=='****MK73'
 assert closed.status_code==204
@pytest.mark.asyncio
async def test_auditor_cannot_mutate_and_invalid_outreach_is_rejected():
 """Enforce audit-only permissions and constrained outreach vocabulary."""
 from app.main import app
 async with app.router.lifespan_context(app):
  async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as client:
   auditor={'Authorization':f'Bearer {await sign_in(client,"auditor@meridian.example.com")}'}; coordinator={'Authorization':f'Bearer {await sign_in(client,"coordinator@meridian.example.com")}'}
   denied=await client.post('/api/v1/members/MEM-1001/gaps/GAP-1002/close',headers=auditor,json={'reason':'No access'}); invalid=await client.post('/api/v1/members/MEM-1001/outreach',headers=coordinator,json={'channel':'email','outcome':'reached','notes':'x'})
 assert denied.status_code==403 and invalid.status_code==422
