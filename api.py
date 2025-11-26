import requests

URL = "https://pax.ulaval.ca/quoridor/api/a25/"


def créer_une_partie(idul, secret):
    rep = requests.post(URL, json={'idul': idul, 'secret': secret})
    if rep.status_code == 200:
        data = rep.json()
        return data['id'], data['état']
    elif rep.status_code == 401:
        raise PermissionError("Jeton d'authentification invalide.")
    elif rep.status_code == 406:
        raise RuntimeError("Requête refusée par le serveur.")
    else:
        raise ConnectionError()
    pass


def appliquer_un_coup(id_partie, coup, position, idul, secret):
    rep = requests.put(f"{URL}/{id_partie}", json={'idul': idul, 'secret': secret, 'type': coup, 'position': position})
    if rep.status_code == 200:
        data = rep.json()
        if data.get("gagnant"):
            raise StopIteration(data["gagnant"])
        return data['dernier_coup'], data['état']
    elif rep.status_code == 401:
        raise PermissionError("Jeton invalide.")
    elif rep.status_code == 404:
        raise ReferenceError("ID de partie introuvable.")
    elif rep.status_code == 406:
        raise RuntimeError("Coup illégal.")
    else:
        raise ConnectionError()
    pass


def récupérer_une_partie(id_partie, idul, secret):
    rep = requests.get(f"{URL}/{id_partie}", params={'idul': idul, 'secret': secret})
    if rep.status_code == 200:
        data = rep.json()
        return data['id'], data['état']
    elif rep.status_code == 401:
        raise PermissionError("Jeton invalide.")
    elif rep.status_code == 404:
        raise ReferenceError("ID de partie introuvable.")
    elif rep.status_code == 406:
        raise RuntimeError("Requête invalide.")
    else:
        raise ConnectionError()
    pass