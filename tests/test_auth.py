import pytest

USER = {'email': 'auth@example.com', 'password': 'password123'}
USER2 = {'email': 'auth2@example.com', 'password': 'password123'}


async def test_register(client):
    r = await client.post('/auth/register', json=USER)
    assert r.status_code == 201
    data = r.json()
    assert data['email'] == USER['email']
    assert data['is_active'] is True
    assert data['token_balance'] == 100
    assert 'id' in data


async def test_register_duplicate(client):
    await client.post('/auth/register', json=USER2)
    r = await client.post('/auth/register', json=USER2)
    assert r.status_code == 409
    assert 'already registered' in r.json()['detail']


async def test_register_invalid_email(client):
    r = await client.post('/auth/register', json={'email': 'not-an-email', 'password': 'password123'})
    assert r.status_code == 422


async def test_register_short_password(client):
    r = await client.post('/auth/register', json={'email': 'short@example.com', 'password': 'abc'})
    assert r.status_code == 422


async def test_login(client):
    await client.post('/auth/register', json={'email': 'login@example.com', 'password': 'password123'})
    r = await client.post('/auth/token', data={'username': 'login@example.com', 'password': 'password123'})
    assert r.status_code == 200
    data = r.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


async def test_login_wrong_password(client):
    await client.post('/auth/register', json={'email': 'wrongpw@example.com', 'password': 'password123'})
    r = await client.post('/auth/token', data={'username': 'wrongpw@example.com', 'password': 'wrong'})
    assert r.status_code == 401


async def test_login_unknown_email(client):
    r = await client.post('/auth/token', data={'username': 'nobody@example.com', 'password': 'password123'})
    assert r.status_code == 401


async def test_get_me(client):
    await client.post('/auth/register', json={'email': 'me@example.com', 'password': 'password123'})
    r = await client.post('/auth/token', data={'username': 'me@example.com', 'password': 'password123'})
    token = r.json()['access_token']

    r = await client.get('/users/me', headers={'Authorization': f'Bearer {token}'})
    assert r.status_code == 200
    assert r.json()['email'] == 'me@example.com'


async def test_get_me_no_token(client):
    r = await client.get('/users/me')
    assert r.status_code == 401


async def test_get_me_invalid_token(client):
    r = await client.get('/users/me', headers={'Authorization': 'Bearer invalidtoken'})
    assert r.status_code == 401
