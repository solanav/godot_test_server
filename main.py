import socket
from hashlib import md5

SERVER_PORT = 4343
MAX_PACKET = 1024

class Player():
    ''' Player object '''
    def __init__(self, addr):
        self.addr = addr
        self.pos = None
        self.id = md5(str(addr).encode()).hexdigest()

    def update_pos(self, posx, posy, posz, rotx, roty, rotz, rotw):
        pos = (posx, posy, posz, rotx, roty, rotz, rotw)
        self.pos = pos

    def send_update(self, sock, id, posx, posy, posz, rotx, roty, rotz, rotw):
        print('{} {} > {}, {}, {}'.format(id, self.addr, posx, posy, posz))
        sock.sendto("{},{},{},{},{},{},{},{}".format(id, posx, posy, posz, rotx, roty, rotz, rotw).encode(), self.addr)

def main():
    ''' Main loop '''
    player_list = []

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', SERVER_PORT))

    print('Starting the server...')

    while True:
        data, addr = sock.recvfrom(MAX_PACKET)

        # Clean packet
        pos = data.decode('ascii').replace('(', '').replace(')', '').replace(' ', '')
        parsed = pos.split(',')
        print(parsed)
        if len(parsed) != 7:
            continue

        # Deserialize position
        posx = float(parsed[0])
        posy = float(parsed[1])
        posz = float(parsed[2])

        # Deserialize rotation
        rotx = float(parsed[3])
        roty = float(parsed[4])
        rotz = float(parsed[5])
        rotw = float(parsed[6])

        # Deserialize hash
        id = md5(str(addr).encode()).hexdigest()

        # Looking through player list to update pos
        found = False
        for player in player_list:
            if player.addr == addr:
                # Update player
                player.update_pos(posx, posy, posz, rotx, roty, rotz, rotw)
                player.send_update(sock, id, posx + 2, posy + 5, posz, rotx, roty, rotz, rotw)
                found = True
            else:
                # Send update to other players
                if player.pos != (posx, posy, posz, rotx, roty, rotz, rotw):
                    player.send_update(sock, id, posx, posy, posz, rotx, roty, rotz, rotw)

        # New player connected
        if not found:
            print('New player connected on {}'.format(addr))
            p = Player(addr)
            p.update_pos(posx, posy, posz, rotx, roty, rotz, rotw)
            player_list.append(p)

if __name__ == '__main__':
    while True:
        try:
            main()
        except:
            pass
