<p align="center"><img width="120" src="./.github/logo.png"></p>
<h2 align="center">Fossil</h2>

<div align="center">

![Status](https://img.shields.io/badge/status-active-success?style=for-the-badge)
![Powered By: EDF](https://img.shields.io/badge/Powered_By-CERT_EDF-FFFF33.svg?style=for-the-badge)
[![License: MIT](https://img.shields.io/badge/License-MIT-2596be.svg?style=for-the-badge)](LICENSE)

</div>

<p align="center">A post-mortem analysis tool for raw disk/partition images</p>
<br>

# Introduction

Fossil is a linux command line collector based on pre-configured or customizable collection profiles.

It uses [sleuthkit](https://github.com/sleuthkit/sleuthkit) tools under the hood.

It can be used to perform various forensic tasks during the post-mortem examination of raw disk or partition images, such as computing image content digests or creating collections based on [generaptor](https://github.com/cert-edf/generaptor) collection targets.

<br>

> [!TIP]
> If your disk image is not a raw disk image, you can use tools such as `affuse` from [afflib-tools](https://github.com/sshock/AFFLIBv3) to create a mountpoint exposing a read-only raw disk image.


## Getting Started

Fossil releases are available on Github and Pypi. Using a Python virtual environment is recommended.

```bash
# Setup sleuthkit toolkit
sudo apt install sleuthkit
# Setup fossil
python3 -m pip install edf-fossil
# Setup generaptor configuration files w/o fetching velociraptor binaries
generaptor update --do-no-fetch
# List partitions
fossil windows disk.img partitions
# List file system entries (see options to include deleted files and directories)
fossil windows disk.img fs_entries
# List file system entries in a raw partition instead
fossil --image-is-partition windows part.img fs_entries
# Perform default data collection on disk.img raw disk image
fossil windows disk.img collect
# Perform custom collection based on a collection profile
echo '{"targets":["WebServer/IIS"]}' > iis_server.json
fossil windows disk.img collect --custom-profile iis_server.json
# Hash all existing files in the disk
fossil windows disk.img digest > result.csv
# Include deleted files (warning, sleuthkit is prone to errors when extracting deleted data)
fossil windows disk.img digest --deleted > result.csv
```

<br>

## Configuration

Fossil does not need any configuration file, it relies on Generaptor [configuration files](https://github.com/CERT-EDF/generaptor?tab=readme-ov-file#configuration) instead.

<br>

## License

Distributed under the [MIT License](LICENSE).

<br>

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

<br>

## Security

To report a (suspected) security issue, see [SECURITY.md](SECURITY.md).
