#include "secrets.h"
#include <WiFi.h>
#include <ESPmDNS.h>
#include <WebServer.h>

WebServer server(80);

String ultimoMessaggio = "NESSUNO";

// ----------------------------
// PIN MOTORI
// ----------------------------
// L293D Input 1,2,3,4
const int IN1 = 25;  // input 1
const int IN2 = 33;  // input 2
const int IN3 = 32;  // input 3
const int IN4 = 26;  // input 4

// ----------------------------
// FUNZIONI MOTORI
// ----------------------------

// Motore sinistro: IN1, IN2
void motoreSinistroAvanti() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
}

void motoreSinistroIndietro() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
}

void motoreSinistroStop() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
}

// Motore destro: IN3, IN4
void motoreDestroAvanti() {
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, HIGH);
}

void motoreDestroIndietro() {
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);
}

void motoreDestroStop() {
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
}

void stopTutto() {
  motoreSinistroStop();
  motoreDestroStop();
}

void avanti() {
  motoreSinistroAvanti();
  motoreDestroAvanti();
}

void indietro() {
  motoreSinistroIndietro();
  motoreDestroIndietro();
}

// Solo lato sinistro attivo
void soloSinistraAvanti() {
  motoreSinistroAvanti();
  motoreDestroStop();
}

void soloSinistraIndietro() {
  motoreSinistroIndietro();
  motoreDestroStop();
}

// Solo lato destro attivo
void soloDestraAvanti() {
  motoreSinistroStop();
  motoreDestroAvanti();
}

void soloDestraIndietro() {
  motoreSinistroStop();
  motoreDestroIndietro();
}

// ----------------------------
// LOGICA MESSAGGI
// ----------------------------
void eseguiComando(String msg) {
  msg.trim();

  if (msg == "NESSUNA_PERSONA") {
    stopTutto();
    return;
  }

  bool personaASinistra = msg.startsWith("SINISTRA");
  bool personaADestra = msg.startsWith("DESTRA");
  bool personaAlCentro = msg.startsWith("CENTRO");

  bool personaLontana = msg.endsWith("LONTANA");
  bool personaVicina = msg.endsWith("VICINA");
  bool personaMedia = msg.endsWith("MEDIA");

  // Caso CENTRO
  if (personaAlCentro) {
    if (personaLontana) {
      avanti();
    } else if (personaVicina) {
      indietro();
    } else if (personaMedia) {
      stopTutto();
    }
    return;
  }

  // Persona a DESTRA:
  // fai partire solo i motori a sinistra
  if (personaADestra) {
    if (personaLontana) {
      soloSinistraAvanti();
    } else if (personaVicina) {
      soloSinistraIndietro();
    } else if (personaMedia) {
      motoreSinistroStop();
      motoreDestroStop();
    }
    return;
  }

  // Persona a SINISTRA:
  // fai partire solo i motori a destra
  if (personaASinistra) {
    if (personaLontana) {
      soloDestraAvanti();
    } else if (personaVicina) {
      soloDestraIndietro();
    } else if (personaMedia) {
      motoreSinistroStop();
      motoreDestroStop();
    }
    return;
  }

  // Qualsiasi altro caso imprevisto
  stopTutto();
}

// ----------------------------
// HTTP HANDLERS
// ----------------------------
void handleCmd() {
  if (server.hasArg("msg")) {
    ultimoMessaggio = server.arg("msg");

    Serial.print("Messaggio ricevuto: ");
    Serial.println(ultimoMessaggio);

    eseguiComando(ultimoMessaggio);

    server.send(200, "text/plain", "OK");
  } else {
    server.send(400, "text/plain", "Parametro msg mancante");
  }
}

void handleRoot() {
  String risposta = "ESP32 attivo. Ultimo messaggio: " + ultimoMessaggio;
  server.send(200, "text/plain", risposta);
}

// ----------------------------
// SETUP
// ----------------------------
void setup() {
  Serial.begin(115200);
  delay(1000);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  stopTutto();

  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connessione al WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  if (MDNS.begin("esp32")) {
    Serial.println("mDNS avviato");
  }

  Serial.println();
  Serial.println("WiFi connesso");
  Serial.print("IP ESP32: ");
  Serial.println(WiFi.localIP());

  server.on("/", handleRoot);
  server.on("/cmd", handleCmd);
  server.begin();

  Serial.println("Server HTTP avviato");
}

// ----------------------------
// LOOP
// ----------------------------
void loop() {
  server.handleClient();
}