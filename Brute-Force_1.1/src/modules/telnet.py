# src/modules/telnet.py

import asyncio
import telnetlib3

async def login_telnet_async(ip, usuario, password, puerto=23, timeout=6):
    try:
        reader, writer = await telnetlib3.open_connection(ip, puerto)
        await reader.readuntil('login: ')
        writer.write(usuario + '\n')
        await reader.readuntil('Password: ')
        writer.write(password + '\n')
        response = await reader.read(1024)
        writer.close()
        await writer.wait_closed()
        return b"incorrect" not in response.lower()
    except Exception:
        return False

def login_telnet(ip, usuario, password, puerto=23, timeout=6):
    try:
        return asyncio.run(asyncio.wait_for(login_telnet_async(ip, usuario, password, puerto, timeout), timeout))
    except Exception:
        return False
