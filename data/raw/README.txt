Put fingerprint images here:

  data/raw/<tribe>/<personID>/<personID>_<finger>_<sample>.png

Examples:
  data/raw/yoruba/P001/P001_RT_01.png
  data/raw/yoruba/P001/P001_RT_02.png
  data/raw/igbo/P010/P010_RT_01.png

Optional pattern label (for CNN training):
  data/raw/yoruba/P001/P001_RT_01.json
  contents: {"pattern": "loop"}

Allowed patterns: arch | loop | whorl
Finger codes: RT (right thumb), RI, LT, LI
Collect 5-10 scans per person.
