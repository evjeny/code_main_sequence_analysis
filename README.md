# code_main_sequence_analysis
how code variability and abstractivity influences number of changes per one commit?

## get data

```bash
gh search repos \
  --language=java \
  --sort=stars \
  --order=desc \
  --size 4096 \
  --limit=1000 \
  --json url > java_repos.json
```

## TODO

* [x] download github java repos (~200)
* [ ] calculate abs. and var. metrics:
  * [ ] abs = #abstract_classes / #all_classes
  * [x] var = #out_deps / #all_deps
* [x] get number of changes per commit
* [ ] plot abs.-var. -> #commits
