import pytest

VALID_JOB = {
    'language': 'en',
    'audio_url': 'https://example.com/audio.mp3',
    'file_ext': 'mp3',
    'priority': 1,
}


async def _get_token(client, email: str) -> str:
    await client.post('/auth/register', json={'email': email, 'password': 'password123'})
    r = await client.post('/auth/token', data={'username': email, 'password': 'password123'})
    return r.json()['access_token']


async def _auth(client, email: str) -> dict:
    return {'Authorization': f'Bearer {await _get_token(client, email)}'}


# --- create ---

async def test_create_job(client):
    headers = await _auth(client, 'createjob@example.com')
    r = await client.post('/jobs/', json=VALID_JOB, headers=headers)
    assert r.status_code == 201
    data = r.json()
    assert data['status'] == 'pending'
    assert data['language'] == 'en'
    assert data['file_ext'] == 'mp3'


async def test_create_job_https_required(client):
    headers = await _auth(client, 'httpsjob@example.com')
    bad = {**VALID_JOB, 'audio_url': 'http://example.com/audio.mp3'}
    r = await client.post('/jobs/', json=bad, headers=headers)
    assert r.status_code == 422


async def test_create_job_invalid_priority(client):
    headers = await _auth(client, 'priorityjob@example.com')
    r = await client.post('/jobs/', json={**VALID_JOB, 'priority': 9}, headers=headers)
    assert r.status_code == 422


async def test_create_job_invalid_language(client):
    headers = await _auth(client, 'langjob@example.com')
    r = await client.post('/jobs/', json={**VALID_JOB, 'language': 'xx'}, headers=headers)
    assert r.status_code == 422


async def test_create_job_unauthenticated(client):
    r = await client.post('/jobs/', json=VALID_JOB)
    assert r.status_code == 401


# --- get by id ---

async def test_get_job(client):
    headers = await _auth(client, 'getjob@example.com')
    job_id = (await client.post('/jobs/', json=VALID_JOB, headers=headers)).json()['id']
    r = await client.get(f'/jobs/{job_id}', headers=headers)
    assert r.status_code == 200
    assert r.json()['id'] == job_id


async def test_get_job_not_found(client):
    headers = await _auth(client, 'notfoundjob@example.com')
    r = await client.get('/jobs/00000000-0000-0000-0000-000000000000', headers=headers)
    assert r.status_code == 404


async def test_get_job_other_user(client):
    headers_a = await _auth(client, 'usera@example.com')
    headers_b = await _auth(client, 'userb@example.com')
    job_id = (await client.post('/jobs/', json=VALID_JOB, headers=headers_a)).json()['id']
    r = await client.get(f'/jobs/{job_id}', headers=headers_b)
    assert r.status_code == 404


# --- list ---

async def test_list_jobs(client):
    headers = await _auth(client, 'listjobs@example.com')
    await client.post('/jobs/', json=VALID_JOB, headers=headers)
    await client.post('/jobs/', json=VALID_JOB, headers=headers)
    r = await client.get('/jobs/', headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert 'items' in data
    assert data['total'] >= 2


async def test_list_jobs_status_filter(client):
    headers = await _auth(client, 'filterjobs@example.com')
    await client.post('/jobs/', json=VALID_JOB, headers=headers)
    r = await client.get('/jobs/?status=pending', headers=headers)
    assert r.status_code == 200
    assert all(j['status'] == 'pending' for j in r.json()['items'])


# --- patch status ---

async def test_patch_status(client):
    headers = await _auth(client, 'patchjob@example.com')
    job_id = (await client.post('/jobs/', json=VALID_JOB, headers=headers)).json()['id']
    r = await client.patch(f'/jobs/{job_id}/status', json={'status': 'processing'}, headers=headers)
    assert r.status_code == 200
    assert r.json()['status'] == 'processing'


# --- soft delete ---

async def test_delete_job(client):
    headers = await _auth(client, 'deletejob@example.com')
    job_id = (await client.post('/jobs/', json=VALID_JOB, headers=headers)).json()['id']
    r = await client.delete(f'/jobs/{job_id}', headers=headers)
    assert r.status_code == 204
    r = await client.get(f'/jobs/{job_id}', headers=headers)
    assert r.status_code == 404


async def test_delete_job_not_found(client):
    headers = await _auth(client, 'deletenotfound@example.com')
    r = await client.delete('/jobs/00000000-0000-0000-0000-000000000000', headers=headers)
    assert r.status_code == 404


# --- healthcheck ---

async def test_healthcheck(client):
    r = await client.get('/healthcheck')
    assert r.status_code == 200
    assert r.json()['status'] == 'ok'
