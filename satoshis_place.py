from socketIO_client import SocketIO, BaseNamespace
from socketIO_client.exceptions import ConnectionError
import numpy as np
import json


allowed_colors = ['#ffffff', '#e4e4e4', '#888888', '#222222', '#e4b4ca', '#d4361e', '#db993e', '#8e705d',
'#e6d84e', '#a3dc67', '#4aba38', '#7fcbd0', '#5880a8', '#3919d1', '#c27ad0', '#742671']

class SatPlaceSocket:

    def __init__(self, url='https://api.satoshis.place'):
        socketIO = SocketIO(url)
        socketIO.on('GET_SETTINGS_RESULT', lambda *args: self._on_get_settings_result(*args))
        socketIO.on('GET_LATEST_PIXELS_RESULT', lambda *args: self._on_get_latest_pixels_result(*args))
        socketIO.on('NEW_ORDER_RESULT', lambda *args: self._on_new_order_result(*args))
        socketIO.on('ORDER_SETTLED', lambda *args: self._on_order_settled(*args))
        self.socketIO = socketIO
        self.maxAttempts = 3

    def wait(self, seconds=0):
        if seconds > 0:
            self.socketIO.wait(seconds=seconds)
        else:
            self.socketIO.wait()

    def emitSettings(self, AttemptNr=0):
        if AttemptNr > self.maxAttempts:
            #failed
            return false
        try:
            self.socketIO.emit("GET_SETTINGS")
        except ConnectionError:
            #try again
            self.emitSettings(AttemptNr=AttemptNr+1)
        
        #succes
        return True
        

    def emitLatestPixels(self, AttemptNr=0):
        if AttemptNr > self.maxAttempts:
            #failed
            return false
        try:
            self.socketIO.emit("GET_LATEST_PIXELS")
        except ConnectionError:
            #try again
            self.emitLatestPixels(AttemptNr=AttemptNr+1)
        
        #succes
        return True
        



    def emitNewOrder(self, order, AttemptNr=0):
        if AttemptNr > self.maxAttempts:
            #failed
            return false
        try:
            self.socketIO.emit("NEW_ORDER", order)
        except ConnectionError:
            #try again
            self.emitNewOrder(order, AttemptNr=AttemptNr+1)
        
        #succes
        return True
 
    def _on_get_settings_result(self, *args):
        self.settings = args[0]['data']

    #this returns base64 image
    def _on_get_latest_pixels_result(self, *args):
        self.latestImage = args[0]['data'][len('data:image/bmp;base64,'):]

    #this returns the invoice
    def _on_new_order_result(self, *args):
        self.receivedInvoice = args[0]['data']

    def _on_order_settled(self, *args):
        self.latestImage =  args[0]['data']['image']
        self.latestPixelsPainted =  args[0]['data']['pixelsPaintedCount']
        #self.latestSessionID =  args[0]['data']['SessionID']


def test_satoshi(cj):
    sps = SatPlaceSocket()
    sps.emitNewOrder(cj)
    sps.wait()
    return sps