# Braccino Leap Motion

Un esperimento per controllare il Tinkerkit Braccio tramite un Leap Motion.

## Struttura del progetto

- 📁 [src](src): codice sorgente
- 📁 [lib](lib): librerie Leap Motion
- 📁 [arduino](arduino): contiene lo skectch Arduino
- 📁 [.vscode](.vscode): impostazioni di VS Code
- 📄 [README.md](README.md): questo file

## Dipendenze

- Python 2.7
- Leap Motion SDK

ATTENZIONE: Le librerie del Leap Motion supportano solo Python 2.7 e non Python 3, quindi è importante usare la version giusta.

## Setup

1. Prima di tutto scaricare e installare il Leap Motion SDK.
2. clonare questo repository
3. creare la cartella `./lib`
4. copiare i file delle librerie del Leap Motion, che trovi dentro l'SDK, nella cartella `./lib`. I file in question sono:
  - Leap.py
  - LeapPython.so
  - libLeap.so

Vedi anche la [guida ufficale per il setup di un progetto](https://developer-archive.leapmotion.com/documentation/python/devguide/Project_Setup.html).
