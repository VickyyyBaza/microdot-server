from machine import Pin, I2C
import ssd1306
def connect_to(ssid : str, passwd : str) -> str:
    """Conecta el microcontrolador a la red indicada.

    Parameters
    ----------
    ssid : str
        Nombre de la red a conectarse
    passwd : str
        Contraseña de la red
    """
    
    import network
    from time import sleep
    
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        sta_if.active(True)
        sta_if.connect(ssid, passwd)
        while not sta_if.isconnected():
            sleep(.05)
            
    return sta_if.ifconfig()[0]


i2c = I2C(0, scl=Pin(22), sda=Pin(21))
 
ip = connect_to("Cooperadora Alumnos", "")
