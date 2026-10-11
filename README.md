# DeckCraft — lokale Coding-AI-Automatisierung

**Controller:** [FabPei/deckcraft](https://github.com/FabPei/deckcraft)
**Öffentlicher Fork:** [FabPei/deckcraft-contrib](https://github.com/FabPei/deckcraft-contrib)
**Originalprojekt:** [storytold/deckcraft](https://github.com/storytold/deckcraft)

Der Agent arbeitet **auf deinem Windows-PC**, nicht in GitHub Actions. Er wählt ein offenes Issue aus, implementiert mit **OpenCode + Xiaomi MiMo**, testet die Rust-Änderungen lokal, lässt einen unabhängigen read-only Reviewer prüfen und pusht einen geprüften Branch in deinen Fork. Du entscheidest danach, ob ein **externer Pull Request** an das Originalprojekt erstellt werden darf.

## Einrichtung auf deinem Windows-PC

Benötigt: **Git**, **GitHub CLI** (gh), **Python 3.10+**, **Node.js/npm** und **Rust/rustup**. Installiere die offiziellen Programme über deren Installer bzw. winget. OpenCode wird bei Bedarf vom Setup über npm installiert. In PowerShell:

    git clone https://github.com/FabPei/deckcraft.git
    cd deckcraft
    gh auth login
    rustup component add rustfmt clippy
    rustup target add wasm32-unknown-unknown
    powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup-local.ps1

Das Setup fragt **einmal lokal** nach deinem MiMo-API-Key und verschlüsselt ihn mit **Windows DPAPI für deinen Windows-Benutzer** in der ignorierten Datei .local/secrets/mimo.dpapi. Du brauchst keinen OpenAI-Key. Der GitHub-Actions-Secret-Wert kann aus Sicherheitsgründen **nicht automatisch auf deinen PC übertragen werden**: den MiMo-Key deshalb lokal erneut eingeben.

- Normaler MiMo-API-Key (sk-...): Enter für https://api.xiaomimimo.com/v1.
- MiMo Token Plan (tp-... / ttp-...): den korrekten OpenAI-kompatiblen Endpoint deines Plans angeben. Siehe [Xiaomi-MiMo-Anleitung](https://mimo.mi.com/docs/tokenplan/integration/opencode).
- Auf GitHub ist **kein CONTRIBUTION_TOKEN** mehr erforderlich. Lokal verwendet Git die von dir eingerichtete GitHub-CLI-Anmeldung. Das zuvor erstellte GitHub-PAT kann nach der Umstellung widerrufen werden; den alten Actions-Secret-Eintrag kannst du löschen.

Die Einrichtung aktiviert den **Windows Task Scheduler** für Montag/Mittwoch/Freitag **19:00 Uhr deiner Windows-Ortszeit**, nur während du angemeldet bist (ausgefallene Starts werden bei der nächsten Möglichkeit nachgeholt). Dein PC muss dafür laufen. Es wird höchstens **ein Issue pro Durchlauf** bearbeitet.

## Benutzung

- **Jetzt einen automatischen Durchlauf ausführen:**
  
      .\scripts\run-local.ps1

- **Ein konkretes Issue bearbeiten** (sofern noch ohne aktiven PR und geeignet):

      .\scripts\run-local.ps1 -Issue 69

- **Geprüfte Ergebnisse ansehen:** [Freigabe-Issues](https://github.com/FabPei/deckcraft/issues) und Branches auf [FabPei/deckcraft-contrib](https://github.com/FabPei/deckcraft-contrib/branches). Die vollständigen Logs bleiben lokal unter .local/logs/.

- **Erst nach Prüfung den externen PR erstellen** (Beispiel für Issue 69):

      .\scripts\approve-pr.ps1 -Issue 69

  Der Publish-Befehl prüft, dass der Fork-Branch genau dem erfolgreich getesteten Commit entspricht. Danach verlangt er im lokalen Terminal die wörtliche Eingabe PUBLISH #69. **Kein Scheduler, Coding-Agent oder automatischer Task kann diesen Schritt ausführen.**

- **Automatisierung anhalten:**

      .\scripts\disable-schedule.ps1

- **Automatisierung wieder aktivieren:**

      .\scripts\enable-schedule.ps1

## Architektur

- scripts/local_agent.py: deterministischer lokaler Orchestrator, einmaliger Lock, Issue-Scout, Code-Agent, Rust-Tests, Reparaturversuch, unabhängiger Reviewer, kontrollierter Push in den Fork und manuelles Publish.
- scripts/select_issue.py: öffentliche Upstream-Issues und PRs analysieren, Doppelarbeit vermeiden und reproduzierbare Bugs priorisieren.
- config/opencode-mimo.json: MiMo-V2.6 Flash (Standard) oder Pro; Eingaben über Umgebungsvariablen; keine Keys im Repo. Für einen anderen Modellmodus kann der Wert model in .local/settings.json geändert werden.
- scripts/validate_review.py: verweigert Veröffentlichung bei fehlendem oder nicht exakt bestandenem Review.
- .local/source: persistent lokaler Fork-Klon mit Git-Upstream-Remote.
- .local/worktrees/issue-N: isolierter Arbeitsbereich pro Issue. Gemeinsamer Cargo-Cache unter .local/cargo-target, Fonts und gemeinsame Regeln werden lokal wiederverwendet.
- .local/approvals/N.json: exakter SHA des bestandenen lokalen CI-Laufs; nur für den manuellen Publish-Befehl.
- tests/: Controller-Tests, vollständig lokal ausführbar:

      python -m unittest discover -s tests -v

Die GitHub-Actions-Dateien für Coding, QA und PR-Publishing wurden **entfernt**, damit keine Coding-Agents, Rust-Builds oder Modellkosten auf GitHub-Runnern entstehen.

## Kosten und Grenzen

- MiMo kostet gemäß deinem API-/Token-Plan. GitHub Actions benötigt keine bezahlten Build-Minuten für den lokalen Ablauf.
- Erst ein tatsächlicher End-to-End-Durchlauf auf deinem Windows-PC kann bestätigen, dass alle Programme, Compiler, API-Zugänge und Prüfungen funktionieren. Die Implementierung allein beweist dies nicht.
- Die Coding-AI erhält Datei-Lese-/Editierwerkzeuge, aber keine Shell-, Netzwerk- oder PR-Publish-Tools. Dies ist eine Zugriffsbeschränkung im Coding-Tool, **keine vollständige Betriebssystem-Sandbox**: OpenCode und der Runner sind lokale Programme mit deinen Benutzerrechten. Für stärkere Isolation sollte ein separater Windows-Benutzer oder eine VM eingesetzt werden.
- Ein Modellfehler, fehlschlagende Tests, überschrittene Patch-Grenzen oder ein konkurrierender PR führt zum Abbruch. Kein ungeprüfter externer PR wird erstellt.
- Bestehende GitHub PRs werden nicht automatisch gemergt; die Maintainer entscheiden.

**Eine PR entsteht ausschließlich nach deiner lokalen, interaktiven Bestätigung.**
