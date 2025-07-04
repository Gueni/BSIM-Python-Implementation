## Writing text files

Please limit all text files line len to max. 120 characters:

Fold USAGE:
```bash
fold -w 120 -s FILENAME
```

## Writing C code

TSaCt2 uses the Kernighan & Ritchie style (plus minor enhancements). 
Please, use GNU Indent to enforce coding style.

To enforce K&R coding style, use GNU/indent.

From GNU Indent manual:

The Kernighan & Ritchie style is used throughout their well-known book The C 
Programming Language. It is enabled with the ‘-kr’ option. The Kernighan & 
Ritchie style corresponds to the following set of options:

```
-nbad -bap -bbo -nbc -br -brs -c33 -cd33 -ncdb -ce -ci4 -cli0
-cp33 -cs -d0 -di1 -nfc1 -nfca -hnl -i4 -ip0 -l75 -lp -npcs
-nprs -npsl -saf -sai -saw -nsc -nsob -nss
```

Additionally, following options are used in TSaCt2 code:

```
-nut
```

## Notes
Prior to use indent on Linux, please convert windows end-lines (CR+LF)
to unix (LF):

```bash
  dos2unix FILENAME
```

Indent USAGE for TSaCt code:

```bash
  indent -kr -nut FILENAME
```

For details, see [https://www.gnu.org/software/indent/manual/indent.pdf](https://www.gnu.org/software/indent/manual/indent.pdf)
