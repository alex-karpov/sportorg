# Legacy's logs: what they hold and how to anonymize them — agent judgement

Agent judgement, **not reviewed by a human**: a sub-agent (Claude Code, Sonnet, effort medium) of
session S3, 2026-11-01, asked by the maintainer (answer 3 to the S3 questions). It read legacy's
code (`.legacy/pysport`, its git history, and `sportident` 1.2.8 in `.legacy-run`), never the
corpus. Its only corpus input was what `scripts/corpus/catalog.py` prints for the two logs of N07:
counts of readouts and punches, counts of log records by level and by code location
(`manifest.json`, `other_files`). Criteria: each claim about code carries a `[код]` tag (short form
`R` = pysport@fd98887, `B` = pysport@b548c35, `SI` = sportident 1.2.8 sportident.py, defined below);
anything else is `[допущение]`. Examples of values are invented.

Checked by the main session (same day): the formats of `sportident.py:974` (`==>> command …`) and
`:1047` (`<<== command …, data …`), the SI10/SIAC block list `0, 4, 5, 6, 7` (`sportident.py:1168`),
`main_window.py:549` and `live.py:80` at `fd98887`. Not checked: the byte offsets of owner data on
the cards (marked `[допущение]` by the sub-agent; they need SportIdent's card data document).

---


Tags: R = pysport@fd98887 (2025-06-19), the revision that best matches the log (see A). B = pysport@b548c35. SI = sportident 1.2.8 sportident.py (identical lock in R and v1.7.1: poetry.lock "sportident 1.2.8"; installed copy is 1.2.8, line numbers 526/713/974/1047/1073/1075 match the log).

## A. Which version wrote the log; location map

1. Tag v1.7.1 = 0952a37 (VERSION 'v1.7.1' [код: pysport@v1.7.1 sportorg/config.py:16]). The log's locations do NOT match it: result_tools.py does not exist there, main_window.py:549 is not a log call. VERSION stays "v1.7.1" in every commit up to e46dfa7 [код: pysport@fd98887 sportorg/config.py:7], so a "1.7.1" banner covers dev builds after the tag.
2. main_window.py:549 `logging.debug("Refresh in %s seconds"...)` exists only in 3 first-parent commits: ef983f3 (2025-05-26), fd98887 (2025-06-19), e46dfa7 (2025-06-28) [код: pysport@fd98887 sportorg/gui/main_window.py:549]. With the file name si20250622 the build is fd98887 (or ef983f3/e46dfa7; line numbers of the other files are identical in them for the checked locations). Locations live.py:80, result_tools.py:49, split_calculation.py:131, sireader.py:91, result_generation.py:135/214, results.py:58, file.py:64 and main_window.py:204/902/937 all hit log calls at R.
3. NOT reproduced at any commit of the repo: winorient.py:75..78, :98, :100 (the file has 91 lines at R, no line 100 in any revision) and orgeo.py:251, :375, :378 (at R :251 is a blank line; the HTTP log calls are at 248/250, 297, 305, 330...). Scan of all revisions found no match. Options: the log was appended (FileHandler mode 'a' [код: pysport@v1.7.1 sportorg/config.py:~140 'mode': 'a']) by several builds, or by a build not in this clone. So the winorient/orgeo rows below are by the module's statements, not by exact line [допущение].
4. Note: the file is opened in append mode, so lines of different versions can mix; the log also has one file for all days (no rotation) [код: pysport@v1.7.1 sportorg/config.py LOG_CONFIG 'file' handler]. A second file sportorg-errors.log (ERROR only) is written next to it.

### Location -> statement (R unless said)

| Location (count) | Statement | Personal data | Why |
|---|---|---|---|
| sportident.py:1047 (652) | `_logger.debug("<<== command '%s', len %i, station %s, data %s, crc %s, etx %s", hex(cmd), len, hex(station), "xx xx ..." data, hex(crc), hex(etx))` [код: sportident 1.2.8 sportident.py:1047-1054] | YES | raw data bytes of every received frame: card number, times, owner-data blocks of the card |
| sportident.py:974 (305) | `"==>> command '%s', parameters %s, crc %s"` [SI:974-979] | no/maybe | sent commands; parameters = block number or system-value address; no card data. Card number not in it |
| sportident.py:1031 | legacy-protocol `<<==` line (`station, data, etx`) [SI:1031] | - | not present in the log (extended protocol only) |
| main_window.py:549 (424) | `Refresh in %s seconds` | no | timing |
| live.py:80 (301) | `LiveClient.send started, data = %s` with `str(data)` [R live.py:80] | MAYBE (yes for Person/list) | `str(single Result)` = `Result.__str__` = system_type [R models/memory.py:524]; `str(Person)` falls to `__repr__` = "full_name bib group" [R memory.py:1342]; a list uses `repr` of items: ResultSportident repr = card number, start, finish, person full name, splits [R memory.py:985-998]. Senders: person_edit.py:295, main_window.py:688, actions.py:885 (list) |
| result_tools.py:49 (252) | `Results recalculation (%s)` timings | no | function names, ms |
| winorient.py:100 (232) | not mapped (file has no line 100) | maybe | import module; the statements that exist log import counts and, for duplicates, `full_name group club card_number` / `full_name year group club` [R winorient.py:67-86] |
| winorient.py:75..78 (4 each) | likely the 4-line duplicate-card / duplicate-name log blocks [R winorient.py:67-86] | YES if so | names, groups, clubs, card numbers, birth year |
| orgeo.py:251 (194) | likely `log.info(LOG_MSG...)` "HTTP Status: %s, Msg: %s" with server response text (made readable by make_nice) [R orgeo.py:8,248-250] | maybe | URL is not logged, but the response text is server-defined: it contains race title ("«...» - loaded") [R orgeo.py:192]; whether it names persons is [допущение] |
| orgeo.py:375,378 (1 each) | not mapped (R has `log.error("Error: %s", str(e))` at 373/395) | maybe | exception text of aiohttp may contain host/URL [допущение] |
| split_calculation.py:131 (178) | `"Group splits generate for " + self.group.name` | no | group name (e.g. class title) |
| sireader.py:91 (151) | `self._logger.error(str(e))` for SIReaderException [R sireader.py:89-91] | no | e.g. "CRC check failed", "No ETX byte", "Invalid start byte 0x..", "Unknown cardtype!" - useful operator/device errors. "Unknown card series: " + bytes could carry 4 card bytes [SI:~770 `_decode_cardnr`] |
| result_generation.py:214 (140) | `"{} {}".format(system_type, card_number)` [R result_generation.py:214-216] | YES (card number) | one line per accepted readout |
| result_generation.py:135 (64) | `"Relay: Card {} assigned to bib {}"` [R :135-139] | YES (card number+bib) | relay leg assignment; bib is a join key to person |
| result_generation.py:172 (2) | `"Result already exist"` | no | duplicate readout |
| file.py:64 (92) / :73 (17) | `"Save " + file_name` / `"Open " + file_name` [R modules/backup/file.py:64,73] | MAYBE | full path of the race file: user name in profile dir, event title in the file name |
| results.py:58 (37) | `Clicked on <row>` | no | |
| main_window.py:204 (23) | `Auto save` | no | |
| main_window.py:937 (17) | `lock start` [R :937] | no | |
| main_window.py:902 (1) | `logging.warning(str(e))` for NotEmptyException [R :902-903] | maybe | text of exception from rebuild_indexes (not read) |
| sportident.py:1073 (16) / :1075 (16) | `station code = %s` / `Operating mode - BSM7/8 Readout` [SI:1073,1075] | no | station code, mode (device facts) |
| sportident.py:713 (4) | `Device connected with speed = %s` [SI:713] | no | 38400 or 4800 |
| sportident.py:526 (4) | `logger param is deprecated` warning [SI:526] | no | harmless: sireader passes `logger=logging.root` [R sireader.py:52] |
| sireader.py:251 (4) / :257 (2) | `Opening port <name>` / `Closing port` [R :251,257] | no | port name e.g. COM3 |
| sireader.py:77 / :95 / :129 (2 each) | `Stop sireader` / error(str(e)) from SIReaderCardChanged ("SI-Card removed during command") / `Stop adder result` | no | card removed during readout = operator error signal |
| actions.py:595 (5) | `Manual finish` | no | |
| actions.py:769 (1) | `SPORTident result` | no | |
| live_dialog.py:212 (3) | `Saving settings of live` | no | |
| language.py:40 (1) | `Generate mo files` | no | |
| charsetgroupprober.py:95/98, mbcharsetprober.py:64, eucjpprober.py:66 | chardet 5.2.0 debug: "%s not active", "%s %s confidence = %s", "prober hit error at byte %s" [chardet 5.2.0 charsetgroupprober.py:95-98; mbcharsetprober.py:64; eucjpprober.py:66] | no | charset names, confidences, byte offsets only. chardet is used by libs/ocad/ocad.py and by aiohttp `resp.text()` (so likely one burst per online response) [допущение] |
| proactor_events.py:623 (8) | Python 3.8 asyncio on Windows (stdlib, no local copy to read) | no/maybe | transport warnings; tracebacks may contain host names [допущение] |

Other things in the log not tied to one location: 154 ERROR records and 1364 continuation lines (tracebacks): paths of the installation/user profile, the exception texts. A traceback of `log.exception(e)` in orgeo may print URL text of the online service [допущение]. Thread name field shows thread class (e.g. SIReaderThread, LiveThread).

## B. Raw byte exchange

Log line formats (SI:974, SI:1047). Hex is lowercase two digits via binascii.hexlify; data bytes space-separated, header fields not:
- Sent: `==>> command 'e1', parameters 08, crc xxxx` (no STX, LEN, ETX in text; they are derivable: STX 02 + cmd + LEN(=len(parameters)) + parameters + CRC + ETX 03 [SI:966-970]).
- Received extended: `<<== command 'ef', len N, station SSSS, data aa bb cc ..., crc xxxx, etx 03` (N is the LEN byte; data has N-2 bytes, station is 2 bytes) [SI:1040-1054]. No leading STX/FF/NAK; ACK (06) written by `ack_sicard` is not logged [SI:1186-1193]; the wake-up `FF 02` written in connect is not logged [SI:696,704,728]. NAK / invalid start byte / timeouts only appear as an ERROR text (sireader.py:91).
- Direction marks: `==>>` host to station, `<<==` station to host. Timestamp: asctime with milliseconds (stdlib default `%Y-%m-%d %H:%M:%S,mmm`) [допущение, stdlib], thread name; logged after the read completes (so it marks the end of the frame, the read has up to 5 s timeout [SI:990]).
- Frame (extended protocol): STX 02, CMD, LEN, STATION(2) + DATA, CRC(2), ETX 03. CRC = SI CRC16 poly 0x8005, init = first two bytes of the message, words processed MSB first, padded with zeros, computed over CMD+LEN+STATION+DATA [SI:68-119, CRC_POLYNOM SI:128]. A message of <=2 bytes: the first two bytes / 0000 [SI:92-93]. Legacy (basic) protocol: cmd < 0x80, no LEN/CRC, bytes 0x00-0x1F inside are DLE (10) escaped; logged with the DLE bytes kept [SI:1013-1036, SI:137].
- Commands with card data: `e8` (SI8/9/10/11/p/t inserted, data = 4 bytes, first byte unreliable), `e6` SI6 inserted, `e5` SI5 inserted, `e7` removed; requests `b1` (SI5 whole card), `e1` + param `08` (SI6 blocks), `ef` + block number (SI8+ blocks; reply data = block number + 128 bytes) [SI:155-171, SI:1129-1168, SI:1196-1240]. In a log with 1047 lines at 652 vs 974 at 305 the difference is the unsolicited e8/e7 events and multi-block replies (SI6: 3 or 8 replies to one request).
- What is read per type (this decides what the log contains) [SI:1129-1168]: SI5: `b1`, one reply; SI6: `e1` block 08 -> blocks 0,6,7 (or 8 blocks in 192-punch mode); SI8/SI9/pCard/tCard: `ef` blocks 0..BC-1 (BC=2); SI10/11/SIAC: `ef` blocks 0,4,5,6,7 as needed by punch count (blocks 1-3 are skipped). So SI10+ replies never include blocks 1-3.
- Where personal data lives: the code only says "3 blocks with personalisation info" for SI10 (blocks 1-3) [SI:944-946] and that punches of SI6 start at byte 128, SI9 at 56, SI8 at 136, SI10 at 128 of the read image [SI:CARD table]; card number is bytes 25-27 (SI8+), 11-13 (SI6), 4-6 (SI5) [SI:305-420]. The exact fields (first name, last name, club, birth date, e-mail, phone, sex, country, ...) and byte offsets are not in the code: [допущение] they are in the first block of SI6 (bytes 32..127 "personalization" before punches), in SI8/SI9 inside the bytes before the first punch (SI9: 32..55; SI8: 32..135), and in SI10/11/SIAC in block 0 after byte 32 plus blocks 1-3; to be confirmed from the SportIdent card data structure document (to be added to docs/sources). SI5 has no owner fields in the code's layout (header, 3-byte card number, times, punches only) [SI:CARD "SI5" P1=32] -> [допущение] no PD. Consequence: for SI10+ the owner fields in block 0 reach the log; blocks 1-3 do not. The maintainer's claim "name is in the log" is plausible for SI6/8/9/10/11/SIAC readouts via `ef`/`e1` replies; whether it is filled depends on the card (cards personalized by the owner/club) [допущение]. Not checked on the corpus (forbidden).
- Can it become an S5 dump? Present: direction, command, parameters, data, CRC, ETX, ms timestamp (end of frame), order of frames and of the unsolicited events, thread. Missing: STX/WAKEUP/ACK(06)/NAK bytes written or read outside `_send_command`/`_read_command` (ack, wake-up, flushInput discard, bytes dropped on "Invalid start byte"), idle gaps within a frame (inter-byte timing; only the end-of-frame stamp), serial port parameters (only the final baud: `Device connected with speed` 38400/4800 after the autodetect attempt; parity/stopbits are hard-coded 8N1 defaults of pyserial [допущение]), port name (`Opening port` in sireader.py:251), the failed 38400 attempt (only an error), DLE-stuffed legacy frames reconstructable but station field is logged separately. Frame text is complete enough to rebuild the exact bytes: STX+cmd+len+station+data+crc+ETX (extended). The reader is event driven: replay needs a virtual port peer that (1) answers each host frame (`==>>`) with the logged `<<==` frames following it, (2) emits unsolicited `e8`/`e7` frames by time order, (3) tolerates the host ACK and wake-up bytes (write-only). The legacy test harness already does this with socat ptys [код: pysport@b548c35 tests/test_reader.py:166-175, from docs/adr/0009]; not read by me.
- Caveat: a log carries only what the program saw; if the station was reconfigured by the operator (not through this module) the log shows only its answers.

## C. Anonymization design for the byte log

Required properties: each frame (or each readout = e8 plus the replies up to its removal) anonymized from the key and its own content; card number mapped by the same keyed permutation as for race files (ADR-0009 T7: Feistel with cycle walking on the card-type range, conjugated one cycle); parse and punches unchanged; CRC valid.

What must change in a frame:
1. Card number: in `e8`/`e6`/`e5` data (4 bytes: series byte + 3 bytes) and inside the card image at the CN offsets (SI5 4-6 [two bytes used], SI6 11-13, SI8+ 25-27) [SI table]. The series byte decides the type ranges [SI:755-778]; permute inside the type's range so `cardtype` detection (range based [SI:1215-1224]) still yields the same type and block count. Consistency check: the card number in the `e8` frame, in the card blocks and in the later SI-backup line must map to the same value.
2. Owner data bytes in the card image: personal block bytes (fields as in B, [допущение] offsets). Option: (a) overwrite the whole personalisation range with a keyed pseudo-random but valid-looking text (fixed pattern like ASCII from HMAC), (b) zero-fill/space-fill, (c) keep bytes whose layout parsing needs (none: `_decode_carddata` reads only card number, times, counters, punches [SI:889-958]) and replace the rest.
3. Blocks of SI10 never include blocks 1-3, so only block 0 bytes >= 32 (and SI6 block 0 range 32..127, SI8/9 up to P1) need replacement.
4. CRC: recompute over cmd+len+station+data with the SI algorithm (self-contained; verified round-trip with `_crc_check`), for both `==>>` (parameters change only for block numbers: unchanged) and `<<==`. Station code (2 bytes) = device id, not personal; may be kept or permuted; changing it requires consistency over the log.
5. Timestamps: absolute dates are personal-adjacent (date of event) but are kept for race files? not decided here; punch times inside cards must be unchanged for replay yielding same punches.
6. Free-text lines in the same log (live.py:80, winorient, result_generation 214/135, file paths, tracebacks) cannot be "anonymized by byte"; they must be dropped or reduced to location+level (see recommendation).

Options:
- C1 (recommended): extract only the SportIdent frames (`==>>`, `<<==`, `Device connected`, `station code`, `Operating mode`, `Opening port`, errors from sireader) into a separate dump file; drop every other log line; in each `<<==` frame decode, map card number, overwrite owner bytes, recompute CRC; keep lines in original order with milliseconds. Locality: a function `anonymize_frame(key, direction, bytes) -> bytes` and `anonymize_readout(key, frames)`, no state.
- C2: keep the whole log, redact text lines by regex. Rejected: no guarantee for free-text messages (names in repr, paths).
- C3: store only decoded readouts (card number, times, punches) as in si<date>.log; no replay. Lowest risk, but loses the device-behavior value for S5.
Open choice for the maintainer: how to treat a card whose personal bytes are empty (all 0x00/0xFF) - keep as is (recommended: if range is already empty, do nothing, so the test of "no PD" is identity).

Tests first (all synthetic, invented bytes):
1. `crc` oracle: algorithm port equals `sportident._crc` on random messages including odd length and 2-byte messages.
2. `parse(frame_text) -> bytes` and `format(bytes) -> text` round trip against the exact legacy format (a line copied from the SI source format string).
3. A synthetic SI9 / SI10 / SI6 / SI8 / SI5 readout built from `SIReader.CARD` offsets with an invented name in the owner area; after `anonymize_readout` run the legacy `_decode_carddata` on the original and the result: same punches/start/finish/check/clear, card number = permutation of the original, name bytes absent (search for the original string and for each 4-byte sequence).
4. CRC of every output frame valid (`_crc_check`); ETX/LEN unchanged; length of every frame unchanged.
5. Locality: result of a frame does not depend on other frames (permuting readout order and re-running gives the same frames).
6. Consistency: same card number in `e8`, in the card image and in the matching line of si<date>.log -> same mapped number; permutation stays inside the type range (ranges as in SI:755-778; an SI5 series < 2 shows no series).
7. Negative: unknown series byte (`Unknown card series`) frame is passed through without crash and reported.
8. Leak check on the produced dump: the card numbers of the input are absent (by number and by hex bytes).
9. Replay: feed the anonymized dump to the legacy reader through a pty pair (S5 harness) and compare punches with the original-dump result mapped by the permutation.

## D. si<date>.log (readout backup)

Format at R and B [код: pysport@b548c35 sportorg/modules/sportident/backup.py:29-44; same at R]: `BackupProcess` appends to `<log_dir>/si<YYYYMMDD of write day>.log` in mode 'a' [R backup.py:20-24]. One block per readout:
```
start
<card_number>
<HH:MM:SS start or "00:00:00"...>   (time_to_hhmmss of card start; empty only if key absent)
<HH:MM:SS finish>
split_start
<code> <HH:MM:SS>        one line per punch (control code, time of day)
split_end
end
```
Times have no date and no milliseconds (strftime %H:%M:%S) [R utils/time.py:82-84]; no timestamp of the readout, no card type, no station code, no check/clear times, no owner data (only the decoded dict `card_data`). Written from `ResultThread` after the result is emitted to the GUI [R sireader.py:120-123], i.e. one block per `read_sicard` that gave card number > 0 [R :81-85], including repeated readouts of the same card (the log has 148 readouts vs 146 persons: repeats or non-participants; the race `_has_result` rejects a second one [R result_generation.py:172, 188-195] so the backup keeps what the race file drops).
Relation to the race file: card_number = Result.card_number; start/finish = result.start_time/finish_time as read from the chip (not the person's assigned start time); punches = splits (code, time) before any editing; SI5 12-hour fix is applied in `_check_data` before the backup, so SI5 times can be altered [R sireader.py:131-148]. Adds over race file: the original unedited chip data and duplicates/repeated readouts, in order of readout (the order is the only time info). Does not add: time of readout, person.
Personal data: card numbers only (pseudonymize with the same permutation); no names.

## E. Other locations (see table)
- Online broadcast: live.py:80 logs str(data) (names possible, see table). orgeo.py logs only HTTP status and response text, card/code/finish of online control (`card=%s code=%s finish=%s` [R orgeo.py:297-302]), and "Ignoring empty card number". The online URL (may contain a race id/token) is not a logging argument, but is part of any aiohttp exception text and traceback [допущение]. `live_urls` lives in race settings, i.e. in the race file [R live.py:63-70], so check race-file anonymization for it as well (outside this task).
- winorient: duplicates listing = names, groups, clubs, card numbers, birth year [R winorient.py:62-86].
- file.py: full path of the race file.
- main_window.py:549, result_tools.py:49, split_calculation.py:131: performance numbers and group names.
- charset probers: noise; asyncio proactor: noise.

## Recommendation: what to extract, what to mask

| Log | Extract | Use | Mask / drop |
|---|---|---|---|
| sportident.py:1047/974/1031/713/1073-1091, sireader.py:251/257/91/95 | frames, errors, device facts | S5 device simulator dumps (replay via pty), ground truth for parser tests (CRC, DLE, multi-block replies), operator-error analysis (card removed during readout, CRC failures, wrong mode) | card number (keyed permutation as race files), owner bytes in blocks, recompute CRC; keep timing in ms; do not keep the raw file |
| si<date>.log | all of it | oracle check: readout list per day vs race file results (card numbers, finish, punches) | card number permutation; the rest has no PD |
| result_generation.py:214/135/172 | counts, "already exist" events, bib/card pairs | operator-error analysis (duplicates, relay assignment) | card number, bib |
| result_tools.py:49, main_window.py:549, split_calculation.py:131 | durations | performance baseline for the oracle/new code | group name if it identifies an event |
| live.py:80, orgeo.py HTTP lines, winorient.py | counts only | detect that online mode / import was used | drop message text entirely (names, response text, URLs) |
| file.py:64/73, tracebacks, 154 ERROR | location+level, exception class | error taxonomy | drop paths and messages |
| chardet, proactor, GUI lines | none | none | drop |
Proposed pipeline: parse the log with a strict allow-list of `file:line` (+ regexp on the message prefix), keep only allow-listed records, anonymize frames per C1, emit counts (not texts) for the rest; a leak check re-scans the output for input card numbers and any allow-list violation. Before any real log is processed, the maintainer should decide the unresolved rows (winorient.py:100, orgeo.py:251/375/378) by looking at message prefixes locally, since they cannot be mapped from the repository.
