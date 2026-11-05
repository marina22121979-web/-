---
name: "better-subs-davinci"
metadata:
  version: "1.2.0"
description: "Better Subs Davinci: sottotitoli per reel verticali in DaVinci Resolve (trascrizione, correzione su script, suddivisione, SRT, marker). Usala per \"fai i subs\" o \"rigenera i subs in questo punto\"."
---

# Better Subs Davinci — v1.2.0
Sottotitoli in DaVinci Resolve per reel verticali.

Lavora sulla timeline aperta in Resolve tramite gli strumenti `run_script` / `run_script_unsafe` (se l'agente li tiene da attivare o differiti, caricali prima con il suo meccanismo; i nomi possono cambiare a seconda del server MCP di Resolve collegato, in tal caso usa gli equivalenti). Ogni chiamata è stateless: rileggi sempre lo stato dalla timeline. Rispondi in italiano.

## 0. Glossario, Resolve, progetto e timeline
- **Prima azione, prima di qualsiasi domanda o chiamata a Resolve:** cerca nella cartella della skill i file `glossario.*` e leggili (vedi sezione Glossario). La sezione del cliente la scegli in ricognizione, quando conosci progetto e timeline.
- Verifica che DaVinci Resolve sia aperto (es. `get_resolve_status`). Se non lo è, aprilo con lo strumento di avvio (es. `launch_resolve`) e aspetta che risponda (il primo avvio può richiedere fino a un minuto). Se l'avvio fallisce, dillo all'utente e fermati.
- Leggi progetto e timeline attualmente aperti.
- **Raccogli in un solo messaggio tutto ciò che manca**: progetto, timeline, `MAXC` e script (formula in sezione 2). Non fare più giri di domande.
- **Se l'utente non ha già indicato progetto e timeline** nella richiesta, chiedigli su quali devi generare i sottotitoli, proponendo come default quelli aperti ora (es. "Genero su *NN - Titolo V1* nel progetto *X*, giusto?"). Se ha già indicato progetto e/o timeline, usa quelli: se diversi da quelli aperti, aprili (`LoadProject`, `SetCurrentTimeline`) e verifica di essere sulla timeline giusta prima di toccare qualcosa.
- Se progetto o timeline indicati non esistono, mostra i nomi disponibili e chiedi quale.
- **Se l'utente non ha già indicato quanti caratteri deve contenere al massimo ogni sottotitolo**, chiedilo nello stesso messaggio, proponendo 20 come valore tipico per i reel verticali 1080×1920. Chiamalo `MAXC` e usalo ovunque sotto: generazione (sezione 3), suddivisione (sezione 5), riepilogo (sezione 8) e controllo `long` dello script. Se l'utente l'ha già detto, usa quel valore senza richiedere.
- **Di' subito all'utente che lo stile dei sottotitoli resta a lui:** l'API non imposta template o stile. A lavoro finito seleziona un sottotitolo e regola lo stile dell'intera traccia nell'Inspector.

## 1. Ricognizione
- Leggi: progetto, timeline, fps, `GetStartFrame()` e TC di partenza (può essere 01:00:00:00 = 86400 a 24 fps), In/Out (`GetMarkInOut`), marker esistenti con colori, tracce audio (quale è la voce, di solito A1), tagli su V1 (`GetStart` degli item V1), sottotitoli già presenti.
- Range di lavoro, in ordine di priorità: indicazione in chat (es. "ignora da 00:00:45:26") → In/Out dell'utente → tutta la timeline.
- **Modalità parziale** ("rigenera nel punto segnato"): tocca solo quel tratto; i testi del resto della traccia (anche modificati a mano dall'utente) devono restare identici.
- Annota i colori marker già usati: non riusarli (Fucsia e Giallo di solito liberi).
- Dal glossario già letto (sezione 0) scegli le voci che corrispondono a progetto e timeline.

## 2. Script
**Se l'utente non ha già indicato lo script nella richiesta** (allegato, testo incollato, nome o link di un file su Google Docs/Drive o su Notion, oppure "senza script"), **chiediglielo, a ogni richiesta, prima di generare i sottotitoli.** Se l'ha già indicato, usa quello e non chiedere di nuovo. Non indovinarlo dal nome del progetto o della timeline e non riusare quello di una richiesta precedente. Falla nello stesso messaggio delle domande della sezione 0 e aspetta la risposta prima di passare alla sezione 3. Formula (adattala, resta breve):

> Mi serve lo script del video. Come me lo dai?
> 1. Allegato o incollato in chat
> 2. Nome (o link) del file su Google Docs / Drive
> 3. Nome (o link) della pagina su Notion
> 4. Nessuno script: sottotitoli solo dall'audio, con trascrizione esterna obbligatoria (attenzione: senza script il controllo degli errori è solo sommario)

Poi, in base alla risposta:
- **Allegato o incollato**: usa direttamente quel testo.
- **Google Docs / Drive**: lo strumento di ricerca file del connettore (es. `search_files` con `title contains '<nome>'`), poi quello di lettura (es. `read_file_content`). Se i risultati sono più d'uno o nessuno, mostra i candidati e chiedi quale; non scegliere a caso.
- **Notion**: cerca la pagina per titolo con lo strumento di ricerca Notion (es. `notion-search`) oppure apri il link dato. Se l'utente ha detto solo "su Notion", o un link dà 404, cerca il nome del progetto o della timeline (con e senza " V1") e leggi anche i contenuti del database, poi **proponi il candidato e chiedi conferma**. Se ci sono più corrispondenze o nessuna, mostra i candidati e chiedi. Leggi anche Note/proprietà della pagina (CTA, parole chiave, avvertenze).
- **Controlla sempre che lo script sia quello giusto**: durata e contenuti devono essere compatibili con la timeline. Se non lo sono, dillo e chiedi.
- **Nessuno script**: **insisti sul fatto che senza script il controllo è solo sommario.** Senza un testo di riferimento non puoi sapere come sono scritti nomi, marchi, titoli e parole chiave, né se la trascrizione automatica ha saltato o storpiato dei pezzi: puoi correggere solo gli errori evidenti (grammatica, parole senza senso). Prima di procedere dillo chiaramente e invita l'utente a darti lo script (anche solo incollato in chat). Se conferma di voler andare avanti senza, **la trascrizione esterna (sezione 3A) è un passaggio obbligatorio**: il motore interno di Resolve non permette di scegliere il modello e da solo, senza script a correggerlo, non è affidabile. Marca Fucsia ogni dubbio su nomi e termini.
- Se il connettore richiesto (Drive o Notion) non è disponibile o la ricerca fallisce, dillo e chiedi di allegare o incollare il testo. Non proseguire senza script a meno che l'utente scelga l'opzione 4.

## 3A. Trascrizione esterna (obbligatoria se non c'è uno script)
Resolve non permette di scegliere il modello di trascrizione. **Il percorso predefinito è `stable-ts` con Whisper large-v3-turbo, che dà sia il testo sia i tempi per parola.** Se non c'è uno script è obbligatorio, non usare `CreateSubtitlesFromAudio`. Con uno script resta il predefinito; il motore interno (sezione 3) è il ripiego se `stable-ts` manca e l'utente non vuole installarlo, o se lo chiede lui. **Non fidarti di Whisper puro per i tempi**: può anticipare l'inizio delle parole di diversi frame.
- **Quale modello consigliare all'utente.** Spiega la scelta in due righe, con peso su disco e motivo. Pesi approssimati: verificali sul Mac dell'utente.

  | Modello | Peso | Scegli se | Contro |
  |---|---|---|---|
  | **Whisper large-v3-turbo** con `stable-ts` (file `large-v3-turbo.pt`) | ~1,5 GB | È il default: buon italiano, veloce, buoni tempi. Va bene per quasi tutti i reel. | Su audio molto sporco (musica sotto, più voci) può sbagliare più parole. |
  | **Whisper large-v3** (`faster-whisper`, cartella `faster-whisper-large-v3`) | ~3 GB | Solo per il testo, se turbo sbaglia nomi o l'audio è difficile. | Più lento (su Mac gira su CPU). I suoi tempi vanno ricontrollati con il controllo voce. |
  | **Parakeet v3** (`sherpa-onnx`, int8) | ~0,6 GB | Solo se l'utente lo chiede, per velocità su parlato pulito. | Italiano meno collaudato, richiede `sherpa-onnx`. |

- **Verifica prima di trascrivere** (senza eseguire nulla): modulo Python `stable_whisper`, file del modello (es. `~/.cache/whisper/large-v3-turbo.pt`) e `ffmpeg`. Cerca i moduli in tutti i Python presenti (di sistema, Homebrew, venv, `~/venv-subs`): possono stare in uno solo e non nel `python3` del PATH.
- **Se manca qualcosa**, fermati: di' cosa manca, cosa scarichi e quanto pesa, e **aspetta il suo ok prima di installare**. Non ripiegare in silenzio sul motore interno. Procedura standard:
  ```bash
  python3 -m venv ~/venv-subs && ~/venv-subs/bin/pip install stable-ts
  ```
  Il modello già presente in `~/.cache/whisper/` viene riusato; se manca, lo scarica al primo uso.
- **Procedura:**
  1. **Audio voce.** Usa il modello "Export voce": ricostruisce la traccia voce dai clip sorgente, ognuno alla sua posizione sulla timeline, e lascia fuori musica ed effetti. Prende l'inizio sorgente in secondi, quindi vale anche per sorgenti con frame rate diverso dalla timeline. Ignora le dissolvenze. Se segnala clip con velocità cambiata, fermati e dillo: i tempi non sarebbero affidabili (ripiego: render audio della traccia voce da Resolve). Se la voce sta su più tracce, chiedi quali usare.
  2. **Trascrizione.** Usa il modello "Trascrizione": `EXT_WORDS` in frame assoluti (`round(secondi * fps) + GetStartFrame()`).
  3. **Punteggiatura.** Se manca, aggiungila prima di suddividere, perché guida dove spezzare le righe. Il numero di parole deve restare uguale.
  4. Passa le parole alle sezioni 4 e 5 e inserisci con l'unico SRT della sezione 6.
  5. **Controllo voce.** Dopo l'inserimento lancia il modello "Controllo voce" (sezione 6).
- Canzoni: vale la regola della sezione 4 (non trascrivere i testi cantati; tratto vuoto + marker Giallo).

## 3. Generazione (motore interno di Resolve, ripiego)
1. Se `GetTrackCount("subtitle") == 0` → `tl.AddTrack("subtitle")` (senza traccia la generazione fallisce in silenzio).
2. Disattiva tutte le tracce audio tranne la voce (musica, SFX, canzoni), genera, riattivale nello stesso script (try/finally) allo stato originale.
3. `tl.CreateSubtitlesFromAudio({resolve.SUBTITLE_LANGUAGE: resolve.AUTO_CAPTION_ITALIAN, resolve.SUBTITLE_CAPTION_PRESET: resolve.AUTO_CAPTION_SUBTITLE_DEFAULT, resolve.SUBTITLE_CHARS_PER_LINE: MAXC + 4, resolve.SUBTITLE_LINE_BREAK: resolve.AUTO_CAPTION_LINE_SINGLE, resolve.SUBTITLE_GAP: 0})`. Rispetta l'In/Out e aggiunge alla traccia esistente.
4. La funzione ritorna prima che i sottotitoli compaiano: in una chiamata successiva controlla `project.GetCreateSubtitlesFromAudioStatus()` finché `JobStatus` è `Complete`, poi rileggi.
5. Range da linea in chat: `tl.SetMarkInOut(in_rel, out_rel)` (frame relativi a inizio timeline), poi `ClearMarkInOut()` alla fine. Se l'utente aveva un suo In/Out, rimettilo come prima a fine lavoro.
6. Se la generazione salta dei tratti o produce righe senza senso: rigenera solo quel tratto con In/Out temporaneo (cancella prima i sub spazzatura). Fallback: `MediaPoolItem.TranscribeAudio()` + `GetTranscription()`, ma spesso è incompleta.
7. **Video lunghi:** la generazione può saltare interi tratti verso la fine. Controlla sempre che i sub arrivino all'ultima clip con voce.
8. Chiamate > 60 s vanno in timeout ma il lavoro prosegue. Se Resolve non risponde (pagina `None`), c'è un dialogo aperto: chiedi all'utente di chiuderlo.

## 4. Correzione del testo
- Segui l'audio, non la lettera dello script: riformulazioni, aggiunte e inversioni vanno bene se il senso regge. Correggi errori di trascrizione veri e grammatica.
- Nomi, marchi, titoli, parole chiave: grafia dello script / del glossario.
- Se dubbio forte: ipotesi più probabile + marker Fucsia.
- Intercalari tipo "e" sospesi possono essere tolti (segnalalo nel marker).
- Testi citati da slide o messaggi: tra virgolette.
- **Canzoni**: mai trascrivere o scrivere testi cantati (nemmeno citati). Lascia il tratto vuoto e metti un marker Giallo "Testo canzone" lungo quanto il verso. Titoli di canzoni sì.

## 5. Suddivisione (1080×1920)
- Una unità di senso per riga, max `MAXC` caratteri. Fino a `MAXC` + 4 solo per nomi, titoli e frasi CTA da non spezzare, o se altrimenti una riga scenderebbe sotto gli 8 frame: elenca queste righe nel riepilogo.
- Spezza dopo la punteggiatura o prima di congiunzioni/preposizioni. Mai riga che finisce con articolo, preposizione, congiunzione o possessivo ("il", "di", "e", "che", "tua"...), salvo che chiuda con punteggiatura. Mai spezzare una parola o una locuzione ("tutte e due"). Evita che una frase finisca a metà riga ("tua. Nessuno ti ha").
- Tempi parole: con `stable-ts` usa i suoi. Solo con il motore interno distribuisci la durata di ogni sub in proporzione ai caratteri (len(parola)+1).
- Definisci le righe come lista `(testo_nuovo, n_parole_originali)`. Prima di inserire stampa per ogni riga `testo nuovo <= parole originali` e verifica che la somma degli n = numero parole trascritte. Un errore di conteggio si propaga a cascata.
- Confini:
  - inizio riga = inizio della sua prima parola; fine = inizio della riga successiva (nessuno spazio);
  - se dentro la pausa tra fine ultima parola precedente e inizio riga (±5 frame) cade un taglio, il confine va esattamente sul taglio;
  - primo sub di un blocco dall'inizio del blocco, ultimo fino alla sua fine;
  - restano vuoti solo tratti senza voce (solo musica/grafica, stacchi senza clip) e canzoni.
- **Blocchi:** ogni tratto continuo di voce è un elemento di `RANGES = [(inizio, fine, righe), ...]`. Vuoti e canzoni sono semplicemente fuori dai blocchi, senza più esecuzioni a mano.
- Durata minima 8 frame: se una riga è più corta, accorpala alla vicina e rilancia (lo script si ferma senza inserire se trova righe corte).
- Attraversamenti di taglio a metà frase o su clip < ~1 s sono accettabili: elencali.

## 6. Inserimento (il testo dei sub non è modificabile via API)
- **Ricostruisci sempre l'intera traccia con un unico SRT**: sub attuali da tenere (con i testi correnti) + tratto nuovo. Un SRT parziale accodato finisce in coda alla timeline, non al suo posto.
- Se `GetTrackCount("subtitle") == 0`, crea la traccia con `tl.AddTrack("subtitle")` prima di inserire (vale anche per il percorso esterno).
- **Sostituire la traccia è distruttivo.** Se contiene già sottotitoli e l'utente non ha chiesto esplicitamente di rigenerarli o sostituirli, chiedi conferma, poi metti `CONFERMATO = True`. `SOSTITUISCI = True` rigenera tutta la traccia senza ricopiare i sub esistenti; con `False` restano quelli fuori dai blocchi (modalità parziale). Lo script salva sempre prima un backup SRT della traccia attuale e, se l'inserimento fallisce, la ripristina da lì. Dì all'utente dove sta il backup.
- Lo script si ferma se la timeline aperta non è `TIMELINE`, quella dichiarata.
- Tempi SRT relativi a `GetStartFrame()` (frame - start) / fps.
- Nella stessa chiamata `run_script_unsafe`: scrivi SRT in tempfile, `DeleteClips(subs)`, `SetTrackEnable("subtitle",1,True)`, `SetCurrentTimecode(tl.GetStartTimecode())`, `MediaPool.ImportMedia([srt])`, `MediaPool.AppendToTimeline([item])` passando **solo il MediaPoolItem** (mai dict con mediaType: crasha).
- Rileggi: numero sub, tempi e testi identici ai previsti, nessuno spazio fuori dai vuoti voluti, `GetEndFrame()` invariato. `AppendToTimeline` può dire successo anche se non ha inserito o ha inserito altrove. Questo controllo confronta i sub con il piano, non con la voce.
- **Controllo voce** (modello in fondo): misura lo scarto tra l'inizio dei sub e gli attacchi della voce dopo una pausa (attività rms a 10 ms, soglia p98 meno 28 dB). Riporta scarto medio assoluto e massimo in frame, non lo scarto medio con segno, che nasconde gli errori. I sub con la voce già nei primi 3 frame contano come allineati (`voce_subito`), quindi le misure riguardano solo i rimanenti. **Serve solo a segnalare, non correggere in automatico**: la forma d'onda scambia respiri e rumori per attacchi. Nei tagli l'inizio del sub è agganciato al taglio, quindi uno scarto lì può essere voluto. Se ci sono scarti oltre 4 frame, elencali nel riepilogo in forma sintetica, con il timecode, e lascia decidere all'utente.
- L'append cancella l'In/Out: ripristinalo se era dell'utente.
- Salva (`SaveProject`). Elimina dal Media Pool solo gli SRT importati da te in questa esecuzione (nomi `bsd-...`), non quello della traccia finale finché non è verificata, e mai altri item. Avvisa che lo stile personalizzato di singoli sub va riapplicato se la traccia è stata ricostruita.

## 7. Marker
- Fucsia "Controlla sub" (colore API `Fuchsia`; `Pink` esiste ma è un altro colore): nota `Trascritto: "...". Ho scritto "..."`, durata pari al sub (o ai sub coinvolti).
- Non toccare i marker dell'utente; se il frame è occupato sposta di +1.
- Non segnalare con marker Fucsia ciò che il glossario già copre (frasi di presentazione, parole chiave CTA).
- Se rigeneri i sub, riposiziona sui nuovi sub i marker "Controlla sub": cancella solo quelli con questo nome e ricreali, senza toccare gli altri.
- In modalità parziale aggiorna la nota dei tuoi marker già presenti nel tratto.
- Marker in frame relativi a inizio timeline; converti in TC per il riepilogo.

## 8. Riepilogo finale (breve, italiano)
- In cima: "Glossario letto: [file e sezioni usate]" oppure "Nessuna voce utile".
- Numero sub, range coperto, spazi (dove e perché), righe oltre `MAXC` caratteri, attraversamenti accettati, risultato del controllo voce (scarto medio assoluto, massimo, punti oltre 4 frame).
- Tabella correzioni principali (trascritto → corretto).
- Marker con timecode e cosa verificare.
- Differenze rilevanti dallo script (frasi improvvisate, parti tagliate, CTA diverso).
- Se si è lavorato senza script: ripeti in cima al riepilogo che il controllo è stato solo sommario (nessun testo di riferimento per nomi, marchi e parole chiave) e che l'utente deve rileggere i sottotitoli, a partire dai marker Fucsia.

## Glossario (opzionale)
I glossari stanno in file a parte, nella stessa cartella di questa skill. Non sono codice della skill: contengono clienti e progetti di chi la usa.
- `glossario.md` è il modello condiviso: struttura vuota con voci segnaposto. Ignora le voci segnaposto; chi vuole può compilarlo.
- `glossario.<nome>.md` (es. `glossario.fabio.md`) è il glossario personale di una persona, pensato per restare privato.
- Come indicato in sezione 0, leggi per prima cosa tutti i file `glossario.*` della cartella della skill e usa le sezioni che corrispondono al cliente o al progetto in corso (parole chiave CTA, frasi tipiche, errori ricorrenti, grafia di nomi e brani). Se più file hanno la stessa voce, vale quello personale.
- Se non trovi voci utili, procedi senza e non inventare. Puoi proporre all'utente di compilare `glossario.md` o di creare il proprio `glossario.<nome>.md`.
- Quando emergono nuove forme (un nome scritto in modo diverso, un errore che si ripete, una nuova parola chiave), proponi di aggiungerle al glossario dell'utente e scrivile solo dopo il suo ok.

## Modello "Export voce" (`run_script_unsafe`)

```python
import json, os, shutil, subprocess, tempfile, wave
TRACCIA = 1          # traccia audio con la voce
SR = 16000
tl = project.GetCurrentTimeline(); fps = float(tl.GetSetting("timelineFrameRate")); S = tl.GetStartFrame()
ff = shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
clips = [x for x in (tl.GetItemListInTrack("audio", TRACCIA) or []) if x.GetMediaPoolItem()]
end = max(x.GetEnd() for x in clips)
buf = bytearray(2 * int((end - S) / fps * SR + SR))
velocita, errori = [], []
for x in clips:
    dur = (x.GetEnd() - x.GetStart()) / fps
    if abs((x.GetSourceEndTime() - x.GetSourceStartTime()) - dur) > 0.1: velocita.append((x.GetStart(), x.GetName()))
    f = x.GetMediaPoolItem().GetClipProperty("File Path")
    r = subprocess.run([ff, "-v", "error", "-ss", str(x.GetSourceStartTime()), "-t", str(dur), "-i", f, "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"], capture_output=True)
    if r.returncode: errori.append((x.GetName(), r.stderr[-200:].decode(errors="ignore"))); continue
    i = 2 * int(round((x.GetStart() - S) / fps * SR)); buf[i:i+len(r.stdout)] = r.stdout
path = os.path.join(tempfile.gettempdir(), "bsd-voce.wav")
w = wave.open(path, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(bytes(buf)); w.close()
result = {"wav": path, "clip": len(clips), "velocita_cambiata": velocita, "errori": errori}
```

## Modello "Trascrizione" (Python con `stable_whisper`, da terminale)

```python
import json, sys, stable_whisper
wav, fps, start = sys.argv[1], float(sys.argv[2]), int(sys.argv[3])
r = stable_whisper.load_model("large-v3-turbo").transcribe(wav, language="it", fp16=False, verbose=None)
ws = [(w.word.strip(), round(w.start * fps) + start, round(w.end * fps) + start) for s in r.segments for w in s.words]
json.dump(ws, open(wav + ".words.json", "w"), ensure_ascii=False)
print(len(ws), "parole"); print(r.text)
```

## Modello "Inserimento" (adatta TIMELINE, MAXC, RANGES, EXT_WORDS, SOSTITUISCI, CONFERMATO)

```python
import tempfile, os, time
TIMELINE = "Nome timeline"   # quella dichiarata: lo script si ferma se è aperta un'altra
MAXC = 20            # massimo caratteri per sottotitolo, come scelto dall'utente
RANGES = [(0, 300, [("Prima riga", 2), ("seconda riga", 3)])]  # (inizio, fine, [(testo, n parole originali), ...]), frame assoluti
EXT_WORDS = None     # percorso esterno: [(parola, frame_inizio, frame_fine), ...] assoluti; None = parole dai sub esistenti
SOSTITUISCI = False  # True = rigenera tutta la traccia senza ricopiare i sub esistenti
CONFERMATO = False   # True solo se la traccia non è vuota e l'utente ha chiesto o confermato di modificarla
def main():
    tl = project.GetCurrentTimeline(); mp = project.GetMediaPool()
    if tl.GetName() != TIMELINE: return {"abort": "timeline", "aperta": tl.GetName()}
    fps = float(tl.GetSetting("timelineFrameRate"))
    S = tl.GetStartFrame()
    subs = sorted((tl.GetItemListInTrack("subtitle", 1) or []) if tl.GetTrackCount("subtitle") else [], key=lambda x: x.GetStart())
    if subs and not CONFERMATO: return {"abort": "conferma", "sub_esistenti": len(subs)}
    blocchi = sorted(RANGES, key=lambda b: b[0])
    if any(blocchi[k][1] > blocchi[k+1][0] for k in range(len(blocchi)-1)): return {"abort": "blocchi sovrapposti"}
    dentro = lambda f: any(b[0] <= f < b[1] for b in blocchi)
    zone = list(subs) if SOSTITUISCI else [x for x in subs if dentro(x.GetStart())]
    keep = [(x.GetStart(), x.GetEnd(), x.GetName()) for x in subs if x not in zone]
    if not SOSTITUISCI:
        edge = [t for a, e, t in keep if any(a < b[0] < e for b in blocchi)] + [x.GetName() for x in zone if not any(b[0] <= x.GetStart() and x.GetEnd() <= b[1] for b in blocchi)]
        if edge: return {"abort": "straddle", "subs": edge}   # un blocco taglia a metà un sub esistente: sposta i suoi confini
    cuts = sorted(it.GetStart() for it in (tl.GetItemListInTrack("video", 1) or []))[1:]
    spans, align = [], []
    for bs, be, L in blocchi:
        if EXT_WORDS:
            ew = [x for x in EXT_WORDS if bs - 10 <= x[1] < be]
            W = [(a, e) for _, a, e in ew]; names = [w for w, _, _ in ew]
        else:
            W, names = [], []
            for it in [x for x in zone if bs <= x.GetStart() < be]:
                ws = it.GetName().split(); s, e = it.GetStart(), it.GetEnd()
                tot = sum(len(w)+1 for w in ws); acc = 0
                for w in ws:
                    a = s + (e-s)*acc/tot; acc += len(w)+1
                    W.append((a, s + (e-s)*acc/tot)); names.append(w)
        i = 0
        for t, n in L:
            align.append(f"{t} <= {' '.join(names[i:i+n])}"); i += n
        if sum(n for _, n in L) != len(W) or any(n < 1 for _, n in L):
            return {"abort": "count", "blocco": (bs, be), "need": sum(n for _, n in L), "have": len(W), "align": align}
        st, i = [], 0
        for k, (t, n) in enumerate(L):
            if k == 0: st.append(bs)
            else:
                a, prev_end = W[i][0], W[i-1][1]
                inside = [c for c in cuts if prev_end - 5 <= c <= a + 5 and bs < c < be]
                st.append(min(inside, key=lambda c: abs(c-a)) if inside else round(a))
            i += n
        spans += [(st[k], st[k+1] if k+1 < len(L) else be, L[k][0]) for k in range(len(L))]
    short = [(t, a, e-a) for a, e, t in spans if e - a < 8]
    if short: return {"abort": "short", "short": short, "align": align}
    data = sorted(keep + spans)
    if any(data[k][1] > data[k+1][0] for k in range(len(data)-1)): return {"abort": "sovrapposti"}
    def tc(f):
        ms = round((f - S) * 1000 / fps)
        h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
    def srt_of(rows):
        return "\n".join(f"{k+1}\n{tc(a)} --> {tc(e)}\n{t}\n" for k, (a, e, t) in enumerate(rows))
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in tl.GetName())
    stamp = time.strftime("%Y%m%d-%H%M%S")
    path = os.path.join(tempfile.gettempdir(), f"bsd-{safe}-{stamp}.srt")
    bak = os.path.join(tempfile.gettempdir(), f"bsd-{safe}-{stamp}-backup.srt")
    open(path, "w", encoding="utf-8").write(srt_of(data))
    open(bak, "w", encoding="utf-8").write(srt_of([(x.GetStart(), x.GetEnd(), x.GetName()) for x in subs]))
    if tl.GetTrackCount("subtitle") == 0: tl.AddTrack("subtitle")
    inout = tl.GetMarkInOut(); fail = None
    try:
        if subs: tl.DeleteClips(subs, False)
        tl.SetTrackEnable("subtitle", 1, True)
        tl.SetCurrentTimecode(tl.GetStartTimecode())
        imp = mp.ImportMedia([path]); assert imp, "import SRT vuoto"
        mp.AppendToTimeline([imp[0]])
    except Exception as err:
        fail = str(err)
        if subs:
            tl.SetCurrentTimecode(tl.GetStartTimecode())
            rb = mp.ImportMedia([bak])
            if rb: mp.AppendToTimeline([rb[0]])
    new = [(x.GetStart(), x.GetEnd(), x.GetName()) for x in sorted(tl.GetItemListInTrack("subtitle", 1) or [], key=lambda x: x.GetStart())]
    gaps = [(new[k][1], new[k+1][0]) for k in range(len(new)-1) if new[k][1] != new[k+1][0]]
    cross = [(t, c) for a, e, t in new for c in cuts if a < c < e]
    v = inout.get("video", {})
    if "in" in v: tl.SetMarkInOut(v["in"], v["out"])
    return {"align": align, "fail": fail, "backup": bak, "match": new == data, "n": len(new), "gaps": gaps, "cross": cross,
            "end": tl.GetEndFrame(), "long": [x[2] for x in data if len(x[2]) > MAXC],
            "saved": resolve.GetProjectManager().SaveProject()}
result = main()
```

## Modello "Controllo voce" (`run_script_unsafe`, non modifica nulla)

```python
import array, math, wave
WAV = "/percorso/bsd-voce.wav"   # dal modello "Export voce"
SOGLIA = 4           # frame oltre i quali segnalare
tl = project.GetCurrentTimeline(); fps = float(tl.GetSetting("timelineFrameRate")); S = tl.GetStartFrame()
w = wave.open(WAV); sr = w.getframerate(); x = array.array("h", w.readframes(w.getnframes())); w.close()
h = sr // 100
db = [10 * math.log10(sum(v*v for v in x[i:i+h]) / h / 32768**2 + 1e-12) for i in range(0, len(x) - h, h)]
thr = sorted(db)[int(len(db) * .98)] - 28
act = [d > thr for d in db]
on = [i * .01 * fps + S for i in range(15, len(act)) if act[i] and not any(act[i-15:i])]   # attacchi dopo almeno 150 ms di pausa
starts = [s.GetStart() for s in (tl.GetItemListInTrack("subtitle", 1) or [])]
def voce(s):   # c'è voce nei primi 3 frame del sub? (una parola breve prima dell'attacco non è un errore)
    i = int((s - S) / fps * 100)
    return any(act[i:i + int(3 / fps * 100) + 1])
d, subito = [], 0
for o in on:
    c = [s for s in starts if abs(s - o) <= 15]
    if c:
        s = min(c, key=lambda v: abs(v - o))
        if s >= o or not voce(s): d.append((s, round(s - o, 1)))
        else: subito += 1
ass = [abs(v) for _, v in d] or [0]
result = {"attacchi": len(on), "voce_subito": subito, "misurati": len(d), "medio_assoluto": round(sum(ass) / len(ass), 2), "massimo": max(ass),
          "oltre_soglia": [(s, v) for s, v in d if abs(v) > SOGLIA]}
```

## Versioni
Aggiorna `metadata.version` nel blocco iniziale, il titolo e una riga qui a ogni modifica. Il dettaglio sta in `CHANGELOG.md` della repo.
- **1.0** — prima versione condivisibile: domande su progetto, timeline, `MAXC` e script se non indicati; trascrizione esterna obbligatoria senza script; glossari in file separati.
- **1.1** — indipendente dall'agente: i nomi degli strumenti sono esempi, niente `ToolSearch`.
- **1.1.5** — dopo la revisione: backup e ripristino della traccia, `EXT_WORDS` per la trascrizione esterna, controlli su `RANGE`, domande in un solo messaggio.
- **1.2.0** — `stable-ts` per testo e tempi; controllo voce che segnala gli scarti; blocchi `RANGES`; `SOSTITUISCI` e controllo della timeline dichiarata; glossario come prima azione e dichiarato nel riepilogo; ripiego Notion con conferma; export voce e venv standard.
