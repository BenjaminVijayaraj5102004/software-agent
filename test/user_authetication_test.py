from datetime import datetime, UTC
import jwt
import pytest
from app.cli.auth import register_cmd, login_cmd


@pytest.mark.asyncio
async def test_login(client):
    response = await client.post(
        "/register",
        json={ 
            "email": "test2@gmail.com",
            "password": "test22004"
        }
    )


@pytest.mark.asyncio
async def test_cli_jwt_token_expiration(client):
    await register_cmd("clitest@gmail.com", "clipassword123", silent=True)
    res = await login_cmd("clitest@gmail.com", "clipassword123", silent=True)
    assert res["status"] == "success"
    token = res["access_token"]
    
    payload = jwt.decode(token, options={"verify_signature": False})
    assert "exp" in payload
    
    exp_timestamp = payload["exp"]
    now_utc = datetime.now(UTC).timestamp()
    time_diff_seconds = exp_timestamp - now_utc
    
    # 14400 seconds = 4 hours (verify within 10 seconds boundary)
    assert 14390 <= time_diff_seconds <= 14410


   




