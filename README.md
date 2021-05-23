# hanzi-writer-char-fixer

This repo fixes the following in the `hanzi-writer-data` `hanzi-writer-data-jp` data sets:

- Inverting the characters (characters are currently horizontally flipped)
- Subtracting 900px from the Y offset

This should allow users to render the characters without requiring unusual scaling transforms (i.e. `translateY(-900px) scale(1, -1)`)

## Running

```sh
pip install -r requirements.txt
yarn
yarn run fix-cn-chars
yarn run fix-jp-chars
```
