# DeckCraft – lokale autonome Beiträge mit Hermes Agent

**Controller:** https://github.com/FabPei/deckcraft  
**Fork:** https://github.com/FabPei/deckcraft-contrib  
**Original:** https://github.com/storytold/deckcraft

Dieses Repository steuert lokale Coding-AIs auf deinem Windows-PC. Es nutzt die **bereits installierte Nous Research Hermes Agent CLI**, nicht OpenCode und nicht GitHub Actions. Der Controller wählt Issues aus, implementiert kleinere Rust-Fixes, prüft sie, und legt einen Branch in deinem Fork sowie ein Freigabe-Issue an. **Ein externer Pull Request wird nur nach deiner interaktiven Zustimmung angelegt.**

## Einmalig einrichten

Benötigt: Git, GitHub CLI, Python 3.10+, Rust/rustup und Hermes CLI (Befehl: hermes). Keine OpenCode- oder npm-Installation nötig.

PowerShell:

    git clone https://github.com/FabPei/deckcraft.git
    cd deckcraft
    gh auth login

Hermes verwendet die von dir bereits konfigurierte Modell- und API-Anmeldung. Falls Xiaomi MiMo noch nicht eingerichtet ist, starte \`hermes model\`, wähle Xiaomi (Provider \`xiaomi\`) und hinterlege deinen Key in Hermes (unterstützt die Umgebungsvariable \`XIAOMI_API_KEY\`). Den Key **nicht** im Repository speichern. Du kannst alternativ bewusst deinen bereits gewählten Hermes-Provider nutzen. Optionale Umgebungsvariablen für einen spezifischen Lauf: \`HERMES_PROVIDER\` und \`HERMES_MODEL\`.

    powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup-local.ps1

Dieses Setup prüft Programme, Rust-Targets, GitHub-Zugang und die Repo-Tests. **Es startet weder einen Coding-Lauf noch den Scheduler.**

## Agenten benutzen

Ein geeignetes Issue automatisch auswählen:

    .\scripts\run-local.ps1

Ein Issue gezielt auswählen (nur falls nicht anderweitig belegt):

    .\scripts\run-local.ps1 -Issue 69

Lokalen Zeitplan explizit aktivieren (Windows Task Scheduler; Montag, Mittwoch, Freitag 19 Uhr):

    .\scripts\enable-schedule.ps1

Zeitplan wieder abschalten:

    .\scripts\disable-schedule.ps1

Scheduler läuft nur mit angemeldetem Windows-Benutzer. PC muss eingeschaltet sein. Ein Agentenlauf bearbeitet höchstens einen Kandidaten.

## PR-Publizierung

Ein erfolgreiches Ergebnis erzeugt den Fork-Branch \`agent/issue-N\` sowie ein GitHub-Issue mit dem Titel \`PR approval: upstream #N\` im Controller. Dort liegen Review, Tests und der Commit zur Ansicht.

Der PR entsteht auf einem von zwei Wegen:

- **Automatisch:** \`python scripts/local_agent.py run --publish\` öffnet den PR unmittelbar nach dem Lauf, solange das Budget es erlaubt (höchstens 3 offene Agent-PRs, höchstens 2 neue PRs pro 24 Stunden) und \`.local/PAUSE\` nicht existiert.
- **Manuell im lokalen Terminal:**

      .\scripts\approve-pr.ps1 -Issue 69

Der Publisher prüft in beiden Fällen, dass der Branch exakt dem getesteten Commit entspricht; manuell verlangt er zusätzlich die wörtliche Eingabe \`PUBLISH #69\`. Harte Grenzen: Der Controller mergt und approvt nie, pusht nie zu upstream, und der Task Scheduler startet weiterhin nur \`run\` ohne \`--publish\`. Kill-Switch: \`.local/PAUSE\` anlegen stoppt jedes Publizieren sofort.

## Technischer Ablauf

- Issue-Scout (\`scripts/select_issue.py\`) vermeidet bestehende PRs, Agent-Branches und Blocker.
- Rust-Code entsteht in eigenen Git-Worktrees unter \`.local/worktrees/\` mit gemeinsamem Cargo-Cache.
- Coding: \`hermes chat --oneshot --toolsets file --format stream-json\`. Die AI erhält Dateiwerkzeuge, aber **keine Shell-, Web-, GitHub- oder Delegationswerkzeuge**.
- Qualität: \`cargo xtask ci\`; bei Fehlschlag ein automatischer Reparaturversuch und erneute Prüfung.
- Reviewer: separater Hermes-Lauf mit \`--toolsets todo\`; der Patch wird im Prompt bereitgestellt, sodass **keine Lese-/Schreib-/Terminal-Dateiwerkzeuge** nötig sind.
- Review-Gate: \`scripts/validate_review.py\` verlangt einen erfolgreichen Hermes-\`result\`-Datensatz mit genau \`PASS\`.
- Es werden keine GitHub-Actions-Workflows für Coding, Tests oder PR-Publishing verwendet.
- Codes, Logs, Worktrees und lokale Entscheidungen bleiben unter \`.local/\` und werden nicht committed.

Referenzen: [Hermes CLI](https://hermes-agent.nousresearch.com/docs/reference/cli-commands) und [Hermes Toolsets](https://hermes-agent.nousresearch.com/docs/reference/toolsets-reference).

**Sicherheitsgrenze:** Hermes verwendet echte lokale Benutzerrechte. Eingeschränkte AI-Toolsets sind keine vollständige Betriebssystem-Sandbox. Für stärkeres Sicherheitsniveau einen eingeschränkten Windows-Benutzer oder eine VM verwenden. Der erste End-to-End-Test mit deiner konkreten Hermes/Rust-Installation ist noch ausstehend.

Die ehemals eingerichteten GitHub-Actions-Secrets für MiMo und den GitHub-PAT sind überflüssig: Hermes nutzt seine bestehende lokale Anmeldung, GitHub lokal \`gh auth login\`. Nicht mehr benötigte GitHub-Actions-Secrets löschen und den alten PAT widerrufen, sofern er anderweitig nicht gebraucht wird.
