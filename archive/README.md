# Archive

Tools and data no longer part of the active daily workflow, kept for reference
and easy restoration. The app narrowed to **vocabulary + conjugation +
conjugation-in-context sentences** (see `enabled_blocks` in
`daily_trainer_config.yaml`), so these blocks were retired from the menu.

## Contents

Retired blocks:

- **`grammar.py`** — standalone grammar (fill-in-the-blank) trainer.
- **`grammar_data/`** — grammar exercise JSON (pronoms relatifs, négation, COI, etc.).
- **`sentence_data/`** — full-sentence translation bank (`translations.json`).

Superseded docs (kept for history; current usage lives in `README.md` and `CLAUDE.md`):

- **`IMPROVEMENTS.md`** — changelog for the old `flashcards_v2.py` enhanced trainer (that script no longer exists; its features are now in `flashcards.py`).
- **`MASTER_VOCABULARY.md`** — early guide to `master_vocabulary.csv` / `combine_csvs.py`; commands and counts are out of date.

## Notes

- The `grammar` and `sentence` exercise classes/loaders still exist in
  `exercise_types.py` (dormant — gated off by config). Nothing imports the
  archived `grammar.py`.
- To restore a block: move its data directory back to the project root and add
  the block name to `enabled_blocks`.
