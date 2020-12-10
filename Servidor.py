import zmq
import json



MiPort = ""
context = zmq.Context()

ListFileServers = {}



def Bdecode(bToEncode):
    return bToEncode.decode("utf-8")

def Strencode(strToEncode):
    return str(strToEncode).encode("utf-8")

def updateListFiles(ServerID,Files):

    global ListFileServers
    DATA = json.loads(Files)
    for Artista,Albunes in DATA.items():

        if not (Artista in ListFileServers):
            ListFileServers[Artista] = {}

        for Album,Canciones in Albunes.items():

            if not (Album in ListFileServers[Artista]):
                ListFileServers[Artista][Album] = {}

            for Cancion in Canciones:

                if not (Cancion in ListFileServers[Artista][Album]):
                    ListFileServers[Artista][Album][Cancion] = []

                if not (ServerID in ListFileServers[Artista][Album][Cancion]):
                    ListFileServers[Artista][Album][Cancion].append(ServerID)


    print(ListFileServers)
    print("--------------------\n")
    return [b"1"]

def GetListData():

    Data = "--------------------\n"
    for Artista,Albunes in ListFileServers.items():
        Data = Data+"*"+Artista+"\n"
        for Album,Canciones in Albunes.items():
            Data = Data+"**"+Album+"\n"
            for Cancion,Servidores in Canciones.items():
                Data = Data+"***"+Cancion+"\n"
        Data = Data+"--------------------\n"
    return [b"1",Strencode(Data)]

def Dowload(Name):

    x = Name.split("|")

    tipe = len(x)

    for Artista,Albunes in ListFileServers.items():
        if x[0].upper() == Artista.upper():

            if tipe > 1 :

                for Album,Canciones in Albunes.items():

                    if x[1].upper() == Album.upper():
                        if tipe > 2 :

                            for Cancion,Servidores in Canciones.items():
                                NameCancion = Cancion.split(".")
                                if x[2].upper() == NameCancion[0].upper():
                                    return [b"1",Strencode('|'.join(Servidores))]

                        else:

                            y = json.dumps(Canciones)
                            return [b"1",Strencode(y)]

            else:
                y = json.dumps(Albunes)
                return [b"1",Strencode(y)]

    return [b"0",Strencode("No se encontro la busqueda solicitada")]

def init():

        global context
        global MiPort

        MiPort = input("INGRESE EL PUERTO DEL SERVIDOR\n")

        socketClients = context.socket(zmq.REP)
        socketClients.bind("tcp://*:"+MiPort)

        while True:
            MSJData = socketClients.recv_multipart()

            Type = Bdecode(MSJData[0])

            if Type == "0" :
                Respt = updateListFiles(Bdecode(MSJData[1]),Bdecode(MSJData[2]))

            elif Type == "1" :
                Respt = GetListData()

            elif Type == "2" :
                Respt = Dowload(Bdecode(MSJData[1]))


            socketClients.send_multipart(Respt)

init()
