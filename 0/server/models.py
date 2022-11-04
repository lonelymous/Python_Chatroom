class User:
    Nickname = None
    Address = None
    Client = None
    IsAdmin = None
    IsServer = None

    def __init__(self, nickname, address, client, isAdmin = False, isServer = False):
        self.Nickname = nickname
        self.Address = address
        self.Client = client
        self.IsAdmin = isAdmin
        self.IsServer = isServer