import zmq
import json
import os
import threading
#import pygame

ipServer = ""
PortServer = ""

context = zmq.Context()

MiIp = ""
MiPort = ""

PathCode = os.path.dirname(os.path.abspath(__file__))

def VerFileExist(PathTemp,FileName):

    if os.path.isdir(PathTemp):

        obj = os.scandir(PathTemp)
        for entry in obj :
            if entry.is_file():
                DataSing = entry.name.split(".")
                if  FileName.upper() == DataSing[0].upper() :
                    return DataSing[1]

    return ""
def reproducir(Artista,Album,music):
    Archivo = Artista+"/"+Album+"/"+music+".mp3"
    playsound(Archivo)

def Strencode(strToEncode):
    return str(strToEncode).encode("utf-8")

def Bdecode(bToEncode):
    return bToEncode.decode("utf-8")

def SendSocketMSJ(IpServer,PortServer,MSJ):
    global context
    Path = "tcp://"+IpServer+":"+PortServer
    socket = context.socket(zmq.REQ)
    socket.connect(Path)
    socket.send_multipart(MSJ)
    Msjresponse = socket.recv_multipart()
    socket.close()
    return Msjresponse

def ip_puerto():
    global ipServer
    ipServer = input("INGRESE LA IP del servidor\n")
    global PortServer
    PortServer = input("INGRESE PUERTO del servidor\n")
    global MiIp
    MiIp = input("INGRESE IP DE ESTE CLIENTE\n")
    global MiPort
    MiPort = input("INGRESE EL PUERTO DE ESTE CLIENTE\n")

def SubLoadListAlbums(PathFolder):

    obj = os.scandir(PathFolder)
    AlbumsBuffer = {}

    for entry in obj :
        if entry.is_dir():
            AlbumsBuffer[entry.name] = SubLoadListMusic(PathFolder+"/"+entry.name)

    return AlbumsBuffer

def SubLoadListMusic(PathFolder):

    obj = os.scandir(PathFolder)
    MusicBuffer = []

    for entry in obj :
        if entry.is_file():
            MusicBuffer.append(entry.name)

    return MusicBuffer

def SendMyListFiles():

    global PathCode
    global ipServer
    global PortServer

    ListFiles = {}
    obj = os.scandir(PathCode)
    for entry in obj :
        if entry.is_dir():
             ListFiles[entry.name] = SubLoadListAlbums(PathCode+"/"+entry.name)

    x = json.dumps(ListFiles)
    MSJData = SendSocketMSJ(ipServer,PortServer,[b"0",Strencode(MiIp+":"+MiPort),Strencode(x)])
    return Bdecode(MSJData[0])

def Menu():

    while True:
        print("Menu \n1.Lista\n2.Descarga\n3.Actualizar")
        val =  int(input("INGRESE LA OPCIÓN\n"))

        if val in (1,2,3):
            return val
        else:
            print("Opcion invalida")

def List():

     global ipServer
     global PortServer

     MSJData = SendSocketMSJ(ipServer,PortServer,[b"1"])

     if Bdecode(MSJData[0]) == "1":
         print(Bdecode(MSJData[1]))
     else:
         print("Error conectandose con el servidor")

def DowloadSing(Artista,Album,NameSing,Servidores):


    global PathCode
    global MiIp
    global MiPort

    Myself = MiIp+":"+MiPort

    PathFileSave =  PathCode +"/"+ Artista +"/"+Album

    if Myself in Servidores:
        if VerFileExist(PathFileSave,NameSing) != "" :
            return


    for servidor in Servidores:

        Severdata = servidor.split(":")

        MSJData = SendSocketMSJ(Severdata[0],Severdata[1],[Strencode(Artista),Strencode(Album),Strencode(NameSing)])
        respt = Bdecode(MSJData[0])
        if respt == "1":
            try:
              os.makedirs(PathFileSave)
            except:
               x=1

            PathFileSave = PathFileSave +"/"+ NameSing + Bdecode(MSJData[2])
            archivo = open(PathFileSave,'ab')
            archivo.write(MSJData[1])
            archivo.close()
            #reproducir(Artista,Album,NameSing)
            return

    print("No se pudo descargar "+Artista+" "+Album+" "+NameSing)


def DowloadAlbum(JSONDATA,Artista,Album):

    DATA = json.loads(JSONDATA)
    for Cancion,Seridores in DATA.items():
            Namesong = Cancion.split(".")
            Namesong = Namesong[0]

            DowloadSing(Artista,Album,Namesong,Seridores)

def DowloadArtist(JSONDATA,Artista):

    DATA = json.loads(JSONDATA)
    for Album,Canciones in DATA.items():
            DowloadAlbum(json.dumps(Canciones),Artista,Album)


def Download():


    global ipServer
    global PortServer


    Name = input("ingrese el comando de descarga\nArtista|Album|Cancion \n ")
    tipe = len(Name.split("|"))

    MSJData = SendSocketMSJ(ipServer,PortServer,[b"2",Strencode(Name)])
    Name = Name.split("|")
    if Bdecode(MSJData[0]) == "1":
        if tipe == 1 :
            DowloadArtist(Bdecode(MSJData[1]),Name[0])
        elif tipe == 2:
            DowloadAlbum(Bdecode(MSJData[1]),Name[0],Name[1])
        elif tipe == 3:
            DowloadSing(Name[0],Name[1],Name[2],Bdecode(MSJData[1]).split("|"))

        SendMyListFiles()
        print("Descarga completa")

    else:
         print(Bdecode(MSJData[1]))

def DeleteSing(Artista,Album,NameSing,Servidores):


    global PathCode
    global MiIp
    global MiPort

    Myself = MiIp+":"+MiPort

    PathFileSave =  PathCode +"/"+ Artista +"/"+Album

    if Myself in Servidores:
        if VerFileExist(PathFileSave,NameSing) != "" :
            return


    for servidor in Servidores:

        Severdata = servidor.split(":")

        MSJData = SendSocketMSJ(Severdata[0],Severdata[1],[Strencode(Artista),Strencode(Album),Strencode(NameSing)])
        respt = Bdecode(MSJData[0])
        if respt == "1":
            try:
              os.makedirs(PathFileSave)
            except:
               x=1

            PathFileSave = PathFileSave +"/"+ NameSing + Bdecode(MSJData[2])
            archivo = open(PathFileSave,'ab')
            archivo.write(MSJData[1])
            archivo.close()
            #reproducir(Artista,Album,NameSing)
            return

    print("No se pudo descargar "+Artista+" "+Album+" "+NameSing)


def DeleteAlbum(JSONDATA,Artista,Album):

    DATA = json.loads(JSONDATA)
    for Cancion,Seridores in DATA.items():
            Namesong = Cancion.split(".")
            Namesong = Namesong[0]

            DeleteSing(Artista,Album,Namesong,Seridores)

def DeleteArtist(JSONDATA,Artista):

    DATA = json.loads(JSONDATA)
    for Album,Canciones in DATA.items():
            DeleteAlbum(json.dumps(Canciones),Artista,Album)       

def Delete():
    

    global ipServer
    global PortServer


    Name = input("ingrese el comando de borrado\nArtista|Album|Cancion \n ")
    tipe = len(Name.split("|"))

    MSJData = SendSocketMSJ(ipServer,PortServer,[b"2",Strencode(Name)])
    Name = Name.split("|")
    if Bdecode(MSJData[0]) == "1":
        if tipe == 1 :
            DeleteArtist(Bdecode(MSJData[1]),Name[0])
        elif tipe == 2:
            DleteAlbum(Bdecode(MSJData[1]),Name[0],Name[1])
        elif tipe == 3:
            DeleteSing(Name[0],Name[1],Name[2],Bdecode(MSJData[1]).split("|"))

        SendMyListFiles()
        print("borrado completo")

    else:
         print(Bdecode(MSJData[1]))


def ListenOtherClients():

    global MiPort
    global context
    global PathCode

    socketClients = context.socket(zmq.REP)
    socketClients.bind("tcp://*:"+MiPort)

    while True:

            MSJData = socketClients.recv_multipart()

            PathTemp =  PathCode +"/"+ Bdecode(MSJData[0]) +"/"+Bdecode(MSJData[1])

            Extension = VerFileExist(PathTemp,Bdecode(MSJData[2]))

            if Extension != "" :
                    PathTemp = PathTemp+"/"+Bdecode(MSJData[2])+"."+Extension
                    file = open(PathTemp, "rb")
                    content = file.read()
                    MSJ = [b"1",content,Strencode("."+Extension)]
                    file.close()
                    socketClients.send_multipart(MSJ)
                    continue

            socketClients.send_multipart([b"0"])


def init():

    ip_puerto()

    t = threading.Thread(target=ListenOtherClients)
    t.start()

    global MiIp
    global MiPort

    if SendMyListFiles():

        print("Conexion exitosa con el servidor")
        while True:

            op = Menu()

            if op == 1 :
                List()
            elif op == 2:
                Download()
            elif op == 3:
                SendMyListFiles()
                print("Archivos actualizados")
            else:
                print("Tipo invalido")
    else:
        print("Error conectandose al servidor")


init()
