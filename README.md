# asemu
Android Studio Emulator that works without Android Studio

# Example
### Run Emulator
**Quick start**
```bash
python3 asemu.py run --name phone
```
**Extra example (pass additional flags to the emulator)**
```bash
python3 asemu.py run --name phone --extra='-memory 4096'
```
**All options**
```
 Usage: asemu.py run [OPTIONS]

╭─ Options ────────────────────────────────────╮
│ --name          TEXT     AVD name [default: phone]                   │
│ --arch          TEXT     Architecture [default: x86_64]              │
│ --image         TEXT     System image [default: google_apis]         │
│ --sdk           INTEGER  Android SDK version [default: 36]           │
│ --device        TEXT     Android device [default: pixel]             │
│ --extra         TEXT     Additional flags for launch                 │
╰──────────────────────────────────────────╯
```

### Delete AVD
```bash
python3 asemu.py delete --name phone
```

### List AVDs
```bash
python3 asemu.py list
```
