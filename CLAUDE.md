# Orchestra Tuner

Single-file web app (`index.html`, no build, no dependencies) for orchestral musicians, mainly the owner (adtromba, orchestral trumpet), on phone and iPad.
Live: https://adtromba.github.io/Orchestra-tuner/ (GitHub Pages from `main`). Give testers `?v=<tag>` (for example `?v=8o`) to bypass cache.

## What the owner wants (keep to this)
- **Super simple.** Advanced things collapsed. Nothing added just to add. Useful to orchestral players only.
- Replies are read on a phone: short, answer first, one link at the end.
- The owner tries each change on a real device and reacts. Ship small steps, say what changed in plain words, give the `?v=` link.
- Sound cues must be very clear (on/off, in/out of tune). Low register (trumpet low notes) must work, not just high.

## Tabs and features
- **Drone**: root note drone, tune A (415/440/442/443), waveforms, floating drone bar (start/stop, note, Tune A) shown on every tab except Rhythm.
- **Tuner** modes (`#modeSeg`): Notes, Target, **Scale** (record each degree, report with Hear it and pitch traces; needs 2 s played per note), **Climb**, My notes (chromatic tendencies per instrument), Beats (ear training).
  - **Climb**: plays root drone plus the current note (in the chosen Starting octave); you must stay within 5 cents of pure (just) pitch for a total of 3.5 s to move up. 4-beat count-in first. Green IN TUNE / gray OFF banner, rising two-note sound when you land in tune, falling two-note sound when you leave (0.15 s grace), three-note run when a note is done. Hold resets after 0.35 s out. Needs headphones (mic would hear the app).
  - Count-in (4 clicks, 60 bpm) is also in Scale and in Sing the scale.
- **Rhythm**: metronome and polyrhythm layers (each layer own sound), Count view (numbered cells, meeting lines, why/LCM math) and Circle view, silent bars, presets, **Sing the scale** (slow scale over a soft root, 4 s per note at 60 bpm).
- iPad/wide (>=700px): tuner controls left, Scale report / My notes right (sticky, scrolls alone). One column on phones.

## Code map (all inside one IIFE in `index.html`)
- State `s` (`note, octave, a4, vol, wave, tuning, scale, inst, tab, playing`), `SCALES`, `DEG`, `spell()`, `baseFreq()`, `justCents()`, `dd()` (signed cents difference), helpers `$`, `mark(id, v)`.
- Audio: drone context `ctx` (`audioReady`, `audioDone` suspends when idle, `toneOnce`, `climbTone`, `ping`, `countIn`), rhythm context `rctx` (`rEnsure`, `rVoice`, phase-based scheduler with lookahead), tuner mic context `tctx` (YIN pitch detection in `tLoop`, median of 5).
- Tuner guide: `guide`, `guideFeed`, `advance`, `finalizeRec`, `guideSilence` (Scale); `climb`, `climbFeed`, `climbSilence`, `zone()`, `zoneUI()` (Climb); `guided()` is true for both.
- Version line: `<p class="hint" id="buildTag">` ("Version: Nov 8o, ..."), copied to `#buildTag2` on Rhythm. Bump the letter every release.

## Known limits and gotchas
- iOS: audio session type is switched with `navigator.audioSession` (`audioMode()`); playback while mic is on needs `play-and-record`.
- `audioReady()` stops the drone if it was playing.
- Hear it and Sing the scale still raise the root to >= 200 Hz; only Climb follows the chosen octave.
- Nothing has been verified on a real device by Claude; all checks are headless Chrome with simulated pitch.
- GitHub Pages build status cannot be checked from the sandbox; the owner sometimes sees a cached older version (use `?v=`).

## Workflow
1. Edit `index.html`, bump the version line.
2. Test: `python3 tests/layout.py` (layout at iPad and phone sizes), `python3 tests/climb.py` (Climb logic). They use Playwright with `/usr/bin/google-chrome`, a temp copy with a `window.__t` hook, fake mic. Look at screenshots for visual changes (phone 390 and 320 wide, iPad 1180x820 and 820x1180).
3. Commit to `main` and push (Pages deploys). Commit message ends with the attribution trailers the session gives.
4. Reply briefly with what changed and `https://adtromba.github.io/Orchestra-tuner/?v=<tag>`.

## Ideas not built yet
- Make Hear it and Sing the scale follow the chosen octave (low register).
- Climb: remember results per note (how long each took), show them in a report like Scale.
- Intonation helpers for orchestra: tune an interval or chord against the drone (fifth, third), section tuning notes by instrument.
- Rhythm: save custom polyrhythm presets; count-in option for the metronome.
