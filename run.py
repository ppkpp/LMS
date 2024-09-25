from server import app
from configs.setting import Settings
import uvicorn
import socket
import pyfiglet
import os
def wlan_ip():
    import subprocess
    result=subprocess.run('ipconfig',stdout=subprocess.PIPE,text=True).stdout.lower()
    scan=0
    for i in result.split('\n'):
        if 'wireless' in i: scan=1
        if scan:
            if 'ipv4' in i: return i.split(':')[1].strip()
settings = Settings()

if __name__ == "__main__":
    out = pyfiglet.figlet_format("IP Address :", justify="center", font="slant")
    print(out)
    #server_ip = wlan_ip()+":8000"
    #out = pyfiglet.figlet_format(server_ip, justify="right", font="digital",width=70)
    #print(out)
    uvicorn.run(
        "run:app",
        host=settings._host,
        port=settings._port,
        debug=settings._isdebug,
        reload=settings._isreload,
    )
