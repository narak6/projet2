import copy
from quoridor_error import QuoridorError
import graphe
import argparse


class Quoridor:
    

    def __init__(self, joueurs=None, murs=None):
        """
        Initialise une partie selon les règles du jeu.
        """
        if joueurs is None:
            raise QuoridorError("Vous devez fournir la liste des joueurs.")

        if not isinstance(joueurs, list) or len(joueurs) != 2:
            raise QuoridorError("Il faut exactement deux joueurs.")

        # Préparation des joueurs
        self.joueurs = []
        for i, j in enumerate(joueurs, start=1):
            if isinstance(j, str):
                self.joueurs.append({
                    "nom": j,
                    "murs": 10,
                    "pos": [5, 9 if i == 2 else 1]
                })
            elif isinstance(j, dict):
                self.joueurs.append({
                    "nom": j["nom"],
                    "murs": j.get("murs", 10),
                    "pos": j.get("pos", [5, 9 if i == 2 else 1])
                })
            else:
                raise QuoridorError("Format de joueur invalide.")

        # Murs
        self.murs = murs if murs else {"horizontaux": [], "verticaux": []}

        self.tour = 1

    def état_partie(self):
        """Retourne une copie profonde de l'état."""
        return copy.deepcopy({
            "joueurs": self.joueurs,
            "murs": self.murs,
            "tour": self.tour,
        })

    def formater_entête(self):
        joueurs = self.joueurs
        noms = [j['nom'] for j in joueurs]
        max_nom_len = max(len(n) for n in noms)

        lignes = ["Légende:"]
        for i, j in enumerate(joueurs, start=1):
            nom = j['nom']
            murs = '|' * j['murs']
            left = f"   {i}={nom},"
            pad = (max_nom_len - len(nom)) + 1
            lignes.append(f"{left}{' ' * pad}murs={murs}")

        return "\n".join(lignes) + "\n"

    def formater_le_damier(self):
        joueurs = self.joueurs
        murs = self.murs

        lignes = ["   " + "-" * 35]
        position = [tuple(j["pos"]) for j in joueurs]

        for y in range(9, 0, -1):
            ligne = f"{y} |"
            for x in range(1, 10):
                if (x, y) == position[0]:
                    ligne += " 1 "
                elif (x, y) == position[1]:
                    ligne += " 2 "
                else:
                    ligne += " . "
                ligne += " "
            ligne = ligne[:-1] + "|"
            lignes.append(ligne)

            if y > 1:
                ligne = "  |"
                for x in range(1, 10):
                    if [x, y] in murs["horizontaux"]:
                        ligne += "-------"
                    else:
                        ligne += "       "
                ligne += "|"
                lignes.append(ligne)

        lignes.append("--|" + "-" * 35)
        lignes.append("  | 1   2   3   4   5   6   7   8   9")

        return "\n".join(lignes) + "\n"

    def __str__(self):
        return self.formater_entête() + self.formater_le_damier()

  
    def déplacer_un_joueur(self, nom_joueur, destination):
        x, y = destination

        if not (1 <= x <= 9 and 1 <= y <= 9):
            raise QuoridorError("Position invalide hors du damier.")

        joueur = next((j for j in self.joueurs if j["nom"] == nom_joueur), None)
        if joueur is None:
            raise QuoridorError("Joueur inexistant.")

        # Construire graphe pour valider movement
        g = construire_graphe(
            {1: self.joueurs[0]["pos"], 2: self.joueurs[1]["pos"]},
            self.murs["horizontaux"],
            self.murs["verticaux"]
        )
        pos_tuple = tuple(destination)

        if pos_tuple not in g.neighbors(tuple(joueur["pos"])):
            raise QuoridorError("Déplacement invalide.")

        joueur["pos"] = destination

    def placer_un_mur(self, nom_joueur, position, orientation):
        x, y = position
        joueur = next((j for j in self.joueurs if j["nom"] == nom_joueur), None)
        if joueur is None:
            raise QuoridorError("Joueur inexistant.")

        if joueur["murs"] == 0:
            raise QuoridorError("Le joueur n'a plus de murs.")

        if orientation == "H":
            if not (1 <= x <= 8 and 2 <= y <= 9):
                raise QuoridorError("Position invalide pour mur horizontal.")
            if [x, y] in self.murs["horizontaux"]:
                raise QuoridorError("Un mur occupe déjà cette position.")
            self.murs["horizontaux"].append([x, y])

        elif orientation == "V":
            if not (2 <= x <= 9 and 1 <= y <= 8):
                raise QuoridorError("Position invalide pour mur vertical.")
            if [x, y] in self.murs["verticaux"]:
                raise QuoridorError("Un mur occupe déjà cette position.")
            self.murs["verticaux"].append([x, y])

        else:
            raise QuoridorError("Orientation invalide.")

        # Vérifier qu'on n’enferme pas un joueur
        g = construire_graphe(
            {1: self.joueurs[0]["pos"], 2: self.joueurs[1]["pos"]},
            self.murs["horizontaux"],
            self.murs["verticaux"]
        )

        for i, joueur in enumerate(self.joueurs, start=1):
            if not any(n[1] == (1 if i == 1 else 9) for n in g.nodes):
                raise QuoridorError("Impossible d’enfermer un joueur.")

        joueur["murs"] -= 1

    def appliquer_un_coup(self, nom_joueur, type_coup, position):
        if self.partie_terminée():
            raise QuoridorError("La partie est déjà terminée.")

        if type_coup == "D":
            self.déplacer_un_joueur(nom_joueur, position)
        elif type_coup == "MH":
            self.placer_un_mur(nom_joueur, position, "H")
        elif type_coup == "MV":
            self.placer_un_mur(nom_joueur, position, "V")
        else:
            raise QuoridorError("Type de coup invalide.")

        # Fin du tour si joueur 2
        if nom_joueur == self.joueurs[1]["nom"]:
            self.tour += 1

        return type_coup, position

    def partie_terminée(self):
        if self.joueurs[0]["pos"][1] == 9:
            return self.joueurs[0]["nom"]
        if self.joueurs[1]["pos"][1] == 1:
            return self.joueurs[1]["nom"]
        return False

    def sélectionner_un_coup(self, nom_joueur):
        while True:
            coup = input("Coup (D, MH, MV) : ").strip()
            pos = input("Position x,y : ").split(",")
            pos = [int(pos[0]), int(pos[1])]

            copie = copy.deepcopy(self)

            try:
                copie.appliquer_un_coup(nom_joueur, coup, pos)
                return coup, pos
            except QuoridorError as e:
                print("Erreur :", e)

    def jouer_un_coup(self, nom_joueur):
        if nom_joueur not in [j["nom"] for j in self.joueurs]:
            raise QuoridorError("Joueur inexistant.")

        if self.partie_terminée():
            raise QuoridorError("La partie est terminée.")

        coup, pos = self.appliquer_un_coup(nom_joueur, *self.sélectionner_un_coup(nom_joueur))
        return coup, pos



def interpréter_la_ligne_de_commande():
    parser = argparse.ArgumentParser(description="Quoridor")
    parser.add_argument("idul", help="IDUL du joueur")
    return parser.parse_args()
