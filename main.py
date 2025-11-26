

if __name__ == '__main__':
    import getpass
    from quoridor import interpréter_la_ligne_de_commande
    import api

    # Récupération des arguments de la ligne de commande
    args = interpréter_la_ligne_de_commande()
    idul = args.idul

    # Demande du jeton secret
    try:
        secret = getpass.getpass('Entrez votre jeton (secret): ')
    except Exception:
        # fallback si getpass échoue
        secret = input('Entrez votre jeton (secret): ')

    # Création de la partie
    try:
        id_partie, etat = api.créer_une_partie(idul, secret)
    except Exception as e:
        print('Erreur lors de la création de la partie:', e)
        exit(1)

    # Boucle principale de jeu
    while True:
        print(formater_le_jeu(etat))
        
        try:
            coup, position = sélectionner_un_coup()
        except StopIteration:
            print("Fin du jeu par interruption de l'utilisateur.")
            break

        # Envoi du coup au serveur
        try:
            api.appliquer_un_coup(id_partie, coup, position, idul, secret)
            _, etat = api.récupérer_une_partie(id_partie, idul, secret)
        except StopIteration as fin:
            print(f"Partie terminée! Gagnant: {fin}")
            break
        except Exception as e:
            print("Erreur lors de l'envoi du coup:", e)
            # On peut continuer ou arrêter selon le type d'erreur
            continue
